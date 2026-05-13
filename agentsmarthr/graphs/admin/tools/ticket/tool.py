from datetime import datetime
from typing import Any, Dict, List
import unicodedata

from clients import php_api_client
from clients.employee_api_client import find_employee_by_name

from .prompts import TICKET_PROMPT


TOOL_DEFINITION = {
    "name": "ticket",
    "schema": {
        "actions": [
            "tickets_count_by_status",
            "tickets_count_open",
            "tickets_count_by_priority",
            "tickets_by_employee",
            "tickets_by_employee_list",
            "last_ticket_employee",
            "last_ticket_date_employee",
            "open_tickets_list",
            "tickets_today",
            "tickets_week",
            "tickets_month",
            "tickets_count_month",
            "employee_most_tickets",
            "employee_created_most_tickets",
            "tickets_by_status_stats",
            "tickets_by_priority_stats",
            "tickets_list_by_priority",
            "tickets_by_employee_and_priority",
            "last_ticket_employee_by_priority",
            "employee_open_tickets_count",
            "recent_tickets_employee",
            "most_recent_ticket",
            "search_tickets",
            "create_ticket",
            "update_ticket_status",
            "assign_ticket",
        ],
    },
    "prompt": TICKET_PROMPT,
}


def extract_ticket_list(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return [ticket for ticket in payload if isinstance(ticket, dict)]

    if not isinstance(payload, dict):
        return []

    for key in ("data", "tickets", "items", "results"):
        value = payload.get(key)
        if isinstance(value, list):
            return [ticket for ticket in value if isinstance(ticket, dict)]

    data = payload.get("data")
    if isinstance(data, dict):
        for key in ("data", "tickets", "items", "results"):
            value = data.get(key)
            if isinstance(value, list):
                return [ticket for ticket in value if isinstance(ticket, dict)]

    return []


def get_all_tickets() -> List[Dict[str, Any]]:
    return extract_ticket_list(php_api_client.get("/api/v1/tickets"))


def clean_text(value: Any) -> str:
    return str(value).strip() if value not in (None, "") else ""


def normalize_text(value: Any) -> str:
    text = clean_text(value).lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.replace("-", " ").replace("_", " ").split())


def normalize_search_text(value: Any) -> str:
    text = normalize_text(value)
    cleaned_chars = []
    for char in text:
        if char.isalnum():
            cleaned_chars.append(char)
        else:
            cleaned_chars.append(" ")
    return " ".join("".join(cleaned_chars).split())


def parse_ticket_date(ticket: Dict[str, Any]) -> datetime | None:
    for key in ("created_at", "date", "createdAt", "created", "updated_at"):
        raw_date = clean_text(ticket.get(key))
        if not raw_date:
            continue
        try:
            return datetime.fromisoformat(raw_date.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            continue
    return None


def get_ticket_code(ticket: Dict[str, Any]) -> str:
    for key in ("ticket_code", "tk_id", "code", "reference", "ticket_number"):
        value = clean_text(ticket.get(key))
        if value:
            return value

    ticket_id = clean_text(ticket.get("id"))
    if ticket_id:
        return f"TKT-{ticket_id}"
    return "TKT-N/A"


def get_ticket_subject(ticket: Dict[str, Any]) -> str:
    for key in ("subject", "title", "name"):
        value = clean_text(ticket.get(key))
        if value:
            return value

    description = clean_text(ticket.get("description"))
    if description:
        return description[:80]
    return "Sujet non renseigné"


def get_ticket_description(ticket: Dict[str, Any]) -> str:
    for key in ("description", "content", "details", "message", "body", "note"):
        value = clean_text(ticket.get(key))
        if value:
            return value
    return ""


def _person_full_name(data: Any) -> str:
    if not isinstance(data, dict):
        return clean_text(data)

    full_name = clean_text(data.get("full_name") or data.get("name"))
    if full_name:
        return full_name

    firstname = clean_text(data.get("firstname"))
    lastname = clean_text(data.get("lastname"))
    return " ".join(part for part in (firstname, lastname) if part)


def get_ticket_employee_name(ticket: Dict[str, Any]) -> str:
    direct_name = clean_text(ticket.get("employee_name"))
    if direct_name:
        return direct_name

    for key in ("employee", "user", "requester", "assigned_to"):
        name = _person_full_name(ticket.get(key))
        if name:
            return name

    return "Employé inconnu"


def get_ticket_creator_name(ticket: Dict[str, Any]) -> str:
    for key in ("created_by_name", "creator_name", "requester_name", "user_name"):
        value = clean_text(ticket.get(key))
        if value:
            return value

    for key in ("created_by", "creator", "requester", "user"):
        value = _person_full_name(ticket.get(key))
        if value:
            return value

    return ""


def normalize_status(value: Any) -> str:
    raw = normalize_text(value)
    mapping = {
        "new": "NEW",
        "nouveau": "NEW",
        "open": "OPEN",
        "opened": "OPEN",
        "ouvert": "OPEN",
        "ouverts": "OPEN",
        "reopen": "REOPEN",
        "reopened": "REOPEN",
        "reouvrir": "REOPEN",
        "réouvrir": "REOPEN",
        "onhold": "ONHOLD",
        "on hold": "ONHOLD",
        "pause": "ONHOLD",
        "en attente": "ONHOLD",
        "in progress": "IN_PROGRESS",
        "inprogress": "IN_PROGRESS",
        "in_progress": "IN_PROGRESS",
        "en cours": "IN_PROGRESS",
        "closed": "CLOSED",
        "close": "CLOSED",
        "ferme": "CLOSED",
        "fermes": "CLOSED",
        "fermer": "CLOSED",
        "fermeture": "CLOSED",
        "cancelled": "CANCELLED",
        "canceled": "CANCELLED",
        "annule": "CANCELLED",
        "annulé": "CANCELLED",
        "annuler": "CANCELLED",
        "completed": "COMPLETED",
        "complete": "COMPLETED",
        "resolved": "COMPLETED",
        "resolve": "COMPLETED",
        "resolu": "COMPLETED",
        "résolu": "COMPLETED",
        "resolus": "COMPLETED",
        "resoudre": "COMPLETED",
        "résoudre": "COMPLETED",
    }
    if raw in mapping:
        return mapping[raw]
    return raw.upper().replace(" ", "_")


def to_laravel_ticket_status(value: Any) -> str | None:
    v = normalize_text(value)
    mapping = {
        "new": "new",
        "nouveau": "new",
        "open": "open",
        "opened": "open",
        "ouvert": "open",
        "ouverts": "open",
        "reopen": "reopen",
        "reopened": "reopen",
        "réouvrir": "reopen",
        "reouvrir": "reopen",
        "onhold": "onhold",
        "on hold": "onhold",
        "pause": "onhold",
        "en attente": "onhold",
        "inprogress": "inprogress",
        "in_progress": "inprogress",
        "in progress": "inprogress",
        "en cours": "inprogress",
        "closed": "closed",
        "close": "closed",
        "fermé": "closed",
        "ferme": "closed",
        "fermer": "closed",
        "fermés": "closed",
        "fermes": "closed",
        "cancelled": "cancelled",
        "canceled": "cancelled",
        "annulé": "cancelled",
        "annule": "cancelled",
        "annuler": "cancelled",
        "completed": "completed",
        "complete": "completed",
        "resolved": "completed",
        "résolu": "completed",
        "resolu": "completed",
        "résoudre": "completed",
        "resoudre": "completed",
    }
    return mapping.get(v)


def normalize_priority(value: Any) -> str:
    raw = normalize_text(value)
    mapping = {
        "urgent": "HIGH",
        "urgents": "HIGH",
        "urgente": "HIGH",
        "urgentes": "HIGH",
        "critique": "HIGH",
        "critical": "HIGH",
        "haute": "HIGH",
        "haute priorite": "HIGH",
        "high": "HIGH",
        "medium": "MEDIUM",
        "moyenne": "MEDIUM",
        "moyenne priorite": "MEDIUM",
        "low": "LOW",
        "basse": "LOW",
        "basse priorite": "LOW",
    }
    if raw in mapping:
        return mapping[raw]
    return raw.upper().replace(" ", "_")


def employee_name_matches(ticket: Dict[str, Any], query: Any) -> bool:
    searched = normalize_text(query)
    if not searched:
        return False

    employee_name = normalize_text(get_ticket_employee_name(ticket))
    if not employee_name:
        return False

    if searched == employee_name or searched in employee_name or employee_name in searched:
        return True

    parts = [part for part in employee_name.split() if part]
    return searched in parts or any(part in searched for part in parts)


def ticket_date_text(ticket: Dict[str, Any]) -> str:
    ticket_date = parse_ticket_date(ticket)
    return ticket_date.date().isoformat() if ticket_date else "Non renseigné"


def format_ticket_line(ticket: Dict[str, Any], index: int) -> str:
    return (
        f"{index}. {get_ticket_code(ticket)} — "
        f"{get_ticket_subject(ticket)} — "
        f"{normalize_status(ticket.get('status')) or 'STATUS_INCONNU'} — "
        f"{normalize_priority(ticket.get('priority')) or 'PRIORITÉ_INCONNUE'} — "
        f"{get_ticket_employee_name(ticket)} — "
        f"{ticket_date_text(ticket)}"
    )


def _normalized_fields(fields: Any) -> List[str]:
    if not fields:
        return ["all"]
    if isinstance(fields, str):
        return [normalize_search_text(fields)]
    if isinstance(fields, list):
        normalized = [normalize_search_text(field) for field in fields if clean_text(field)]
        return normalized or ["all"]
    return ["all"]


def get_ticket_search_blob(ticket: Dict[str, Any], fields: Any = None) -> str:
    normalized_fields = _normalized_fields(fields)

    if "subject" in normalized_fields:
        return " ".join(
            clean_text(ticket.get(key))
            for key in ("subject", "title", "name")
            if clean_text(ticket.get(key))
        )

    if "description" in normalized_fields:
        return get_ticket_description(ticket)

    values = [
        get_ticket_code(ticket),
        get_ticket_subject(ticket),
        get_ticket_description(ticket),
        normalize_status(ticket.get("status")),
        normalize_priority(ticket.get("priority")),
        get_ticket_employee_name(ticket),
        get_ticket_creator_name(ticket),
    ]
    return " ".join(value for value in values if clean_text(value))


def search_tickets(tickets: List[Dict[str, Any]], query: Any, fields: Any = None) -> List[Dict[str, Any]]:
    normalized_query = normalize_search_text(query)
    if not normalized_query:
        return []

    results = []
    for ticket in tickets or []:
        if not isinstance(ticket, dict):
            continue
        blob = get_ticket_search_blob(ticket, fields)
        if normalized_query in normalize_search_text(blob):
            results.append(ticket)
    return results


def format_search_results(results: List[Dict[str, Any]], query: Any, limit: int = 10) -> str:
    visible_results = results[:limit]
    lines = [f"Tickets trouvés pour '{clean_text(query)}' :", ""]
    for index, ticket in enumerate(visible_results, start=1):
        ticket_date = parse_ticket_date(ticket)
        date_text = ticket_date.date().isoformat() if ticket_date else "Date inconnue"
        lines.append(
            f"{index}. {get_ticket_code(ticket)} — "
            f"{get_ticket_subject(ticket)} — "
            f"{normalize_status(ticket.get('status')) or 'STATUS_INCONNU'} — "
            f"{normalize_priority(ticket.get('priority')) or 'PRIORITÉ_INCONNUE'} — "
            f"{get_ticket_employee_name(ticket)} — "
            f"{date_text}"
        )

    remaining_count = len(results) - len(visible_results)
    if remaining_count > 0:
        lines.append(f"... et {remaining_count} autre(s) ticket(s).")
    return "\n".join(lines)


def get_active_statuses() -> List[str]:
    return ["OPEN", "NEW", "INPROGRESS", "REOPEN", "ONHOLD"]


def _compact_status(value: Any) -> str:
    return normalize_status(value).replace("_", "")


def is_active_ticket(ticket: Dict[str, Any]) -> bool:
    return _compact_status(ticket.get("status")) in get_active_statuses()


def get_employee_ticket_load(tickets: List[Dict[str, Any]], employee_name: str) -> Dict[str, int]:
    matched_tickets = [
        ticket
        for ticket in tickets or []
        if isinstance(ticket, dict) and employee_name_matches(ticket, employee_name)
    ]
    active_tickets = [ticket for ticket in matched_tickets if is_active_ticket(ticket)]
    return {
        "active_count": len(active_tickets),
        "open_count": sum(1 for ticket in matched_tickets if normalize_status(ticket.get("status")) == "OPEN"),
        "high_active_count": sum(
            1
            for ticket in active_tickets
            if normalize_priority(ticket.get("priority")) == "HIGH"
        ),
        "total_count": len(matched_tickets),
    }


def recommend_employee_load(employee_name: str, load: Dict[str, int]) -> str:
    name = clean_text(employee_name)
    if not name or not isinstance(load, dict):
        return "Recommandation indisponible : données insuffisantes."

    active_count = int(load.get("active_count") or 0)
    open_count = int(load.get("open_count") or 0)
    high_active_count = int(load.get("high_active_count") or 0)

    if active_count >= 5 and high_active_count >= 3:
        return (
            f"{name} est déjà très chargé avec {active_count} tickets actifs, "
            f"dont {high_active_count} urgents. Je recommande de vérifier sa disponibilité "
            "avant de lui ajouter d’autres tickets."
        )
    if active_count >= 5:
        return (
            f"{name} est déjà très chargé avec {active_count} tickets actifs. "
            "Je recommande de vérifier sa disponibilité ou d’assigner à un employé moins chargé."
        )
    if high_active_count >= 3:
        return (
            f"{name} a déjà {high_active_count} tickets urgents actifs. "
            "Il vaut mieux prioriser ou redistribuer."
        )
    if open_count >= 5:
        return f"{name} est très chargé."
    if 3 <= open_count <= 4:
        return f"{name} a une charge moyenne."
    if open_count <= 2:
        return f"Charge actuelle acceptable pour {name}."

    return "Recommandation indisponible : données insuffisantes."


def _ticket_has_critical_words(ticket: Dict[str, Any]) -> bool:
    critical_words = ["bank", "login", "payment", "payroll", "salary", "security", "accès", "erreur"]
    text = normalize_search_text(f"{get_ticket_subject(ticket)} {get_ticket_description(ticket)}")
    return any(normalize_search_text(word) in text for word in critical_words)


def score_ticket_priority(ticket: Dict[str, Any]) -> int:
    score = 0
    if normalize_priority(ticket.get("priority")) == "HIGH":
        score += 50
    if is_active_ticket(ticket):
        score += 30

    ticket_date = parse_ticket_date(ticket)
    if ticket_date:
        age_days = max((datetime.now() - ticket_date).days, 0)
        score += min(age_days, 20)

    if _ticket_has_critical_words(ticket):
        score += 20
    return score


def recommend_first_ticket(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    candidates = [
        ticket
        for ticket in tickets or []
        if isinstance(ticket, dict)
        and normalize_priority(ticket.get("priority")) == "HIGH"
        and is_active_ticket(ticket)
    ]
    if not candidates:
        return {"ticket": None, "reason": "Recommandation indisponible : données insuffisantes."}

    best_ticket = sorted(
        candidates,
        key=lambda ticket: (-score_ticket_priority(ticket), parse_ticket_date(ticket) or datetime.max),
    )[0]
    reason_parts = ["il est urgent", "encore ouvert"]
    if parse_ticket_date(best_ticket):
        reason_parts.append("plus ancien")
    if _ticket_has_critical_words(best_ticket):
        reason_parts.append("concerne un sujet critique")

    return {
        "ticket": best_ticket,
        "reason": (
            f"Je recommande de commencer par {get_ticket_code(best_ticket)} car "
            + ", ".join(reason_parts[:-1])
            + (" et " + reason_parts[-1] if len(reason_parts) > 1 else reason_parts[0])
            + "."
        ),
    }


def get_ticket_id(ticket: Dict[str, Any]) -> Any:
    return ticket.get("id") or ticket.get("ticket_id")


def normalize_ticket_code_for_match(value: Any) -> str:
    code = clean_text(value).upper().replace(" ", "")
    if code.startswith("#"):
        code = code[1:]
    return code.replace("-", "")


def _ticket_code_values(ticket: Dict[str, Any]) -> List[str]:
    values = [
        ticket.get("ticket_code"),
        ticket.get("tk_id"),
        ticket.get("code"),
        ticket.get("reference"),
        ticket.get("ticket_number"),
    ]
    return [value for value in values if clean_text(value)]


def _ticket_numeric_value(value: Any) -> int | None:
    text = clean_text(value)
    if not text or not text.isdigit():
        return None
    return int(text)


def _ticket_code_numeric_suffix(value: Any) -> int | None:
    normalized = normalize_ticket_code_for_match(value)
    if not normalized.startswith("TKT"):
        return None
    suffix = normalized[3:]
    if not suffix.isdigit():
        return None
    return int(suffix)


def _requested_ticket_is_full_code(ticket_code: Any) -> bool:
    normalized = normalize_ticket_code_for_match(ticket_code)
    return normalized.startswith("TKT") and any(char.isdigit() for char in normalized)


def find_ticket_by_code(ticket_code: Any, tickets: List[Dict[str, Any]] | None = None) -> Dict[str, Any] | None:
    requested = clean_text(ticket_code)
    if not requested:
        return None

    ticket_list = tickets if tickets is not None else get_all_tickets()
    matches: List[Dict[str, Any]] = []

    if _requested_ticket_is_full_code(requested):
        requested_code = normalize_ticket_code_for_match(requested)
        for ticket in ticket_list:
            ticket_codes = [normalize_ticket_code_for_match(value) for value in _ticket_code_values(ticket)]
            if requested_code in ticket_codes:
                matches.append(ticket)
    else:
        requested_number = _ticket_numeric_value(requested)
        if requested_number is None:
            return None

        for ticket in ticket_list:
            id_values = [ticket.get("id"), ticket.get("ticket_id")]
            if any(_ticket_numeric_value(value) == requested_number for value in id_values):
                matches.append(ticket)
                continue

            ticket_number = _ticket_numeric_value(ticket.get("ticket_number"))
            if ticket_number == requested_number:
                matches.append(ticket)
                continue

            code_suffixes = [_ticket_code_numeric_suffix(value) for value in _ticket_code_values(ticket)]
            if requested_number in code_suffixes:
                matches.append(ticket)

    unique_matches: List[Dict[str, Any]] = []
    seen_ids = set()
    for ticket in matches:
        identity = get_ticket_id(ticket) or id(ticket)
        if identity in seen_ids:
            continue
        seen_ids.add(identity)
        unique_matches.append(ticket)

    if len(unique_matches) > 1:
        raise ValueError("J’ai trouvé plusieurs tickets possibles. Donnez le code exact du ticket.")
    if len(unique_matches) == 1:
        return unique_matches[0]

    return None


def _backend_status(value: Any) -> str:
    backend_status = to_laravel_ticket_status(value)
    if backend_status:
        return backend_status
    return clean_text(value).lower()


def _backend_priority(value: Any) -> str:
    priority = normalize_priority(value) or "MEDIUM"
    return priority.lower()


def _extract_user_id(employee: Dict[str, Any]) -> Any:
    user = employee.get("user")
    if isinstance(user, dict):
        return user.get("id") or user.get("user_id")
    return employee.get("user_id") or employee.get("id")


def _employee_display_name(employee: Dict[str, Any]) -> str:
    full_name = clean_text(employee.get("full_name") or employee.get("name"))
    if full_name:
        return full_name
    firstname = clean_text(employee.get("firstname"))
    lastname = clean_text(employee.get("lastname"))
    display_name = f"{firstname} {lastname}".strip()
    if display_name:
        return display_name
    user = employee.get("user")
    if isinstance(user, dict):
        return clean_text(user.get("full_name") or user.get("name") or user.get("email"))
    return clean_text(employee.get("email")) or "Employé"


def resolve_employee_for_ticket(employee_name: str) -> Dict[str, Any]:
    result = find_employee_by_name(employee_name, use_search=True)
    status = result.get("status")
    if status == "found":
        employee = result.get("employee") or {}
        return {
            "status": "found",
            "employee": employee,
            "employee_id": employee.get("id"),
            "user_id": _extract_user_id(employee),
            "employee_name": _employee_display_name(employee),
        }
    if status == "multiple":
        return {
            "status": "multiple",
            "message": "J’ai trouvé plusieurs employés avec ce nom. Pouvez-vous préciser ?",
        }
    return {"status": "not_found", "message": "Employé introuvable."}


def build_full_ticket_update_payload(ticket: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    assigned_to = ticket.get("assigned_to")
    assigned_user_id = None
    if isinstance(assigned_to, dict):
        assigned_user_id = assigned_to.get("id") or assigned_to.get("user_id")

    payload = {
        "subject": get_ticket_subject(ticket),
        "description": get_ticket_description(ticket) or get_ticket_subject(ticket),
        "priority": _backend_priority(ticket.get("priority")),
        "status": _backend_status(ticket.get("status")),
        "user_id": ticket.get("user_id") or assigned_user_id,
    }
    payload.update(overrides)
    return {key: value for key, value in payload.items() if value not in (None, "")}


def create_ticket_backend(payload: Dict[str, Any]) -> Any:
    prepared_payload = dict(payload)
    prepared_payload["status"] = to_laravel_ticket_status(prepared_payload.get("status") or "open")
    print("USER STATUS:", payload.get("status") or "open")
    print("LARAVEL STATUS:", prepared_payload["status"])
    if not prepared_payload["status"]:
        raise ValueError("Statut invalide. Utilisez : new, open, reopen, onhold, closed, inprogress, cancelled, completed.")
    return php_api_client.post("/api/v1/tickets", json=prepared_payload)


def update_ticket_status_backend(ticket_id_or_code: Any, status: str) -> Any:
    tickets = get_all_tickets()
    ticket = find_ticket_by_code(ticket_id_or_code, tickets)
    if not ticket:
        raise ValueError("Ticket introuvable.")

    ticket_id = get_ticket_id(ticket)
    if not ticket_id:
        raise ValueError("Ticket introuvable.")

    backend_status = to_laravel_ticket_status(status)
    print("USER STATUS:", status)
    print("LARAVEL STATUS:", backend_status)
    if not backend_status:
        raise ValueError("Statut invalide. Utilisez : new, open, reopen, onhold, closed, inprogress, cancelled, completed.")

    payload = build_full_ticket_update_payload(ticket, {"status": backend_status})
    return php_api_client.patch(f"/api/v1/tickets/{ticket_id}", json=payload)


def assign_ticket_backend(ticket_id_or_code: Any, employee_name: str) -> Any:
    tickets = get_all_tickets()
    ticket = find_ticket_by_code(ticket_id_or_code, tickets)
    if not ticket:
        raise ValueError("Ticket introuvable.")

    ticket_id = get_ticket_id(ticket)
    if not ticket_id:
        raise ValueError("Ticket introuvable.")

    employee_result = resolve_employee_for_ticket(employee_name)
    if employee_result.get("status") != "found":
        raise ValueError(employee_result.get("message") or "Employé introuvable.")
    if not employee_result.get("user_id"):
        raise ValueError("Employé introuvable.")

    payload = build_full_ticket_update_payload(ticket, {"user_id": employee_result.get("user_id")})
    return php_api_client.patch(f"/api/v1/tickets/{ticket_id}", json=payload)
