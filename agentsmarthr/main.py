import sys
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

AGENT_ROOT = Path(__file__).resolve().parent
if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))

from graphs.admin.mcp.micro_planner import OPENROUTER_ERROR_MESSAGE, plan_employee_request
from graphs.admin.tools.absence.executor import ABSENCE_ACTIONS, execute_absence_tool
from graphs.admin.tools.employees.executor import execute_employee_tool
from graphs.admin.tools.ticket.executor import TICKET_ACTIONS, execute_ticket_tool
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
    elif tool_name in ("employee", "employees"):
        plan["tool_name"] = "employees"
    elif tool_name in ("absence", "absences"):
        plan["tool_name"] = "absence"
    elif tool_name in ("ticket", "tickets"):
        plan["tool_name"] = "ticket"

    action_name = str(plan.get("action_name") or "").lower()
    if action_name == "add_employee":
        plan["action_name"] = "create_employee"
    elif action_name == "edit_employee":
        plan["action_name"] = "update_employee"
    elif action_name == "remove_employee":
        plan["action_name"] = "delete_employee"
    elif action_name in ("list_clients", "get_clients"):
        plan["action_name"] = "projects_by_client"

    if plan.get("action_name") in EMPLOYEE_ACTIONS and not plan.get("tool_name"):
        plan["tool_name"] = "employees"
    if plan.get("action_name") in ABSENCE_ACTIONS and not plan.get("tool_name"):
        plan["tool_name"] = "absence"
    if plan.get("action_name") in TICKET_ACTIONS and not plan.get("tool_name"):
        plan["tool_name"] = "ticket"
    if plan.get("action_name") in PROJECT_ACTIONS and not plan.get("tool_name"):
        plan["tool_name"] = "projects"
    return plan


def _plan_request(message: str) -> dict:
    return _normalize_plan(plan_employee_request(message))


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
async def chat(req: ChatRequest, _: None = Depends(verify_admin_guard)):
    pending = get_pending_state(req.session_id)
    normalized_message = _normalized_message(req.message)

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
            new_plan = _plan_request(req.message)
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
        plan = _plan_request(req.message)
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
