import sys
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

AGENT_ROOT = Path(__file__).resolve().parent
if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))

from clients.php_api_client import request_token
from graphs.admin.mcp.micro_planner import OPENROUTER_ERROR_MESSAGE, plan_employee_request
from graphs.admin.tools.absence.executor import ABSENCE_ACTIONS, execute_absence_tool
from graphs.admin.tools.employees.executor import execute_employee_tool
from graphs.admin.tools.ticket.executor import TICKET_ACTIONS, execute_ticket_tool
from llm.conversation_gate import classify_message
from llm.response_humanizer import humanize_response
from memory.conversation_memory import clear_memory as clear_conversation_memory
from memory.conversation_memory import get_memory, resolve_reference, update_memory
from memory.pending_state import clear_pending_state, get_pending_state
from security.admin_guard import verify_admin_guard
from tools.projects.handler import PROJECT_ACTIONS, execute_project_tool


app = FastAPI()
@app.get("/")
def root():
    return {"status": "ok"}
@app.get("/up")
def root():
    return {"status": "ok"}
@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/login")
def health_compat():
    return {"status": "ok"}

EMPLOYEE_ACTIONS = {
    "get_employee_info",
    "get_employee_full_info",
    "create_employee",
    "update_employee",
    "delete_employee",
    "employee_analytics",
}
ABSENCE_ACTIONS = set(ABSENCE_ACTIONS)
TICKET_ACTIONS = set(TICKET_ACTIONS)
PROJECT_ACTIONS = set(PROJECT_ACTIONS)
ALL_ACTIONS = EMPLOYEE_ACTIONS | ABSENCE_ACTIONS | TICKET_ACTIONS | PROJECT_ACTIONS
TICKET_ACTION_ALIASES = {
    "change_status": "update_ticket_status",
    "change_ticket_status": "update_ticket_status",
    "ticket_change_status": "update_ticket_status",
    "update_status": "update_ticket_status",
    "status_update": "update_ticket_status",
    "modify_ticket_status": "update_ticket_status",
    "set_ticket_status": "update_ticket_status",
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://localhost",
        "https://smarthr.anesbhd.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    session_id: str
    message: str


def _normalized_message(message: str) -> str:
    return (message or "").strip().lower()


def _cancel_message(action_name: str) -> str:
    if action_name == "update_employee":
        return "Modification annulée."
    if action_name == "delete_employee":
        return "Suppression annulée."
    if action_name == "create_ticket":
        return "Création du ticket annulée."
    if action_name == "update_ticket_status":
        return "Modification du statut annulée."
    if action_name == "assign_ticket":
        return "Assignation du ticket annulée."
    return "Création annulée."


def _normalize_plan(plan: dict) -> dict:
    tool = plan.get("tool")
    if tool and not plan.get("tool_name"):
        plan["tool_name"] = tool
    action = plan.get("action")
    if action and not plan.get("action_name"):
        plan["action_name"] = action
    intent = plan.get("intent")
    if intent and not plan.get("action_name"):
        plan["action_name"] = intent
        
    tool_name = str(plan.get("tool_name") or "").lower()
    if tool_name in ("project", "projects"):
        plan["tool_name"] = "projects"
    if plan.get("action_name") in TICKET_ACTION_ALIASES:
        plan["action_name"] = TICKET_ACTION_ALIASES[plan["action_name"]]
        if not plan.get("tool_name"):
            plan["tool_name"] = "ticket"
    if plan.get("tool_name") in {"tickets", "ticket"}:
        plan["tool_name"] = "ticket"

    arguments = plan.get("arguments")
    if isinstance(arguments, dict):
        for key in (
            "employee_name",
            "project_name",
            "ticket_code",
            "ticket_ref",
            "status",
            "field",
            "priority",
            "client_name",
            "person_name",
        ):
            if plan.get(key) not in (None, "", []) and not arguments.get(key):
                arguments[key] = plan[key]
        if plan.get("tool_name") == "ticket":
            ticket_ref = arguments.get("ticket_ref") or arguments.get("ticket")
            if ticket_ref and not arguments.get("ticket_code"):
                arguments["ticket_code"] = ticket_ref

    if plan.get("action_name") in EMPLOYEE_ACTIONS and not plan.get("tool_name"):
        plan["tool_name"] = "employees"
    if plan.get("action_name") in ABSENCE_ACTIONS and not plan.get("tool_name"):
        plan["tool_name"] = "absence"
    if plan.get("action_name") in TICKET_ACTIONS and not plan.get("tool_name"):
        plan["tool_name"] = "ticket"
    if plan.get("action_name") in PROJECT_ACTIONS and not plan.get("tool_name"):
        plan["tool_name"] = "projects"
    return plan


def _plan_arguments(plan: dict) -> dict:
    arguments = plan.get("arguments")
    if not isinstance(arguments, dict):
        arguments = {}
        plan["arguments"] = arguments
    for key in (
        "employee_name",
        "project_name",
        "ticket_code",
        "ticket_ref",
        "status",
        "field",
        "priority",
        "client_name",
        "person_name",
    ):
        if plan.get(key) not in (None, "", []) and not arguments.get(key):
            arguments[key] = plan[key]
    return arguments


def _set_plan_value(plan: dict, key: str, value: str) -> None:
    if value in (None, "", []):
        return
    arguments = _plan_arguments(plan)
    if not arguments.get(key) and not plan.get(key):
        arguments[key] = value
        plan[key] = value


def _apply_memory_references(session_id: str, message: str, plan: dict) -> dict:
    resolved = resolve_reference(session_id, message)
    tool_name = plan.get("tool_name")
    arguments = _plan_arguments(plan)

    if tool_name == "employees" and resolved.get("employee_name") and not arguments.get("employee_name"):
        _set_plan_value(plan, "employee_name", resolved["employee_name"])
    if tool_name == "projects" and resolved.get("project_name") and not (arguments.get("project_name") or plan.get("project_name")):
        _set_plan_value(plan, "project_name", resolved["project_name"])
    if tool_name == "ticket" and resolved.get("ticket_ref"):
        if not (arguments.get("ticket_code") or arguments.get("ticket_ref") or plan.get("ticket_code")):
            _set_plan_value(plan, "ticket_code", resolved["ticket_ref"])
    if tool_name == "ticket" and arguments.get("ticket_ref") and not arguments.get("ticket_code"):
        _set_plan_value(plan, "ticket_code", arguments["ticket_ref"])

    return plan


def _plan_request(session_id: str, message: str) -> dict:
    memory = get_memory(session_id)
    plan = _normalize_plan(plan_employee_request(message, memory=memory))
    return _apply_memory_references(session_id, message, plan)


def _memory_reset_requested(message: str) -> bool:
    text = _normalized_message(message)
    return any(
        phrase in text
        for phrase in (
            "reset mémoire",
            "reset memoire",
            "oublie le contexte",
            "recommencer conversation",
        )
    )


def _selected_employee_name(employee: dict) -> str | None:
    if not isinstance(employee, dict):
        return None
    full_name = employee.get("full_name") or employee.get("name")
    if full_name:
        return str(full_name)
    firstname = employee.get("firstname") or ""
    lastname = employee.get("lastname") or ""
    name = f"{firstname} {lastname}".strip()
    return name or employee.get("email")


def _response_successful(message: str) -> bool:
    text = _normalized_message(message)
    failure_markers = [
        "quel ",
        "quelle ",
        "je n’ai pas trouvé",
        "je n'ai pas trouvé",
        "introuvable",
        "impossible",
        "répondez",
        "repondez",
        "n’est pas encore",
        "n'est pas encore",
        "annul",
        "erreur",
    ]
    return bool(text) and not any(marker in text for marker in failure_markers)


def _update_conversation_memory(session_id: str, plan: dict, final_message: str) -> None:
    if not _response_successful(final_message):
        return

    arguments = plan.get("arguments") if isinstance(plan.get("arguments"), dict) else {}
    tool_name = plan.get("tool_name")
    action_name = plan.get("action_name") or plan.get("action") or plan.get("intent")

    memory_tool = "tickets" if tool_name == "ticket" else tool_name
    updates = {
        "last_tool": memory_tool,
        "last_action": action_name,
    }

    if tool_name == "employees":
        selected_employee = _selected_employee_name(plan.get("_selected_employee"))
        employee_name = selected_employee or arguments.get("employee_name") or plan.get("employee_name")
        if employee_name:
            updates["last_employee"] = employee_name

    if tool_name == "projects":
        project_name = arguments.get("project_name") or plan.get("project_name")
        if project_name:
            updates["last_project"] = project_name

    if tool_name == "ticket":
        ticket_ref = (
            arguments.get("ticket_code")
            or arguments.get("ticket_ref")
            or arguments.get("code")
            or plan.get("ticket_code")
            or plan.get("ticket_ref")
        )
        if ticket_ref:
            updates["last_ticket"] = ticket_ref

    update_memory(session_id, **updates)


def _looks_like_new_intention(message: str) -> bool:
    text = _normalized_message(message)
    keywords = [
        "modifier",
        "change",
        "changer",
        "update",
        "corrige",
        "supprimer",
        "delete",
        "efface",
        "ajouter",
        "ajoute",
        "créer",
        "creer",
        "combien",
        "nombre",
        "liste",
        "téléphone de",
        "telephone de",
        "email de",
        "department de",
        "designation de",
        "absent",
        "absence",
        "absents",
        "anomalie",
        "top abs",
        "ticket",
        "tickets",
        "projet",
        "projets",
        "project",
        "projects",
    ]
    return any(keyword in text for keyword in keywords)


def _employee_candidate_text(employee: dict) -> str:
    values = [
        employee.get("full_name"),
        employee.get("name"),
        employee.get("firstname"),
        employee.get("lastname"),
        employee.get("email"),
    ]
    user = employee.get("user")
    if isinstance(user, dict):
        values.extend([user.get("firstname"), user.get("lastname"), user.get("email")])
    return " ".join(str(value).lower() for value in values if value)


def _resolve_disambiguation_choice(message: str, candidates: list) -> dict | None:
    text = _normalized_message(message)
    if not text:
        return None

    ordinal_map = {
        "1": 0,
        "premier": 0,
        "le premier": 0,
        "first": 0,
        "2": 1,
        "deuxième": 1,
        "deuxieme": 1,
        "second": 1,
        "le second": 1,
        "3": 2,
        "troisième": 2,
        "troisieme": 2,
        "third": 2,
    }
    if text in ordinal_map and ordinal_map[text] < len(candidates):
        return candidates[ordinal_map[text]]

    exact_matches = [
        employee
        for employee in candidates
        if text in {
            str(employee.get("full_name", "")).strip().lower(),
            str(employee.get("name", "")).strip().lower(),
            str(employee.get("email", "")).strip().lower(),
            f"{employee.get('firstname', '')} {employee.get('lastname', '')}".strip().lower(),
        }
    ]
    if len(exact_matches) == 1:
        return exact_matches[0]

    contains_matches = [
        employee
        for employee in candidates
        if text in _employee_candidate_text(employee)
    ]
    if len(contains_matches) == 1:
        return contains_matches[0]

    return None


@app.post("/chat")
async def chat(req: ChatRequest, request: Request, _: None = Depends(verify_admin_guard)):
    auth_header = request.headers.get("Authorization")
    if auth_header:
        request_token.set(auth_header)

    pending = get_pending_state(req.session_id)
    normalized_message = _normalized_message(req.message)

    if _memory_reset_requested(req.message):
        clear_conversation_memory(req.session_id)
        return {
            "message": "Contexte de conversation réinitialisé.",
            "meta": {
                "tool_name": None,
                "action_name": "reset_memory",
                "field": None,
                "employee_name": None,
                "project_name": None,
            },
        }

    if pending and pending.get("awaiting_disambiguation"):
        candidates = pending.get("candidates") or []
        selected_employee = _resolve_disambiguation_choice(req.message, candidates)
        pending_action = pending.get("pending_action")

        if selected_employee:
            plan = {
                "handled": True,
                "tool_name": "employees",
                "action_name": pending_action,
                "arguments": {},
                "_session_id": req.session_id,
                "_raw_message": req.message,
                "_selected_employee": selected_employee,
            }
            final_message = execute_employee_tool(plan)
        else:
            plan = {
                "handled": True,
                "tool_name": "employees",
                "action_name": pending_action,
                "arguments": {},
            }
            final_message = "Je n’ai pas reconnu ce choix. Donnez le numéro ou le nom complet."
    elif pending and pending.get("awaiting_confirmation"):
        pending_action = pending.get("pending_action")
        pending_tool = pending.get("tool_name") or "employees"
        if normalized_message in {"oui", "confirme", "confirm", "ok", "yes"}:
            plan = {
                "handled": True,
                "tool_name": pending_tool,
                "action_name": pending_action,
                "arguments": {},
                "_session_id": req.session_id,
                "_raw_message": req.message,
                "_confirmed": True,
            }
            if pending_tool == "ticket":
                final_message = execute_ticket_tool(plan)
            else:
                final_message = execute_employee_tool(plan)
        elif normalized_message in {"non", "annuler", "annule", "stop", "cancel", "no"}:
            clear_pending_state(req.session_id)
            plan = {
                "handled": True,
                "tool_name": pending_tool,
                "action_name": pending_action,
                "arguments": {},
            }
            final_message = _cancel_message(pending_action)
        else:
            if _looks_like_new_intention(req.message):
                clear_pending_state(req.session_id)
            new_plan = _plan_request(req.session_id, req.message)
            if not new_plan.get("error") and (
                new_plan.get("action_name") in ALL_ACTIONS
                or new_plan.get("tool_name") == "projects"
            ):
                plan = new_plan
                plan["_session_id"] = req.session_id
                plan["_raw_message"] = req.message
                if plan.get("tool_name") == "absence":
                    final_message = execute_absence_tool(plan)
                elif plan.get("tool_name") == "ticket":
                    final_message = execute_ticket_tool(plan)
                elif plan.get("tool_name") == "projects":
                    final_message = execute_project_tool(plan)
                else:
                    final_message = execute_employee_tool(plan)
            else:
                plan = {
                    "handled": True,
                    "tool_name": "employees",
                    "action_name": pending_action,
                    "arguments": {},
                }
                final_message = "Répondez par oui ou non."
    else:
        gate_result = classify_message(req.message, memory=get_memory(req.session_id))
        if gate_result.get("category") in {"chitchat", "offtopic"}:
            return {
                "message": gate_result.get("response"),
                "meta": {
                    "tool_name": None,
                    "action_name": gate_result.get("category"),
                    "field": None,
                    "employee_name": None,
                    "project_name": None,
                },
            }

        plan = _plan_request(req.session_id, req.message)
        plan["_session_id"] = req.session_id
        plan["_raw_message"] = req.message

        if pending and pending.get("pending_action") in {"create_employee", "update_employee"}:
            pending_action = pending.get("pending_action")
            if plan.get("error") or plan.get("tool_name") != "employees" or plan.get("action_name") != pending_action:
                plan = {
                    "handled": True,
                    "tool_name": "employees",
                    "action_name": pending_action,
                    "arguments": {},
                    "_session_id": req.session_id,
                    "_raw_message": req.message,
                }

        if plan.get("error"):
            final_message = plan.get("error") or OPENROUTER_ERROR_MESSAGE
        elif plan.get("action_name") == "unsupported_action":
            final_message = "Je suis votre assistant SmartHR. Comment puis-je vous aider avec les employés, absences, tickets ou projets ?"
        elif plan.get("tool_name") == "projects":
            final_message = execute_project_tool(plan)
        elif plan.get("action_name") not in ALL_ACTIONS or plan.get("tool_name") not in {"employees", "absence", "ticket"}:
            final_message = "Cette action n’est pas encore activée dans cette phase."
        else:
            if plan.get("tool_name") == "absence":
                final_message = execute_absence_tool(plan)
            elif plan.get("tool_name") == "ticket":
                final_message = execute_ticket_tool(plan)
            elif plan.get("tool_name") == "projects":
                final_message = execute_project_tool(plan)
            else:
                final_message = execute_employee_tool(plan)

    raw_response = final_message
    _update_conversation_memory(req.session_id, plan, raw_response)
    final_message = humanize_response(
        raw_response=raw_response,
        user_message=req.message,
        tool=plan.get("tool_name"),
        action=plan.get("action_name"),
        memory=get_memory(req.session_id),
    )

    arguments = plan.get("arguments") or {}
    return {
        "message": final_message,
        "meta": {
            "tool_name": plan.get("tool_name"),
            "action_name": plan.get("action_name"),
            "field": arguments.get("field"),
            "employee_name": arguments.get("employee_name"),
            "project_name": plan.get("project_name") or arguments.get("project_name"),
        },
    }
