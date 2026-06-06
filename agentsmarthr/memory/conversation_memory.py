from copy import deepcopy
from typing import Any, Dict
import unicodedata


conversation_memory: Dict[str, Dict[str, Any]] = {}


EMPTY_MEMORY = {
    "last_employee": None,
    "last_project": None,
    "last_ticket": None,
    "last_tool": None,
    "last_action": None,
}


def _normalize_text(value: str) -> str:
    text = (value or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.replace("-", " ").replace("_", " ").split())


def get_memory(session_id: str) -> Dict[str, Any]:
    if session_id not in conversation_memory:
        conversation_memory[session_id] = deepcopy(EMPTY_MEMORY)
    return deepcopy(conversation_memory[session_id])


def update_memory(session_id: str, **kwargs: Any) -> None:
    memory = get_memory(session_id)
    for key, value in kwargs.items():
        if key in EMPTY_MEMORY and value not in (None, "", []):
            memory[key] = value
    conversation_memory[session_id] = memory


def clear_memory(session_id: str) -> None:
    conversation_memory.pop(session_id, None)


def resolve_reference(session_id: str, text: str) -> Dict[str, Any]:
    memory = get_memory(session_id)
    normalized = _normalize_text(text)
    resolved: Dict[str, Any] = {}

    employee_refs = {
        "son",
        "sa",
        "ses",
        "lui",
        "cet employe",
        "cette personne",
    }
    if memory.get("last_employee") and any(ref in normalized for ref in employee_refs):
        resolved["employee_name"] = memory["last_employee"]

    project_refs = {
        "ce projet",
        "son projet",
        "sa deadline",
        "projet actuel",
    }
    if memory.get("last_project") and any(ref in normalized for ref in project_refs):
        resolved["project_name"] = memory["last_project"]

    ticket_refs = {
        "ce ticket",
        "son ticket",
        "ticket actuel",
        "son statut",
        "son status",
    }
    if memory.get("last_ticket") and any(ref in normalized for ref in ticket_refs):
        resolved["ticket_ref"] = memory["last_ticket"]

    return resolved
