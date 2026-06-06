import json
from typing import Any, Dict
import unicodedata

import httpx

from config import OPENROUTER_API_KEY, OPENROUTER_MODEL
from graphs.admin.tools.absence.prompts import ABSENCE_PROMPT
from graphs.admin.tools.employees.prompts import EMPLOYEES_PROMPT
from graphs.admin.tools.ticket.prompts import TICKET_PLANNER_PROMPT
from tools.projects.prompt import PROJECTS_PLANNER_PROMPT


OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_ERROR_MESSAGE = "Erreur OpenRouter : impossible de comprendre la demande."
SMALL_GENERIC_PROMPT = """
Tu es SmartHR AI.
Tu aides pour :
- employés
- tickets
- absences
- projets

Réponds uniquement en JSON valide avec tool_name, action_name et arguments.
En cas de doute, choisis l'action la plus probable.
"""


def _error_plan() -> Dict[str, Any]:
    return {
        "handled": False,
        "tool_name": "",
        "action_name": "",
        "arguments": {},
        "confidence": 0,
        "reason": OPENROUTER_ERROR_MESSAGE,
        "error": OPENROUTER_ERROR_MESSAGE,
    }


def _normalize_text(value: str) -> str:
    text = (value or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.replace("-", " ").replace("_", " ").split())


def _normalize_tool(value: Any) -> str:
    tool = str(value or "").strip().lower()
    if tool in {"tickets", "ticket"}:
        return "ticket"
    if tool in {"project", "projects"}:
        return "projects"
    if tool in {"employee", "employees", "employe", "employes"}:
        return "employees"
    if tool in {"absence", "absences"}:
        return "absence"
    return tool


def _detect_tool(user_message: str, memory: Dict[str, Any] | None = None) -> str:
    text = _normalize_text(user_message)
    memory = memory or {}
    last_tool = _normalize_tool(memory.get("last_tool"))

    ticket_terms = {
        "ticket",
        "tickets",
        "tkt",
        "assigner",
        "assigne",
        "affecter",
    }
    project_terms = {
        "projet",
        "projets",
        "project",
        "projects",
        "deadline",
        "leader",
        "chef projet",
        "equipe projet",
        "priorite projet",
    }
    absence_terms = {
        "absence",
        "absences",
        "absent",
        "absents",
        "aujourd hui absent",
        "jours absent",
    }
    employee_terms = {
        "employe",
        "employes",
        "employee",
        "employees",
        "telephone",
        "phone",
        "email",
        "mail",
        "designation",
        "departement",
        "department",
        "adresse",
        "info",
        "infos",
        "statut",
        "status",
    }

    if any(term in text for term in ticket_terms):
        return "ticket"
    if any(term in text for term in project_terms):
        return "projects"
    if any(term in text for term in absence_terms):
        return "absence"

    if memory.get("last_ticket") and any(term in text for term in ("son statut", "son ticket", "ce ticket", "ticket actuel")):
        return "ticket"
    if memory.get("last_project") and any(term in text for term in ("sa deadline", "ce projet", "son projet", "projet actuel")):
        return "projects"
    if memory.get("last_employee") and any(term in text.split() for term in ("son", "sa", "ses", "lui")):
        return "employees"
    if any(term in text for term in employee_terms):
        return "employees"

    if last_tool in {"employees", "ticket", "absence", "projects"}:
        return last_tool
    return "generic"


def _extract_ticket_status(user_message: str) -> str | None:
    text = _normalize_text(user_message)
    phrase_statuses = {
        "in progress": "inprogress",
        "in_progress": "inprogress",
        "on hold": "onhold",
        "en cours": "inprogress",
        "en attente": "onhold",
    }
    for phrase, status in phrase_statuses.items():
        if phrase in text:
            return status

    status_aliases = {
        "new": "new",
        "nouveau": "new",
        "open": "open",
        "ouvert": "open",
        "reopen": "reopen",
        "reopened": "reopen",
        "reouvrir": "reopen",
        "onhold": "onhold",
        "closed": "closed",
        "close": "closed",
        "ferme": "closed",
        "fermer": "closed",
        "inprogress": "inprogress",
        "cancelled": "cancelled",
        "canceled": "cancelled",
        "annule": "cancelled",
        "completed": "completed",
        "complete": "completed",
        "resolved": "completed",
        "resolu": "completed",
    }
    for token in text.split():
        if token in status_aliases:
            return status_aliases[token]
    return None


def _prompt_for_tool(tool: str) -> str:
    if tool == "employees":
        return EMPLOYEES_PROMPT
    if tool == "ticket":
        return TICKET_PLANNER_PROMPT
    if tool == "absence":
        return ABSENCE_PROMPT
    if tool == "projects":
        return PROJECTS_PLANNER_PROMPT
    return SMALL_GENERIC_PROMPT


def _normalize_ticket_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    action = plan.get("action") or plan.get("action_name")
    arguments = plan.get("arguments") if isinstance(plan.get("arguments"), dict) else {}

    def value(key: str) -> Any:
        return arguments.get(key) or plan.get(key)

    ticket_ref = value("ticket_ref") or value("ticket_code")
    employee_name = value("employee_name")
    priority = value("priority")
    status = value("status")
    if isinstance(status, str):
        status = _extract_ticket_status(status) or status.lower()
    description = value("description")
    confidence = plan.get("confidence", 0.8)

    mapped_action = action
    mapped_arguments: Dict[str, Any] = {}

    if action == "list_tickets":
        mapped_action = "open_tickets_list"
    elif action == "show_ticket":
        mapped_action = "search_tickets"
        mapped_arguments["query"] = ticket_ref
        mapped_arguments["ticket_ref"] = ticket_ref
    elif action == "tickets_by_status":
        if status == "open":
            mapped_action = "open_tickets_list"
        else:
            mapped_action = "tickets_count_by_status"
            mapped_arguments["status"] = status
    elif action == "tickets_by_priority":
        mapped_action = "tickets_list_by_priority"
        mapped_arguments["priority"] = priority
    elif action == "tickets_by_employee":
        mapped_action = "tickets_by_employee_list"
        mapped_arguments["employee_name"] = employee_name
    elif action == "count_tickets":
        if status == "open":
            mapped_action = "tickets_count_open"
            mapped_arguments["status"] = status
        elif status:
            mapped_action = "tickets_count_by_status"
            mapped_arguments["status"] = status
        elif priority:
            mapped_action = "tickets_count_by_priority"
            mapped_arguments["priority"] = priority
        else:
            mapped_action = "tickets_by_status_stats"
    elif action == "count_tickets_by_status":
        mapped_action = "tickets_count_by_status"
        mapped_arguments["status"] = status
    elif action == "count_tickets_by_priority":
        mapped_action = "tickets_count_by_priority"
        mapped_arguments["priority"] = priority
    elif action == "update_ticket_status":
        mapped_action = "update_ticket_status"
        mapped_arguments["ticket_code"] = ticket_ref
        mapped_arguments["status"] = status
    elif action == "assign_ticket":
        mapped_action = "assign_ticket"
        mapped_arguments["ticket_code"] = ticket_ref
        mapped_arguments["employee_name"] = employee_name
    elif action == "create_ticket":
        mapped_action = "create_ticket"
        mapped_arguments["employee_name"] = employee_name
        mapped_arguments["subject"] = description
        mapped_arguments["description"] = description
        mapped_arguments["priority"] = priority
        mapped_arguments["status"] = status
    elif action == "search_tickets":
        mapped_action = "search_tickets"
        mapped_arguments["query"] = description or ticket_ref
    elif action == "unsupported_action":
        mapped_action = "unsupported_action"

    return {
        "handled": True,
        "tool_name": "ticket",
        "action_name": mapped_action,
        "arguments": {key: value for key, value in mapped_arguments.items() if value not in (None, "", [])},
        "confidence": confidence,
        "reason": "compact ticket planner",
    }


def _memory_context(memory: Dict[str, Any] | None) -> str:
    memory = memory or {}
    return (
        "Mémoire compacte :\n"
        f"employee={memory.get('last_employee') or 'null'}\n"
        f"ticket={memory.get('last_ticket') or 'null'}\n"
        f"project={memory.get('last_project') or 'null'}\n"
        f"tool={memory.get('last_tool') or 'null'}"
    )


def _extract_json_object(raw_content: str) -> Dict[str, Any] | None:
    content = (raw_content or "").strip()
    if content.startswith("```"):
        lines = content.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        content = "\n".join(lines).strip()

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        try:
            parsed = json.loads(content[start : end + 1])
        except json.JSONDecodeError:
            return None

    return parsed if isinstance(parsed, dict) else None


def _is_max_tokens_budget_error(response: httpx.Response | None) -> bool:
    if response is None or response.status_code != 402:
        return False
    body = (response.text or "").lower()
    return "max_tokens" in body or "fewer max_tokens" in body or "can only afford" in body


def _call_openrouter(payload: Dict[str, Any]) -> Dict[str, Any] | None:
    try:
        response = httpx.post(
            OPENROUTER_ENDPOINT,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"[OPENROUTER ERROR] {e}")
        print(f"[OPENROUTER STATUS] {e.response.status_code}")
        print(f"[OPENROUTER BODY] {e.response.text}")
        if _is_max_tokens_budget_error(e.response) and payload.get("max_tokens") != 100:
            print("[OPENROUTER RETRY] max_tokens=100")
            retry_payload = dict(payload)
            retry_payload["max_tokens"] = 100
            return _call_openrouter(retry_payload)
        return None
    except httpx.HTTPError as e:
        print(f"[OPENROUTER ERROR] {e}")
        response = getattr(e, "response", None)
        if response is not None:
            print(f"[OPENROUTER STATUS] {response.status_code}")
            print(f"[OPENROUTER BODY] {response.text}")
        return None
    except ValueError as e:
        print(f"[OPENROUTER JSON ERROR] {e}")
        return None


def plan_employee_request(user_message: str, memory: Dict[str, Any] | None = None) -> Dict[str, Any]:
    tool = _detect_tool(user_message, memory)
    system_prompt = _prompt_for_tool(tool)
    print("[MICRO_PLANNER TOOL]", tool)
    print("[PROMPT SIZE]", len(system_prompt))
    if tool == "ticket":
        print("[TICKET PROMPT COMPACT]", len(system_prompt))
    if tool == "projects":
        print("[PROJECTS PROMPT COMPACT]", len(system_prompt))

    payload = {
        "model": OPENROUTER_MODEL,
        "temperature": 0,
        "max_tokens": 120,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": _memory_context(memory)},
            {"role": "user", "content": user_message},
        ],
    }

    data = _call_openrouter(payload)
    if data is None:
        return _error_plan()

    content = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
    print("[OPENROUTER RAW]", content)
    parsed = _extract_json_object(content)
    if parsed is None:
        print("[OPENROUTER JSON PARSE ERROR]", content)
        return _error_plan()

    return _normalize_ticket_plan(parsed) if tool == "ticket" else parsed
