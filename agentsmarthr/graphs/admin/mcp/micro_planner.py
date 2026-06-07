import json
import re
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
    ticket_status_values = {
        "completed",
        "inprogress",
        "onhold",
        "reopen",
        "reopened",
        "cancelled",
        "canceled",
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

    if memory.get("last_ticket") and any(term in text for term in ("son statut", "son ticket", "ce ticket", "ticket actuel", "statut", "status")):
        return "ticket"
    if memory.get("last_ticket") and any(term in text.split() for term in ticket_status_values):
        return "ticket"
    if any(term in text.split() for term in ticket_status_values):
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
    action = plan.get("action") or plan.get("action_name") or plan.get("a")
    action_aliases = {
        "show": "show_ticket",
        "search": "search_tickets",
        "priority": "tickets_by_priority",
        "status": "tickets_by_status",
        "count": "count_tickets",
        "create": "create_ticket",
        "update": "update_ticket_status",
        "assign": "assign_ticket",
        "unsupported": "unsupported_action",
    }
    action = action_aliases.get(action, action)
    arguments = plan.get("arguments") if isinstance(plan.get("arguments"), dict) else {}

    short_keys = {
        "ticket_ref": "r",
        "employee_name": "e",
        "priority": "p",
        "status": "s",
        "description": "d",
    }

    def value(key: str) -> Any:
        return arguments.get(key) or plan.get(key) or plan.get(short_keys.get(key, ""))

    ticket_ref = value("ticket_ref") or value("ticket_code")
    employee_name = value("employee_name")
    priority = value("priority")
    status = value("status")
    if isinstance(status, str):
        status = _extract_ticket_status(status) or status.lower()
    description = value("description")
    confidence = plan.get("confidence") or plan.get("c") or 0.8

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
        "arguments": {key: value for key, value in mapped_arguments.items() if value not in (None, "", [], "null")},
        "confidence": confidence,
        "reason": "compact ticket planner",
    }


def _memory_context(memory: Dict[str, Any] | None, tool: str) -> str:
    memory = memory or {}
    if tool == "ticket":
        last = memory.get("last_ticket")
        return f"ticket={last}" if last else ""
    if tool == "projects":
        last = memory.get("last_project")
        return f"project={last}" if last else ""
    if tool == "employees":
        last = memory.get("last_employee")
        return f"employee={last}" if last else ""
    last_tool = memory.get("last_tool")
    return f"tool={last_tool}" if last_tool else ""


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


def _lock_plan_tool(plan: Dict[str, Any], selected_tool: str) -> Dict[str, Any]:
    if selected_tool not in {"employees", "ticket", "absence", "projects"}:
        return plan
    plan["tool"] = selected_tool
    plan["tool_name"] = selected_tool
    return plan


def _affordable_max_tokens(response: httpx.Response | None) -> int | None:
    if response is None or response.status_code != 402:
        return None
    body = (response.text or "").lower()
    if not ("max_tokens" in body or "fewer max_tokens" in body or "can only afford" in body):
        return None
    match = re.search(r"can only afford\s+(\d+)", body)
    return int(match.group(1)) if match else 100


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
        affordable_tokens = _affordable_max_tokens(e.response)
        current_tokens = int(payload.get("max_tokens") or 0)
        if affordable_tokens and affordable_tokens < current_tokens:
            print(f"[OPENROUTER RETRY] max_tokens={affordable_tokens}")
            retry_payload = dict(payload)
            retry_payload["max_tokens"] = affordable_tokens
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
        "reasoning": {"enabled": False},
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"{_memory_context(memory, tool)}\nDemande: {user_message}",
            },
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

    parsed = _lock_plan_tool(parsed, tool)
    return _normalize_ticket_plan(parsed) if tool == "ticket" else parsed
