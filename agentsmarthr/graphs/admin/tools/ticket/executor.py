from datetime import date, datetime, timedelta
from typing import Any, Dict, List

from clients import php_api_client
from graphs.admin.tools.ticket.tool import (
    assign_ticket_backend,
    build_full_ticket_update_payload,
    create_ticket_backend,
    employee_name_matches,
    find_ticket_by_code,
    format_ticket_line,
    format_search_results,
    get_all_tickets,
    get_employee_ticket_load,
    get_ticket_code,
    get_ticket_employee_name as tool_get_ticket_employee_name,
    get_ticket_subject,
    normalize_priority as tool_normalize_priority,
    normalize_status as tool_normalize_status,
    normalize_ticket_code_for_match,
    parse_ticket_date,
    recommend_employee_load,
    recommend_first_ticket,
    resolve_employee_for_ticket,
    search_tickets,
    ticket_date_text,
    to_laravel_ticket_status,
    update_ticket_status_backend,
)
from memory.pending_state import clear_pending_state, get_pending_state, set_pending_state


TICKETS_COUNT_BY_STATUS = "tickets_count_by_status"
TICKETS_COUNT_OPEN = "tickets_count_open"
TICKETS_COUNT_BY_PRIORITY = "tickets_count_by_priority"
TICKETS_BY_EMPLOYEE = "tickets_by_employee"
TICKETS_BY_EMPLOYEE_LIST = "tickets_by_employee_list"
LAST_TICKET_EMPLOYEE = "last_ticket_employee"
LAST_TICKET_DATE_EMPLOYEE = "last_ticket_date_employee"
OPEN_TICKETS_LIST = "open_tickets_list"
TICKETS_TODAY = "tickets_today"
TICKETS_WEEK = "tickets_week"
TICKETS_MONTH = "tickets_month"
TICKETS_COUNT_MONTH = "tickets_count_month"
EMPLOYEE_MOST_TICKETS = "employee_most_tickets"
EMPLOYEE_CREATED_MOST_TICKETS = "employee_created_most_tickets"
TICKETS_BY_STATUS_STATS = "tickets_by_status_stats"
TICKETS_BY_PRIORITY_STATS = "tickets_by_priority_stats"
TICKETS_LIST_BY_PRIORITY = "tickets_list_by_priority"
TICKETS_BY_EMPLOYEE_AND_PRIORITY = "tickets_by_employee_and_priority"
LAST_TICKET_EMPLOYEE_BY_PRIORITY = "last_ticket_employee_by_priority"
EMPLOYEE_OPEN_TICKETS_COUNT = "employee_open_tickets_count"
RECENT_TICKETS_EMPLOYEE = "recent_tickets_employee"
MOST_RECENT_TICKET = "most_recent_ticket"
SEARCH_TICKETS = "search_tickets"
CREATE_TICKET = "create_ticket"
UPDATE_TICKET_STATUS = "update_ticket_status"
ASSIGN_TICKET = "assign_ticket"
TICKET_ACTIONS = {
    TICKETS_COUNT_BY_STATUS,
    TICKETS_COUNT_OPEN,
    TICKETS_COUNT_BY_PRIORITY,
    TICKETS_BY_EMPLOYEE,
    TICKETS_BY_EMPLOYEE_LIST,
    LAST_TICKET_EMPLOYEE,
    LAST_TICKET_DATE_EMPLOYEE,
    OPEN_TICKETS_LIST,
    TICKETS_TODAY,
    TICKETS_WEEK,
    TICKETS_MONTH,
    TICKETS_COUNT_MONTH,
    EMPLOYEE_MOST_TICKETS,
    EMPLOYEE_CREATED_MOST_TICKETS,
    TICKETS_BY_STATUS_STATS,
    TICKETS_BY_PRIORITY_STATS,
    TICKETS_LIST_BY_PRIORITY,
    TICKETS_BY_EMPLOYEE_AND_PRIORITY,
    LAST_TICKET_EMPLOYEE_BY_PRIORITY,
    EMPLOYEE_OPEN_TICKETS_COUNT,
    RECENT_TICKETS_EMPLOYEE,
    MOST_RECENT_TICKET,
    SEARCH_TICKETS,
    CREATE_TICKET,
    UPDATE_TICKET_STATUS,
    ASSIGN_TICKET,
}

VALID_TICKET_STATUSES = {"NEW", "OPEN", "REOPEN", "ONHOLD", "CLOSED", "IN_PROGRESS", "CANCELLED", "COMPLETED"}
VALID_TICKET_PRIORITIES = {"HIGH", "MEDIUM", "LOW"}


def _clean(value: Any) -> str:
    return str(value).strip() if value not in (None, "") else ""


def _person_full_name(data: Any) -> str:
    if not isinstance(data, dict):
        return ""
    full_name = _clean(data.get("full_name") or data.get("name"))
    if full_name:
        return full_name
    firstname = _clean(data.get("firstname"))
    lastname = _clean(data.get("lastname"))
    return " ".join(part for part in (firstname, lastname) if part)


def normalize_status(value: Any) -> str:
    raw = _clean(value).lower().replace("-", " ").replace("_", " ")
    mapping = {
        "open": "OPEN",
        "opened": "OPEN",
        "closed": "CLOSED",
        "resolved": "RESOLVED",
        "new": "NEW",
        "in progress": "IN_PROGRESS",
        "inprogress": "IN_PROGRESS",
    }
    if raw in mapping:
        return mapping[raw]
    return raw.upper().replace(" ", "_")


def normalize_priority(value: Any) -> str:
    raw = _clean(value).lower().replace("-", " ").replace("_", " ")
    mapping = {
        "urgent": "HIGH",
        "urgents": "HIGH",
        "critique": "HIGH",
        "critical": "HIGH",
        "haute": "HIGH",
        "haute priorite": "HIGH",
        "haute priorité": "HIGH",
        "high": "HIGH",
        "medium": "MEDIUM",
        "moyenne": "MEDIUM",
        "moyenne priorite": "MEDIUM",
        "moyenne priorité": "MEDIUM",
        "low": "LOW",
        "basse": "LOW",
        "basse priorite": "LOW",
        "basse priorité": "LOW",
    }
    if raw in mapping:
        return mapping[raw]
    return raw.upper().replace(" ", "_")


def get_ticket_employee_name(ticket: Dict[str, Any]) -> str:
    direct_name = _clean(ticket.get("employee_name"))
    if direct_name:
        return direct_name

    for key in ("employee", "user", "requester", "assigned_to"):
        direct_value = ticket.get(key)
        if not isinstance(direct_value, dict):
            direct_name = _clean(direct_value)
            if direct_name:
                return direct_name
        name = _person_full_name(ticket.get(key))
        if name:
            return name

    return "Employé inconnu"


def get_ticket_creator_name(ticket: Dict[str, Any]) -> tuple[str, bool]:
    for key in ("created_by_name", "creator_name", "requester_name", "user_name"):
        name = _clean(ticket.get(key))
        if name:
            return name, False

    for key in ("created_by", "creator", "requester", "user"):
        direct_value = ticket.get(key)
        if not isinstance(direct_value, dict):
            direct_name = _clean(direct_value)
            if direct_name:
                return direct_name, False
        name = _person_full_name(ticket.get(key))
        if name:
            return name, False

    employee_name = get_ticket_employee_name(ticket)
    if employee_name != "Employé inconnu":
        return employee_name, True

    return "Créateur inconnu", False


def _status(ticket: Dict[str, Any]) -> str:
    return normalize_status(ticket.get("status"))


def _title(ticket: Dict[str, Any]) -> str:
    return _clean(ticket.get("title") or ticket.get("subject")) or f"Ticket #{ticket.get('id')}"


def _employee_name(ticket: Dict[str, Any]) -> str:
    return get_ticket_employee_name(ticket)


def _employee_matches(ticket: Dict[str, Any], employee_name: str) -> bool:
    searched = _clean(employee_name).lower()
    if not searched:
        return False
    return searched in _employee_name(ticket).lower()


def _created_at(ticket: Dict[str, Any]) -> datetime:
    raw_date = _clean(ticket.get("created_at"))
    if not raw_date:
        return datetime.min
    try:
        return datetime.fromisoformat(raw_date.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return datetime.min


def _created_date(ticket: Dict[str, Any]) -> date | None:
    created_at = _created_at(ticket)
    if created_at == datetime.min:
        return None
    return created_at.date()


def _date_text(ticket: Dict[str, Any]) -> str:
    created_date = _created_date(ticket)
    return created_date.isoformat() if created_date else "Non renseigné"


def _week_range(today: date) -> tuple[date, date]:
    start = today - timedelta(days=today.weekday())
    return start, start + timedelta(days=6)


def _month_range(today: date) -> tuple[date, date]:
    start = today.replace(day=1)
    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)
    return start, next_month - timedelta(days=1)


def _ticket_line(ticket: Dict[str, Any], index: int) -> str:
    priority = _clean(ticket.get("priority")) or "priorité inconnue"
    employee = _employee_name(ticket) or "non assigné"
    return f"{index}. {_title(ticket)} — {_status(ticket) or 'status inconnu'} — {priority} — {employee}"


def _employee_ticket_line(ticket: Dict[str, Any], index: int) -> str:
    return f"{index}. {_title(ticket)} — {_status(ticket) or 'status inconnu'} — {_date_text(ticket)}"


def normalize_status(value: Any) -> str:
    return tool_normalize_status(value)


def normalize_priority(value: Any) -> str:
    return tool_normalize_priority(value)


def get_ticket_employee_name(ticket: Dict[str, Any]) -> str:
    return tool_get_ticket_employee_name(ticket)


def _title(ticket: Dict[str, Any]) -> str:
    return get_ticket_subject(ticket)


def _employee_matches(ticket: Dict[str, Any], employee_name: str) -> bool:
    return employee_name_matches(ticket, employee_name)


def _created_at(ticket: Dict[str, Any]) -> datetime:
    parsed_date = parse_ticket_date(ticket)
    return parsed_date if parsed_date else datetime.min


def _date_text(ticket: Dict[str, Any]) -> str:
    return ticket_date_text(ticket)


def _tickets_or_error() -> Dict[str, Any]:
    try:
        tickets = get_all_tickets()
        print("TICKETS COUNT:", len(tickets))
        return {"ok": True, "tickets": tickets}
    except php_api_client.SmartHRApiError as error:
        if error.status_code == 401:
            return {"ok": False, "message": "Laravel a refusé la demande tickets : token invalide."}
        return {"ok": False, "message": f"Laravel a refusé la demande tickets : {error.message}"}
    except Exception:
        return {"ok": False, "message": "Impossible de récupérer les tickets depuis Laravel."}


def _execute_count_by_status(arguments: Dict[str, Any]) -> str:
    requested_status = normalize_status(arguments.get("status"))
    if not requested_status:
        return "Quel status de ticket voulez-vous compter ?"

    result = _tickets_or_error()
    if not result["ok"]:
        return result["message"]

    count = sum(1 for ticket in result["tickets"] if _status(ticket) == requested_status)
    return f"Il y a {count} ticket(s) avec le status {requested_status}."


def _execute_tickets_count_open() -> str:
    result = _tickets_or_error()
    if not result["ok"]:
        return result["message"]

    count = sum(1 for ticket in result["tickets"] if _status(ticket) == "OPEN")
    return f"Il y a {count} ticket(s) ouverts."


def _execute_count_by_priority(arguments: Dict[str, Any]) -> str:
    requested_priority = normalize_priority(arguments.get("priority"))
    if not requested_priority:
        return "Quelle priorité voulez-vous compter ?"

    result = _tickets_or_error()
    if not result["ok"]:
        return result["message"]

    count = sum(
        1
        for ticket in result["tickets"]
        if normalize_priority(ticket.get("priority")) == requested_priority
    )
    if count == 0:
        return f"Aucun ticket avec la priorité {requested_priority} trouvé."

    return f"Il y a {count} ticket(s) avec la priorité {requested_priority}."


def _count_by_name(tickets: List[Dict[str, Any]], name_getter) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for ticket in tickets:
        name = name_getter(ticket)
        if isinstance(name, tuple):
            name = name[0]
        name = _clean(name)
        if not name:
            continue
        counts[name] = counts.get(name, 0) + 1
    return counts


def _top_count(counts: Dict[str, int]) -> tuple[str, int] | None:
    if not counts:
        return None
    return sorted(counts.items(), key=lambda item: item[1], reverse=True)[0]


def _execute_employee_most_tickets() -> str:
    result = _tickets_or_error()
    if not result["ok"]:
        return result["message"]

    tickets = result["tickets"]
    if not tickets:
        return "Aucun ticket trouvé."

    top = _top_count(_count_by_name(tickets, get_ticket_employee_name))
    if not top:
        return "Aucun ticket trouvé."

    employee_name, count = top
    return f"L’employé avec le plus de tickets est {employee_name} avec {count} ticket(s)."


def _execute_employee_created_most_tickets() -> str:
    result = _tickets_or_error()
    if not result["ok"]:
        return result["message"]

    tickets = result["tickets"]
    if not tickets:
        return "Aucun ticket trouvé."

    counts: Dict[str, int] = {}
    fallback_used = False
    for ticket in tickets:
        creator_name, used_employee_fallback = get_ticket_creator_name(ticket)
        fallback_used = fallback_used or used_employee_fallback
        counts[creator_name] = counts.get(creator_name, 0) + 1

    top = _top_count(counts)
    if not top:
        return "Aucun ticket trouvé."

    creator_name, count = top
    response = f"L’employé qui a créé le plus de tickets est {creator_name} avec {count} ticket(s)."
    if fallback_used:
        response += "\nNote : calcul basé sur les tickets associés aux employés."
    return response


def _format_stats(title: str, counts: Dict[str, int]) -> str:
    if not counts:
        return "Aucun ticket trouvé."

    lines = [title, ""]
    for key, count in sorted(counts.items(), key=lambda item: item[1], reverse=True):
        lines.append(f"* {key} : {count}")
    return "\n".join(lines)


def _execute_tickets_by_status_stats() -> str:
    result = _tickets_or_error()
    if not result["ok"]:
        return result["message"]

    counts: Dict[str, int] = {}
    for ticket in result["tickets"]:
        status = _status(ticket) or "STATUS_INCONNU"
        counts[status] = counts.get(status, 0) + 1
    return _format_stats("Tickets par statut :", counts)


def _execute_tickets_by_priority_stats() -> str:
    result = _tickets_or_error()
    if not result["ok"]:
        return result["message"]

    counts: Dict[str, int] = {}
    for ticket in result["tickets"]:
        priority = normalize_priority(ticket.get("priority")) or "PRIORITÉ_INCONNUE"
        counts[priority] = counts.get(priority, 0) + 1
    return _format_stats("Tickets par priorité :", counts)


def _sorted_by_recent(tickets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(tickets, key=_created_at, reverse=True)


def _limit_lines(tickets: List[Dict[str, Any]], formatter=format_ticket_line, limit: int = 10) -> List[str]:
    visible_tickets = tickets[:limit]
    lines = [formatter(ticket, index) for index, ticket in enumerate(visible_tickets, start=1)]
    remaining_count = len(tickets) - len(visible_tickets)
    if remaining_count > 0:
        lines.append(f"... et {remaining_count} autre(s) ticket(s).")
    return lines


def _filter_by_priority(tickets: List[Dict[str, Any]], priority: str) -> List[Dict[str, Any]]:
    normalized_priority = normalize_priority(priority)
    return [
        ticket
        for ticket in tickets
        if normalize_priority(ticket.get("priority")) == normalized_priority
    ]


def _filter_by_employee(tickets: List[Dict[str, Any]], employee_name: str) -> List[Dict[str, Any]]:
    return [ticket for ticket in tickets if employee_name_matches(ticket, employee_name)]


def _priority_argument(arguments: Dict[str, Any]) -> str:
    return normalize_priority(arguments.get("priority"))


def _employee_argument(arguments: Dict[str, Any]) -> str:
    return _clean(arguments.get("employee_name") or arguments.get("employee"))


def _ticket_requested_matches_found(requested_code: str, found_code: str) -> bool:
    requested = _clean(requested_code)
    if requested.isdigit():
        return True
    return normalize_ticket_code_for_match(requested) == normalize_ticket_code_for_match(found_code)


def _ticket_not_found_message(ticket_code: str) -> str:
    return f"Ticket {ticket_code} introuvable."


def _ticket_display_code(ticket_code: str) -> str:
    code = _clean(ticket_code)
    return code[1:] if code.startswith("#") else code


def _recommendation_section(recommendation: str) -> str:
    text = _clean(recommendation)
    if not text:
        text = "Recommandation indisponible : données insuffisantes."
    return f"\n\nRecommandation :\n{text}"


def _employee_load_recommendation(employee_name: str, extra_ticket: Dict[str, Any] | None = None) -> str:
    try:
        tickets = get_all_tickets()
    except Exception:
        return "Recommandation indisponible : données insuffisantes."

    if not tickets and not extra_ticket:
        return "Recommandation indisponible : données insuffisantes."
    if extra_ticket:
        tickets = list(tickets) + [extra_ticket]
    load = get_employee_ticket_load(tickets, employee_name)
    return recommend_employee_load(employee_name, load)


def _execute_tickets_list_by_priority(arguments: Dict[str, Any]) -> str:
    priority = _priority_argument(arguments)
    if not priority:
        return "Quelle priorité voulez-vous consulter ?"

    result = _tickets_or_error()
    if not result["ok"]:
        return result["message"]

    filtered_tickets = _sorted_by_recent(_filter_by_priority(result["tickets"], priority))
    print("FILTERED COUNT:", len(filtered_tickets))
    if not filtered_tickets:
        return f"Aucun ticket avec la priorité {priority} trouvé."

    lines = [f"Tickets priorité {priority} :", ""]
    lines.extend(_limit_lines(filtered_tickets))
    response = "\n".join(lines)
    if priority == "HIGH":
        recommendation = recommend_first_ticket(filtered_tickets)
        response += _recommendation_section(recommendation.get("reason"))
    return response


def _execute_tickets_by_employee_and_priority(arguments: Dict[str, Any]) -> str:
    employee_name = _employee_argument(arguments)
    priority = _priority_argument(arguments)
    if not employee_name:
        return "Quel employé voulez-vous consulter ?"
    if not priority:
        return "Quelle priorité voulez-vous consulter ?"

    result = _tickets_or_error()
    if not result["ok"]:
        return result["message"]

    employee_tickets = _filter_by_employee(result["tickets"], employee_name)
    filtered_tickets = _sorted_by_recent(_filter_by_priority(employee_tickets, priority))
    print("FILTERED COUNT:", len(filtered_tickets))
    if not filtered_tickets:
        return f"Aucun ticket {priority} trouvé pour {employee_name}."

    lines = [f"Tickets {priority} de {employee_name} :", ""]
    lines.extend(_limit_lines(filtered_tickets))
    return "\n".join(lines)


def _execute_last_ticket_employee_by_priority(arguments: Dict[str, Any]) -> str:
    employee_name = _employee_argument(arguments)
    priority = _priority_argument(arguments)
    if not employee_name:
        return "Quel employé voulez-vous consulter ?"
    if not priority:
        return "Quelle priorité voulez-vous consulter ?"

    result = _tickets_or_error()
    if not result["ok"]:
        return result["message"]

    employee_tickets = _filter_by_employee(result["tickets"], employee_name)
    filtered_tickets = _sorted_by_recent(_filter_by_priority(employee_tickets, priority))
    print("FILTERED COUNT:", len(filtered_tickets))
    if not filtered_tickets:
        return f"Aucun ticket {priority} trouvé pour {employee_name}."

    ticket = filtered_tickets[0]
    return (
        f"Dernier ticket {priority} de {employee_name} :\n"
        f"Code : {get_ticket_code(ticket)}\n"
        f"Sujet : {get_ticket_subject(ticket)}\n"
        f"Statut : {_status(ticket) or 'Non renseigné'}\n"
        f"Date : {_date_text(ticket)}"
    )


def _execute_employee_open_tickets_count(arguments: Dict[str, Any]) -> str:
    employee_name = _employee_argument(arguments)
    if not employee_name:
        return "Quel employé voulez-vous consulter ?"

    result = _tickets_or_error()
    if not result["ok"]:
        return result["message"]

    employee_tickets = _filter_by_employee(result["tickets"], employee_name)
    filtered_tickets = [ticket for ticket in employee_tickets if _status(ticket) == "OPEN"]
    print("FILTERED COUNT:", len(filtered_tickets))
    load = get_employee_ticket_load(result["tickets"], employee_name)
    recommendation = _recommendation_section(recommend_employee_load(employee_name, load))
    if not filtered_tickets:
        return f"{employee_name} n’a aucun ticket ouvert." + recommendation

    return f"{employee_name} a {len(filtered_tickets)} ticket(s) ouverts." + recommendation


def _execute_recent_tickets_employee(arguments: Dict[str, Any]) -> str:
    employee_name = _employee_argument(arguments)
    if not employee_name:
        return "Quel employé voulez-vous consulter ?"

    try:
        limit = int(arguments.get("limit") or 5)
    except (TypeError, ValueError):
        limit = 5
    limit = max(1, min(limit, 10))

    result = _tickets_or_error()
    if not result["ok"]:
        return result["message"]

    filtered_tickets = _sorted_by_recent(_filter_by_employee(result["tickets"], employee_name))
    print("FILTERED COUNT:", len(filtered_tickets))
    if not filtered_tickets:
        return f"Aucun ticket récent trouvé pour {employee_name}."

    lines = [f"Tickets récents de {employee_name} :", ""]
    lines.extend(_limit_lines(filtered_tickets, limit=limit))
    load = get_employee_ticket_load(result["tickets"], employee_name)
    return "\n".join(lines) + _recommendation_section(recommend_employee_load(employee_name, load))


def _execute_most_recent_ticket() -> str:
    result = _tickets_or_error()
    if not result["ok"]:
        return result["message"]

    tickets = _sorted_by_recent(result["tickets"])
    print("FILTERED COUNT:", len(tickets))
    if not tickets:
        return "Aucun ticket trouvé."

    ticket = tickets[0]
    return (
        "Ticket le plus récent :\n"
        f"Code : {get_ticket_code(ticket)}\n"
        f"Sujet : {get_ticket_subject(ticket)}\n"
        f"Employé : {_employee_name(ticket)}\n"
        f"Statut : {_status(ticket) or 'Non renseigné'}\n"
        f"Priorité : {normalize_priority(ticket.get('priority')) or 'Non renseigné'}\n"
        f"Date : {_date_text(ticket)}"
    )


def _execute_search_tickets(arguments: Dict[str, Any]) -> str:
    query = _clean(arguments.get("query") or arguments.get("keyword"))
    fields = arguments.get("fields") or ["all"]
    print("SEARCH QUERY:", query)

    if not query:
        print("SEARCH RESULTS COUNT:", 0)
        return "Quel mot-clé voulez-vous chercher dans les tickets ?"

    result = _tickets_or_error()
    if not result["ok"]:
        print("SEARCH RESULTS COUNT:", 0)
        return result["message"]

    tickets = result["tickets"]
    if not tickets:
        print("SEARCH RESULTS COUNT:", 0)
        return "Aucun ticket trouvé."

    results = _sorted_by_recent(search_tickets(tickets, query, fields))
    print("SEARCH RESULTS COUNT:", len(results))
    if not results:
        return f"Aucun ticket trouvé contenant '{query}'."

    return format_search_results(results, query)


def _session_id(plan: Dict[str, Any]) -> str:
    return _clean(plan.get("_session_id"))


def _response_ticket(response: Any) -> Dict[str, Any]:
    if isinstance(response, dict):
        data = response.get("data")
        if isinstance(data, dict):
            return data
        return response
    return {}


def _laravel_error_message(error: php_api_client.SmartHRApiError) -> str:
    if error.status_code == 401:
        return "token Laravel invalide"
    details = _clean(error.details)
    return details or error.message


def _confirmed_pending(plan: Dict[str, Any], action_name: str) -> Dict[str, Any] | None:
    if not plan.get("_confirmed"):
        return None
    session_id = _session_id(plan)
    pending = get_pending_state(session_id) if session_id else None
    if pending and pending.get("pending_action") == action_name:
        return pending
    return None


def _set_ticket_pending(session_id: str, action_name: str, slots: Dict[str, Any]) -> None:
    if not session_id:
        return
    set_pending_state(
        session_id,
        {
            "tool_name": "ticket",
            "pending_action": action_name,
            "pending_slots": slots,
            "awaiting_confirmation": True,
        },
    )


def _normalize_ticket_status_or_error(status: Any) -> tuple[str, str | None]:
    normalized_status = normalize_status(status)
    if normalized_status not in VALID_TICKET_STATUSES or not to_laravel_ticket_status(status):
        return "", "Statut invalide. Utilisez : new, open, reopen, onhold, closed, inprogress, cancelled, completed."
    return normalized_status, None


def _normalize_ticket_priority_or_error(priority: Any) -> tuple[str, str | None]:
    normalized_priority = normalize_priority(priority or "MEDIUM")
    if normalized_priority not in VALID_TICKET_PRIORITIES:
        return "", "Priorité invalide. Utilisez HIGH, MEDIUM ou LOW."
    return normalized_priority, None


def _execute_confirmed_create_ticket(plan: Dict[str, Any]) -> str:
    session_id = _session_id(plan)
    pending = _confirmed_pending(plan, CREATE_TICKET)
    if not pending:
        return "Aucune création de ticket en attente."

    slots = pending.get("pending_slots") or {}
    payload = slots.get("payload") or {}
    try:
        response = create_ticket_backend(payload)
        clear_pending_state(session_id)
    except php_api_client.SmartHRApiError as error:
        clear_pending_state(session_id)
        return f"Impossible de créer le ticket : {_laravel_error_message(error)}"
    except Exception as error:
        clear_pending_state(session_id)
        return f"Impossible de créer le ticket : {error}"

    ticket = _response_ticket(response)
    ticket_code = get_ticket_code(ticket)
    employee_display_name = slots.get("employee_display_name") or slots.get("employee_name")
    recommendation_ticket = dict(ticket)
    if employee_display_name and "employee_name" not in recommendation_ticket:
        recommendation_ticket["employee_name"] = employee_display_name
    if slots.get("priority") and "priority" not in recommendation_ticket:
        recommendation_ticket["priority"] = slots.get("priority")
    if slots.get("status") and "status" not in recommendation_ticket:
        recommendation_ticket["status"] = slots.get("status")
    recommendation = _employee_load_recommendation(employee_display_name, recommendation_ticket)

    if ticket_code and ticket_code != "TKT-N/A":
        message = (
            "Ticket créé avec succès.\n"
            f"Code : {ticket_code}\n"
            f"Sujet : {get_ticket_subject(ticket)}\n"
            f"Employé : {employee_display_name}\n"
            f"Priorité : {normalize_priority(ticket.get('priority') or slots.get('priority'))}\n"
            f"Statut : {normalize_status(ticket.get('status') or slots.get('status'))}"
        )
        return message + _recommendation_section(recommendation)
    return "Ticket créé avec succès." + _recommendation_section(recommendation)


def _execute_create_ticket(plan: Dict[str, Any]) -> str:
    if plan.get("_confirmed"):
        return _execute_confirmed_create_ticket(plan)

    arguments = plan.get("arguments") or plan
    session_id = _session_id(plan)
    employee_name = _employee_argument(arguments)
    subject = _clean(arguments.get("subject") or arguments.get("title") or arguments.get("description"))
    description = _clean(arguments.get("description")) or subject
    status = normalize_status(arguments.get("status") or "OPEN")
    priority, priority_error = _normalize_ticket_priority_or_error(arguments.get("priority") or "MEDIUM")

    if not employee_name:
        return "Pour quel employé voulez-vous créer ce ticket ?"
    if not subject:
        return "Quel est le sujet du ticket ?"
    if priority_error:
        return priority_error

    status, status_error = _normalize_ticket_status_or_error(status)
    if status_error:
        return status_error

    employee_result = resolve_employee_for_ticket(employee_name)
    if employee_result.get("status") == "multiple":
        return employee_result.get("message") or "J’ai trouvé plusieurs employés avec ce nom. Pouvez-vous préciser ?"
    if employee_result.get("status") != "found":
        return "Employé introuvable."
    if not employee_result.get("user_id"):
        return "Employé introuvable."

    payload = {
        "subject": subject,
        "description": description,
        "priority": priority.lower(),
        "status": to_laravel_ticket_status(status),
        "user_id": employee_result.get("user_id"),
    }
    slots = {
        "employee_name": employee_name,
        "employee_display_name": employee_result.get("employee_name") or employee_name,
        "subject": subject,
        "description": description,
        "priority": priority,
        "status": status,
        "payload": {key: value for key, value in payload.items() if value not in (None, "")},
    }
    _set_ticket_pending(session_id, CREATE_TICKET, slots)
    return (
        "Confirmez-vous la création du ticket ?\n"
        f"Employé : {slots['employee_display_name']}\n"
        f"Sujet : {subject}\n"
        f"Priorité : {priority}\n"
        f"Statut : {status}"
    )


def _execute_confirmed_update_ticket_status(plan: Dict[str, Any]) -> str:
    session_id = _session_id(plan)
    pending = _confirmed_pending(plan, UPDATE_TICKET_STATUS)
    if not pending:
        return "Aucune modification de statut en attente."

    slots = pending.get("pending_slots") or {}
    ticket_code = slots.get("ticket_code")
    status = slots.get("status")
    try:
        update_ticket_status_backend(ticket_code, status)
        clear_pending_state(session_id)
    except php_api_client.SmartHRApiError as error:
        clear_pending_state(session_id)
        return f"Impossible de modifier le statut : {_laravel_error_message(error)}"
    except Exception as error:
        clear_pending_state(session_id)
        return f"Impossible de modifier le statut : {error}"

    return f"Statut du ticket {ticket_code} modifié avec succès.\nNouveau statut : {status}"


def _execute_update_ticket_status(plan: Dict[str, Any]) -> str:
    if plan.get("_confirmed"):
        return _execute_confirmed_update_ticket_status(plan)

    arguments = plan.get("arguments") or plan
    session_id = _session_id(plan)
    ticket_code = _clean(arguments.get("ticket_code") or arguments.get("code") or arguments.get("ticket_id"))
    status = _clean(arguments.get("status"))

    if not ticket_code:
        return "Quel est le code du ticket ?"
    if not status:
        return "Quel nouveau statut voulez-vous appliquer ?"

    print("REQUESTED TICKET CODE:", ticket_code)
    status, status_error = _normalize_ticket_status_or_error(status)
    if status_error:
        return status_error

    try:
        ticket = find_ticket_by_code(ticket_code)
    except php_api_client.SmartHRApiError as error:
        return f"Impossible de modifier le statut : {_laravel_error_message(error)}"
    except ValueError as error:
        return str(error)
    if not ticket:
        return _ticket_not_found_message(ticket_code)

    display_code = get_ticket_code(ticket)
    print("MATCHED TICKET CODE:", display_code)
    if not _ticket_requested_matches_found(ticket_code, display_code):
        return "Le ticket trouvé ne correspond pas au ticket demandé. Action annulée."

    slots = {"ticket_code": display_code, "requested_ticket_code": ticket_code, "status": status}
    _set_ticket_pending(session_id, UPDATE_TICKET_STATUS, slots)
    return (
        "Confirmez-vous le changement de statut ?\n"
        f"Ticket demandé : {_ticket_display_code(ticket_code)}\n"
        f"Ticket trouvé : {_ticket_display_code(display_code)}\n"
        f"Nouveau statut : {status}"
    )


def _execute_confirmed_assign_ticket(plan: Dict[str, Any]) -> str:
    session_id = _session_id(plan)
    pending = _confirmed_pending(plan, ASSIGN_TICKET)
    if not pending:
        return "Aucune assignation de ticket en attente."

    slots = pending.get("pending_slots") or {}
    ticket_code = slots.get("ticket_code")
    employee_name = slots.get("employee_name")
    try:
        assign_ticket_backend(ticket_code, employee_name)
        clear_pending_state(session_id)
    except php_api_client.SmartHRApiError as error:
        clear_pending_state(session_id)
        return f"Impossible d’assigner le ticket : {_laravel_error_message(error)}"
    except Exception as error:
        clear_pending_state(session_id)
        return f"Impossible d’assigner le ticket : {error}"

    employee_display_name = slots.get("employee_display_name") or employee_name
    message = f"Ticket {ticket_code} assigné avec succès à {employee_display_name}."
    return message + _recommendation_section(_employee_load_recommendation(employee_display_name))


def _execute_assign_ticket(plan: Dict[str, Any]) -> str:
    if plan.get("_confirmed"):
        return _execute_confirmed_assign_ticket(plan)

    arguments = plan.get("arguments") or plan
    session_id = _session_id(plan)
    ticket_code = _clean(arguments.get("ticket_code") or arguments.get("code") or arguments.get("ticket_id"))
    employee_name = _employee_argument(arguments)

    if not ticket_code:
        return "Quel est le code du ticket ?"
    if not employee_name:
        return "À quel employé voulez-vous assigner ce ticket ?"

    print("REQUESTED TICKET CODE:", ticket_code)
    try:
        ticket = find_ticket_by_code(ticket_code)
    except php_api_client.SmartHRApiError as error:
        return f"Impossible d’assigner le ticket : {_laravel_error_message(error)}"
    except ValueError as error:
        return str(error)
    if not ticket:
        return _ticket_not_found_message(ticket_code)

    employee_result = resolve_employee_for_ticket(employee_name)
    if employee_result.get("status") == "multiple":
        return employee_result.get("message") or "J’ai trouvé plusieurs employés avec ce nom. Pouvez-vous préciser ?"
    if employee_result.get("status") != "found":
        return "Employé introuvable."
    if not employee_result.get("user_id"):
        return "Employé introuvable."

    display_code = get_ticket_code(ticket)
    print("MATCHED TICKET CODE:", display_code)
    if not _ticket_requested_matches_found(ticket_code, display_code):
        return "Le ticket trouvé ne correspond pas au ticket demandé. Action annulée."

    slots = {
        "ticket_code": display_code,
        "requested_ticket_code": ticket_code,
        "employee_name": employee_name,
        "employee_display_name": employee_result.get("employee_name") or employee_name,
    }
    _set_ticket_pending(session_id, ASSIGN_TICKET, slots)
    return (
        "Confirmez-vous l’assignation du ticket ?\n"
        f"Ticket demandé : {_ticket_display_code(ticket_code)}\n"
        f"Ticket trouvé : {_ticket_display_code(display_code)}\n"
        f"Employé : {slots['employee_display_name']}"
    )


def _execute_tickets_by_employee(arguments: Dict[str, Any]) -> str:
    employee_name = _clean(arguments.get("employee_name"))
    if not employee_name:
        return "Quel employé voulez-vous consulter ?"

    result = _tickets_or_error()
    if not result["ok"]:
        return result["message"]

    tickets = [ticket for ticket in result["tickets"] if _employee_matches(ticket, employee_name)]
    if not tickets:
        return f"Aucun ticket trouvé pour {employee_name}."

    lines = [f"Tickets de {employee_name} : {len(tickets)} ticket(s)."]
    for index, ticket in enumerate(tickets, start=1):
        lines.append(_ticket_line(ticket, index))
    return "\n".join(lines)


def _execute_tickets_by_employee_list(arguments: Dict[str, Any]) -> str:
    employee_name = _clean(arguments.get("employee_name"))
    if not employee_name:
        return "Quel employé voulez-vous consulter ?"

    result = _tickets_or_error()
    if not result["ok"]:
        return result["message"]

    tickets = [ticket for ticket in result["tickets"] if _employee_matches(ticket, employee_name)]
    if not tickets:
        return "Aucun ticket trouvé pour cet employé"

    display_name = _employee_name(tickets[0]) or employee_name
    tickets = sorted(tickets, key=_created_at, reverse=True)
    lines = [f"Tickets de {display_name} :"]
    for index, ticket in enumerate(tickets, start=1):
        lines.append(_employee_ticket_line(ticket, index))
    return "\n".join(lines)


def _execute_last_ticket_employee(arguments: Dict[str, Any]) -> str:
    employee_name = _clean(arguments.get("employee_name"))
    if not employee_name:
        return "Quel employé voulez-vous consulter ?"

    result = _tickets_or_error()
    if not result["ok"]:
        return result["message"]

    tickets = [ticket for ticket in result["tickets"] if _employee_matches(ticket, employee_name)]
    if not tickets:
        return f"Aucun ticket trouvé pour {employee_name}."

    ticket = sorted(tickets, key=_created_at, reverse=True)[0]
    return (
        f"Dernier ticket de {employee_name} :\n"
        f"Titre : {_title(ticket)}\n"
        f"Status : {_status(ticket) or 'Non renseigné'}\n"
        f"Priorité : {_clean(ticket.get('priority')) or 'Non renseigné'}\n"
        f"Créé le : {_clean(ticket.get('created_at')) or 'Non renseigné'}"
    )


def _execute_last_ticket_date_employee(arguments: Dict[str, Any]) -> str:
    employee_name = _clean(arguments.get("employee_name"))
    if not employee_name:
        return "Quel employé voulez-vous consulter ?"

    result = _tickets_or_error()
    if not result["ok"]:
        return result["message"]

    tickets = [ticket for ticket in result["tickets"] if _employee_matches(ticket, employee_name)]
    if not tickets:
        return "Aucun ticket trouvé pour cet employé"

    ticket = sorted(tickets, key=_created_at, reverse=True)[0]
    display_name = _employee_name(ticket) or employee_name
    return f"Dernier ticket de {display_name} :\nDate : {_date_text(ticket)}"


def _execute_open_tickets_list() -> str:
    result = _tickets_or_error()
    if not result["ok"]:
        return result["message"]

    tickets = [ticket for ticket in result["tickets"] if _status(ticket) in {"OPEN", "NEW"}]
    if not tickets:
        return "Aucun ticket ouvert."

    lines = ["Tickets ouverts :"]
    for index, ticket in enumerate(tickets, start=1):
        lines.append(_ticket_line(ticket, index))
    return "\n".join(lines)


def _count_tickets_between(start: date, end: date) -> Dict[str, Any]:
    result = _tickets_or_error()
    if not result["ok"]:
        return result

    tickets = [
        ticket
        for ticket in result["tickets"]
        if _created_date(ticket) is not None and start <= _created_date(ticket) <= end
    ]
    return {"ok": True, "tickets": tickets}


def _execute_tickets_today() -> str:
    today = date.today()
    result = _count_tickets_between(today, today)
    if not result["ok"]:
        return result["message"]
    return f"Tickets aujourd’hui :\n{len(result['tickets'])} ticket(s)"


def _execute_tickets_week() -> str:
    start, end = _week_range(date.today())
    result = _count_tickets_between(start, end)
    if not result["ok"]:
        return result["message"]
    return f"Tickets cette semaine :\n{len(result['tickets'])} ticket(s)"


def _execute_tickets_month() -> str:
    start, end = _month_range(date.today())
    result = _count_tickets_between(start, end)
    if not result["ok"]:
        return result["message"]
    return f"Tickets ce mois :\n{len(result['tickets'])} ticket(s)"


def execute_ticket_tool(plan: Dict[str, Any]) -> str:
    action_name = plan.get("action_name") or plan.get("intent")
    raw_arguments = plan.get("arguments")
    arguments = raw_arguments if isinstance(raw_arguments, dict) else plan

    print("TICKET INTENT:", action_name)
    print("TICKET PARAMS:", arguments)

    if action_name == TICKETS_COUNT_BY_STATUS:
        return _execute_count_by_status(arguments)
    if action_name == TICKETS_COUNT_OPEN:
        return _execute_tickets_count_open()
    if action_name == TICKETS_COUNT_BY_PRIORITY:
        return _execute_count_by_priority(arguments)
    if action_name == TICKETS_BY_EMPLOYEE:
        return _execute_tickets_by_employee(arguments)
    if action_name == TICKETS_BY_EMPLOYEE_LIST:
        return _execute_tickets_by_employee_list(arguments)
    if action_name == LAST_TICKET_EMPLOYEE:
        return _execute_last_ticket_employee(arguments)
    if action_name == LAST_TICKET_DATE_EMPLOYEE:
        return _execute_last_ticket_date_employee(arguments)
    if action_name == OPEN_TICKETS_LIST:
        return _execute_open_tickets_list()
    if action_name == TICKETS_TODAY:
        return _execute_tickets_today()
    if action_name == TICKETS_WEEK:
        return _execute_tickets_week()
    if action_name in {TICKETS_MONTH, TICKETS_COUNT_MONTH}:
        return _execute_tickets_month()
    if action_name == EMPLOYEE_MOST_TICKETS:
        return _execute_employee_most_tickets()
    if action_name == EMPLOYEE_CREATED_MOST_TICKETS:
        return _execute_employee_created_most_tickets()
    if action_name == TICKETS_BY_STATUS_STATS:
        return _execute_tickets_by_status_stats()
    if action_name == TICKETS_BY_PRIORITY_STATS:
        return _execute_tickets_by_priority_stats()
    if action_name == TICKETS_LIST_BY_PRIORITY:
        return _execute_tickets_list_by_priority(arguments)
    if action_name == TICKETS_BY_EMPLOYEE_AND_PRIORITY:
        return _execute_tickets_by_employee_and_priority(arguments)
    if action_name == LAST_TICKET_EMPLOYEE_BY_PRIORITY:
        return _execute_last_ticket_employee_by_priority(arguments)
    if action_name == EMPLOYEE_OPEN_TICKETS_COUNT:
        return _execute_employee_open_tickets_count(arguments)
    if action_name == RECENT_TICKETS_EMPLOYEE:
        return _execute_recent_tickets_employee(arguments)
    if action_name == MOST_RECENT_TICKET:
        return _execute_most_recent_ticket()
    if action_name == SEARCH_TICKETS:
        return _execute_search_tickets(arguments)
    if action_name == CREATE_TICKET:
        return _execute_create_ticket(plan)
    if action_name == UPDATE_TICKET_STATUS:
        return _execute_update_ticket_status(plan)
    if action_name == ASSIGN_TICKET:
        return _execute_assign_ticket(plan)

    return "Cette action ticket n’est pas encore activée."
