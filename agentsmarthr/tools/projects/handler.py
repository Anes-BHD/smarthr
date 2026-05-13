from typing import Any, Dict

from clients.php_api_client import SmartHRApiError
from clients.project_api_client import PROJECTS_ENDPOINT_MESSAGE, ProjectApiClient, normalize_priority

from .formatter import (
    format_count_projects,
    format_near_deadline,
    format_overdue_projects,
    format_project_choices,
    format_project_deadline,
    format_project_details,
    format_project_leader,
    format_project_list,
    format_project_priority,
    format_project_recommendation,
    format_project_team,
    format_projects_by_client,
    format_projects_by_person,
    format_projects_by_priority,
)


UNSUPPORTED_MESSAGE = "Cette action projet sera disponible dans une prochaine phase."
PROJECT_ACTIONS = {
    "list_projects",
    "project_details",
    "project_deadline",
    "project_leader",
    "project_team",
    "project_priority",
    "count_projects",
    "list_by_priority",
    "projects_by_client",
    "projects_by_leader",
    "projects_by_member",
    "projects_near_deadline",
    "overdue_projects",
    "project_recommendation",
    "unsupported_action",
}


def _client() -> ProjectApiClient:
    return ProjectApiClient()


def _arguments(plan: Dict[str, Any]) -> Dict[str, Any]:
    arguments = plan.get("arguments")
    if isinstance(arguments, dict):
        return arguments
    return {}


def _plan_value(plan: Dict[str, Any], key: str) -> Any:
    return _arguments(plan).get(key) or plan.get(key)


def _project_or_message(client: ProjectApiClient, project_name: str | None) -> tuple[Dict[str, Any] | None, str | None]:
    if not project_name:
        return None, "Quel projet voulez-vous consulter ?"

    result = client.find_project_by_name(project_name)
    status = result.get("status")
    if status == "found":
        return result.get("project"), None
    if status == "multiple":
        return None, format_project_choices(result.get("projects") or [])
    return None, f"Je n’ai pas trouvé le projet {project_name}."


def execute_project_tool(plan: Dict[str, Any]) -> str:
    action = plan.get("action") or plan.get("action_name") or plan.get("intent")
    if action not in PROJECT_ACTIONS:
        return UNSUPPORTED_MESSAGE
    if action == "unsupported_action":
        return UNSUPPORTED_MESSAGE

    client = _client()
    try:
        if action == "list_projects":
            return format_project_list(client.list_projects())

        if action == "count_projects":
            return format_count_projects(client.list_projects())

        if action == "list_by_priority":
            priority = _plan_value(plan, "priority")
            if not priority:
                return "Quelle priorité voulez-vous filtrer ? High, Normal ou Low ?"
            normalized_priority = normalize_priority(priority)
            return format_projects_by_priority(client.filter_by_priority(normalized_priority), normalized_priority)

        if action == "projects_by_client":
            client_name = _plan_value(plan, "client_name")
            if not client_name:
                return "Quel client voulez-vous consulter ?"
            return format_projects_by_client(client.filter_by_client(client_name), client_name)

        if action == "projects_by_leader":
            person_name = _plan_value(plan, "person_name")
            if not person_name:
                return "Quel chef de projet voulez-vous consulter ?"
            return format_projects_by_person(client.filter_by_leader(person_name), person_name, "leader")

        if action == "projects_by_member":
            person_name = _plan_value(plan, "person_name")
            if not person_name:
                return "Quel membre voulez-vous consulter ?"
            return format_projects_by_person(client.filter_by_member(person_name), person_name, "member")

        if action == "projects_near_deadline":
            return format_near_deadline(client.get_near_deadline_projects(days=30))

        if action == "overdue_projects":
            return format_overdue_projects(client.get_overdue_projects())

        if action == "project_recommendation":
            project_name = _plan_value(plan, "project_name")
            if project_name:
                project, message = _project_or_message(client, project_name)
                if message:
                    return message
                return format_project_recommendation(project)
            return format_project_recommendation(client.list_projects())

        project, message = _project_or_message(client, _plan_value(plan, "project_name"))
        if message:
            return message

        if action == "project_details":
            return format_project_details(project)
        if action == "project_deadline":
            return format_project_deadline(project)
        if action == "project_leader":
            return format_project_leader(project)
        if action == "project_team":
            return format_project_team(project)
        if action == "project_priority":
            return format_project_priority(project)
    except SmartHRApiError:
        return PROJECTS_ENDPOINT_MESSAGE

    return UNSUPPORTED_MESSAGE
