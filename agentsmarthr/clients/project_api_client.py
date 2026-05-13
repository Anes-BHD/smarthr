from datetime import date, datetime, timedelta
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional
import unicodedata

from clients import php_api_client


PROJECTS_ENDPOINT_MESSAGE = "Impossible de récupérer les projets depuis Laravel. Vérifiez l’endpoint /api/v1/projects."


def normalize_text(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.replace("-", " ").replace("_", " ").split())


def normalize_priority(value: Any) -> str:
    text = normalize_text(value)
    if text in {"urgent", "urgents", "critical", "critique", "high", "haute"}:
        return "high"
    if text in {"normal", "medium", "moyenne"}:
        return "normal"
    if text in {"low", "basse"}:
        return "low"
    return text


def parse_project_date(value: Any) -> Optional[date]:
    if not value:
        return None
    text = str(value).strip()
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(text[:10], fmt).date()
        except ValueError:
            continue
    return None


def _matches_text(value: Any, query: Any) -> bool:
    candidate = normalize_text(value)
    searched = normalize_text(query)
    if not candidate or not searched:
        return False
    if candidate == searched:
        return True
    if searched in candidate or candidate in searched:
        return True
    return SequenceMatcher(None, searched, candidate).ratio() >= 0.72


class ProjectApiClient:
    def _extract_projects(self, payload: Any) -> List[Dict[str, Any]]:
        if isinstance(payload, list):
            return [project for project in payload if isinstance(project, dict)]

        if not isinstance(payload, dict):
            return []

        for key in ("data", "projects", "items", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                return [project for project in value if isinstance(project, dict)]

        data = payload.get("data")
        if isinstance(data, dict):
            for key in ("data", "projects", "items", "results"):
                value = data.get(key)
                if isinstance(value, list):
                    return [project for project in value if isinstance(project, dict)]

        return []

    def list_projects(self) -> List[Dict[str, Any]]:
        try:
            payload = php_api_client.get("/api/v1/projects")
        except php_api_client.SmartHRApiError as error:
            raise php_api_client.SmartHRApiError(
                PROJECTS_ENDPOINT_MESSAGE,
                status_code=error.status_code,
                details=error.details,
            ) from error
        return [self.normalize_project(project) for project in self._extract_projects(payload)]

    def get_all_projects(self) -> List[Dict[str, Any]]:
        return self.list_projects()

    def normalize_project(self, project: Dict[str, Any]) -> Dict[str, Any]:
        normalized = dict(project)
        normalized["id"] = self._first(project, ("id", "project_id"))
        normalized["name"] = self._first(project, ("name", "project_name", "title"))
        normalized["client"] = self._client_name(project)
        normalized["start_date"] = self._first(project, ("start_date", "startDate", "start"))
        normalized["end_date"] = self._first(project, ("end_date", "endDate", "deadline", "due_date"))
        normalized["deadline"] = normalized["end_date"]
        normalized["priority"] = self._first(project, ("priority", "project_priority"))
        normalized["rate"] = self._first(project, ("rate",))
        normalized["rate_type"] = self._first(project, ("rate_type", "rateType"))
        normalized["project_leader"] = self._leader_name(project)
        normalized["team"] = self._team_names(project)
        normalized["description"] = self._first(project, ("description", "brief_description", "summary", "short_desc"))
        normalized["opened_tasks"] = self._first(project, ("opened_tasks", "open_tasks", "tasks_open_count"))
        normalized["completed_tasks"] = self._first(project, ("completed_tasks", "done_tasks", "tasks_completed_count"))
        return normalized

    def _first(self, project: Dict[str, Any], keys: tuple[str, ...]) -> Optional[Any]:
        for key in keys:
            value = self._nested(project, key)
            if value not in (None, ""):
                return value
        return None

    def _nested(self, data: Dict[str, Any], path: str) -> Optional[Any]:
        current: Any = data
        for part in path.split("."):
            if not isinstance(current, dict):
                return None
            current = current.get(part)
        return current

    def _person_name(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        if not isinstance(value, dict):
            return ""
        full_name = value.get("full_name") or value.get("name")
        if full_name:
            return str(full_name)
        firstname = value.get("firstname") or value.get("first_name") or ""
        middlename = value.get("middlename") or value.get("middle_name") or ""
        lastname = value.get("lastname") or value.get("last_name") or ""
        return f"{firstname} {middlename} {lastname}".strip()

    def _client_name(self, project: Dict[str, Any]) -> Optional[str]:
        direct = self._first(project, ("client_name", "customer_name", "client.name", "customer.name"))
        if direct:
            return str(direct)
        for key in ("client", "customer"):
            name = self._person_name(project.get(key))
            if name:
                return name
        return None

    def _leader_name(self, project: Dict[str, Any]) -> Optional[str]:
        direct = self._first(
            project,
            ("leader_name", "manager_name", "project_leader.name", "leader.name", "manager.name"),
        )
        if direct:
            return str(direct)
        for key in ("project_leader", "leader", "manager"):
            name = self._person_name(project.get(key))
            if name:
                return name
        return None

    def _team_names(self, project: Dict[str, Any]) -> List[str]:
        value = (
            project.get("team")
            or project.get("members")
            or project.get("employees")
            or project.get("project_members")
            or []
        )
        if not isinstance(value, list):
            return []
        names = []
        for member in value:
            if isinstance(member, dict):
                user = member.get("user") if isinstance(member.get("user"), dict) else member
                name = self._person_name(user)
            else:
                name = str(member)
            if name:
                names.append(name)
        return names

    def find_project_by_name(self, name: str) -> Dict[str, Any]:
        searched = normalize_text(name)
        if not searched:
            return {"status": "missing_name", "project": None}

        projects = self.get_all_projects()
        exact = [project for project in projects if normalize_text(project.get("name")) == searched]
        if len(exact) == 1:
            return {"status": "found", "project": exact[0]}
        if len(exact) > 1:
            return {"status": "multiple", "projects": exact}

        starts = [project for project in projects if normalize_text(project.get("name")).startswith(searched)]
        candidates = starts or [project for project in projects if searched in normalize_text(project.get("name"))]

        if not candidates:
            candidates = [
                project
                for project in projects
                if SequenceMatcher(None, searched, normalize_text(project.get("name"))).ratio() >= 0.72
            ]

        if len(candidates) == 1:
            return {"status": "found", "project": candidates[0]}
        if len(candidates) > 1:
            return {"status": "multiple", "projects": candidates}
        return {"status": "not_found", "project": None}

    def filter_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        searched = normalize_priority(priority)
        return [
            project
            for project in self.get_all_projects()
            if normalize_priority(project.get("priority")) == searched
        ]

    def filter_by_client(self, client_name: str) -> List[Dict[str, Any]]:
        return [
            project
            for project in self.get_all_projects()
            if _matches_text(project.get("client"), client_name)
        ]

    def filter_by_leader(self, person_name: str) -> List[Dict[str, Any]]:
        return [
            project
            for project in self.get_all_projects()
            if _matches_text(project.get("project_leader"), person_name)
        ]

    def filter_by_member(self, person_name: str) -> List[Dict[str, Any]]:
        return [
            project
            for project in self.get_all_projects()
            if any(_matches_text(member, person_name) for member in project.get("team", []))
        ]

    def get_near_deadline_projects(self, days: int = 30) -> List[Dict[str, Any]]:
        today = date.today()
        limit = today + timedelta(days=days)
        projects = []
        for project in self.get_all_projects():
            deadline = parse_project_date(project.get("deadline") or project.get("end_date"))
            if deadline and today <= deadline <= limit:
                projects.append(project)
        return sorted(projects, key=lambda project: parse_project_date(project.get("deadline")) or date.max)

    def get_overdue_projects(self) -> List[Dict[str, Any]]:
        today = date.today()
        projects = []
        for project in self.get_all_projects():
            deadline = parse_project_date(project.get("deadline") or project.get("end_date"))
            if deadline and deadline < today:
                projects.append(project)
        return sorted(projects, key=lambda project: parse_project_date(project.get("deadline")) or date.max)

    def get_project_field(self, name: str, field: str) -> Dict[str, Any]:
        result = self.find_project_by_name(name)
        if result.get("status") != "found":
            return result
        project = result["project"]
        return {"status": "found", "project": project, "value": project.get(field)}
