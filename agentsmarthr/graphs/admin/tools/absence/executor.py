from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from clients import absence_api_client, employee_api_client, php_api_client


ABSENCES_TODAY = "absences_today"
ABSENCES_TODAY_BY_DEPARTMENT = "absences_today_by_department"
EMPLOYEE_ABSENCE_DAYS = "employee_absence_days"
ABSENCES_BETWEEN_DATES = "absences_between_dates"
ABSENCES_MONTH_BY_DEPARTMENT = "absences_month_by_department"
TOP_ABSENT_EMPLOYEES = "top_absent_employees"
TOTAL_ABSENCES_TODAY = "total_absences_today"
TOTAL_ABSENCE_DAYS_MONTH = "total_absence_days_month"
ABSENCES_BY_DEPARTMENT = "absences_by_department"
ABSENCE_ANOMALIES_MONTH = "absence_anomalies_month"
ABSENCE_ACTIONS = {
    ABSENCES_TODAY,
    ABSENCES_TODAY_BY_DEPARTMENT,
    EMPLOYEE_ABSENCE_DAYS,
    ABSENCES_BETWEEN_DATES,
    ABSENCES_MONTH_BY_DEPARTMENT,
    TOP_ABSENT_EMPLOYEES,
    TOTAL_ABSENCES_TODAY,
    TOTAL_ABSENCE_DAYS_MONTH,
    ABSENCES_BY_DEPARTMENT,
    ABSENCE_ANOMALIES_MONTH,
}


def _clean(value: Any) -> str:
    return str(value).strip() if value not in (None, "") else ""


def _parse_date(value: str) -> Optional[date]:
    value = _clean(value)
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _date_text(value: date) -> str:
    return value.isoformat()


def _week_range(today: date) -> Tuple[date, date]:
    start = today - timedelta(days=today.weekday())
    return start, start + timedelta(days=6)


def _month_range(today: date) -> Tuple[date, date]:
    start = today.replace(day=1)
    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)
    return start, next_month - timedelta(days=1)


def _absence_employee_name(absence: Dict[str, Any]) -> str:
    return _clean(absence.get("employee_name")) or _clean(absence.get("full_name")) or "Employé"


def _absence_department(absence: Dict[str, Any]) -> str:
    return _clean(absence.get("department")) or "Non renseigné"


def _department_aliases(department_name: str) -> set[str]:
    value = _clean(department_name).lower()
    aliases = {value}

    if value in {"rh", "hr", "human resources", "ressources humaines"}:
        aliases.update({"rh", "hr", "human resources", "ressources humaines"})
    if value in {"it", "informatique", "it department"}:
        aliases.update({"it", "informatique", "it department"})
    if value in {"finance", "financial"}:
        aliases.update({"finance", "financial"})
    if value in {"customer support", "support", "support client"}:
        aliases.update({"customer support", "support", "support client"})

    return aliases


def _department_matches(absence: Dict[str, Any], department_name: str) -> bool:
    department = _absence_department(absence).lower()
    return any(alias and alias in department for alias in _department_aliases(department_name))


def _absence_reason(absence: Dict[str, Any]) -> str:
    return _clean(absence.get("reason")) or _clean(absence.get("status")) or "Absence"


def _absence_days(absence: Dict[str, Any]) -> int:
    days_count = absence.get("days_count")
    if isinstance(days_count, (int, float)):
        return int(days_count)
    if isinstance(days_count, str) and days_count.isdigit():
        return int(days_count)

    start = _parse_date(_clean(absence.get("start_date")))
    end = _parse_date(_clean(absence.get("end_date")))
    if start and end:
        return max((end - start).days + 1, 1)
    return 1


def _absence_dates(absence: Dict[str, Any]) -> str:
    start = _clean(absence.get("start_date"))
    end = _clean(absence.get("end_date"))
    if start and end and start != end:
        return f"{start} à {end}"
    return start or end or "date inconnue"


def _find_employee(employee_name: str) -> Dict[str, Any]:
    result = employee_api_client.find_employee_by_name(employee_name, use_search=True)
    status = result.get("status")
    if status == "not_found":
        return {"ok": False, "message": f"Employé introuvable : {employee_name}"}
    if status == "multiple":
        return {"ok": False, "message": employee_api_client.MULTIPLE_EMPLOYEES_MESSAGE}
    if status != "found":
        return {"ok": False, "message": "Je n’ai pas pu trouver cet employé."}

    employee = result.get("employee") or {}
    employee_id = employee.get("id") or employee.get("employee_id")
    if not employee_id:
        return {"ok": False, "message": "Je n’ai pas trouvé l’identifiant Laravel de cet employé."}

    return {"ok": True, "employee": employee, "employee_id": employee_id}


def _list_absences_or_error(**kwargs: Any) -> Dict[str, Any]:
    try:
        return {"ok": True, "absences": absence_api_client.list_absences(**kwargs)}
    except php_api_client.SmartHRApiError as error:
        if error.status_code == 401:
            return {"ok": False, "message": "Laravel a refusé la demande d’absence : token invalide."}
        return {"ok": False, "message": f"Laravel a refusé la demande d’absence : {error.message}"}


def _execute_absences_today() -> str:
    today = date.today()
    result = _list_absences_or_error(start_date=_date_text(today), end_date=_date_text(today))
    if not result["ok"]:
        return result["message"]

    absences = result["absences"]
    if not absences:
        return "Aucun employé absent aujourd’hui."

    lines = ["Absents aujourd’hui :"]
    for index, absence in enumerate(absences, start=1):
        lines.append(
            f"{index}. {_absence_employee_name(absence)} — {_absence_department(absence)} — {_absence_reason(absence)}"
        )
    return "\n".join(lines)


def _execute_absences_today_by_department(arguments: Dict[str, Any]) -> str:
    department_name = _clean(arguments.get("department") or arguments.get("department_name"))
    if not department_name:
        return "Quel département voulez-vous consulter ?"

    today = date.today()
    result = _list_absences_or_error(start_date=_date_text(today), end_date=_date_text(today))
    if not result["ok"]:
        return result["message"]

    absences = [
        absence
        for absence in result["absences"]
        if _department_matches(absence, department_name)
    ]
    if not absences:
        return f"Aucun employé absent aujourd’hui dans {department_name}."

    lines = [f"Absents aujourd’hui dans {department_name} :"]
    for index, absence in enumerate(absences, start=1):
        lines.append(f"{index}. {_absence_employee_name(absence)} — {_absence_reason(absence)}")
    return "\n".join(lines)


def _execute_employee_absence_days(arguments: Dict[str, Any]) -> str:
    employee_name = _clean(arguments.get("employee_name"))
    period = _clean(arguments.get("period")).lower()
    if not employee_name:
        return "Quel employé voulez-vous analyser ?"
    if period not in {"week", "month"}:
        return "Quelle période voulez-vous analyser : cette semaine ou ce mois ?"

    employee_result = _find_employee(employee_name)
    if not employee_result["ok"]:
        return employee_result["message"]

    today = date.today()
    start, end = _week_range(today) if period == "week" else _month_range(today)
    result = _list_absences_or_error(
        employee_id=employee_result["employee_id"],
        start_date=_date_text(start),
        end_date=_date_text(end),
    )
    if not result["ok"]:
        return result["message"]

    absences = result["absences"]
    display_name = employee_api_client.get_employee_field(employee_result["employee"], "full_name") or employee_name
    period_label = "cette semaine" if period == "week" else "ce mois"
    total_days = sum(_absence_days(absence) for absence in absences)

    if not absences:
        return f"{display_name} est absent 0 jour(s) {period_label}."

    lines = [f"{display_name} est absent {total_days} jour(s) {period_label}."]
    lines.append("Détails :")
    for absence in absences:
        lines.append(f"- {_absence_dates(absence)} : {_absence_reason(absence)}")
    return "\n".join(lines)


def _execute_absences_between_dates(arguments: Dict[str, Any]) -> str:
    start = _parse_date(_clean(arguments.get("start_date")))
    end = _parse_date(_clean(arguments.get("end_date")))
    if not start or not end:
        return "Date invalide. Utilisez YYYY-MM-DD ou DD/MM/YYYY."
    if end < start:
        return "Date invalide : la date de fin doit être après la date de début."

    result = _list_absences_or_error(start_date=_date_text(start), end_date=_date_text(end))
    if not result["ok"]:
        return result["message"]

    absences = result["absences"]
    if not absences:
        return f"Aucune absence trouvée entre {_date_text(start)} et {_date_text(end)}."

    grouped: Dict[str, int] = defaultdict(int)
    for absence in absences:
        grouped[_absence_employee_name(absence)] += _absence_days(absence)

    lines = [f"Absences entre {_date_text(start)} et {_date_text(end)} :"]
    for employee_name in sorted(grouped):
        lines.append(f"- {employee_name} : {grouped[employee_name]} jour(s)")
    return "\n".join(lines)


def _execute_absences_month_by_department(arguments: Dict[str, Any]) -> str:
    department_name = _clean(arguments.get("department") or arguments.get("department_name"))
    if not department_name:
        return "Quel département voulez-vous consulter ?"

    result = _current_month_absences()
    if not result["ok"]:
        return result["message"]

    absences = [
        absence
        for absence in result["absences"]
        if _department_matches(absence, department_name)
    ]
    if not absences:
        return f"Aucune absence trouvée dans {department_name} ce mois."

    grouped = _days_by_employee(absences)
    lines = [f"Absences dans {department_name} ce mois :"]
    for employee_name, days in sorted(grouped.items(), key=lambda item: item[1], reverse=True):
        flag = " ⚠️" if days > 5 else ""
        lines.append(f"- {employee_name} : {days} jour(s){flag}")
    return "\n".join(lines)


def _current_month_absences() -> Dict[str, Any]:
    start, end = _month_range(date.today())
    return _list_absences_or_error(start_date=_date_text(start), end_date=_date_text(end))


def _days_by_employee(absences: List[Dict[str, Any]]) -> Dict[str, int]:
    grouped: Dict[str, int] = defaultdict(int)
    for absence in absences:
        grouped[_absence_employee_name(absence)] += _absence_days(absence)
    return grouped


def _execute_top_absent_employees() -> str:
    result = _current_month_absences()
    if not result["ok"]:
        return result["message"]

    grouped = _days_by_employee(result["absences"])
    if not grouped:
        return "Aucune absence trouvée ce mois."

    ranked = sorted(grouped.items(), key=lambda item: item[1], reverse=True)
    lines = ["Top employés absents ce mois :"]
    for index, (employee_name, days) in enumerate(ranked, start=1):
        flag = " ⚠️" if days > 5 else ""
        lines.append(f"{index}. {employee_name} : {days} jour(s){flag}")
    return "\n".join(lines)


def _execute_total_absences_today() -> str:
    today = date.today()
    result = _list_absences_or_error(start_date=_date_text(today), end_date=_date_text(today))
    if not result["ok"]:
        return result["message"]

    count = len(result["absences"])
    return f"Il y a {count} employé(s) absent(s) aujourd’hui."


def _execute_total_absence_days_month() -> str:
    result = _current_month_absences()
    if not result["ok"]:
        return result["message"]

    total_days = sum(_absence_days(absence) for absence in result["absences"])
    return f"Total des jours d’absence ce mois : {total_days} jour(s)."


def _execute_absences_by_department() -> str:
    result = _current_month_absences()
    if not result["ok"]:
        return result["message"]

    grouped: Dict[str, int] = defaultdict(int)
    for absence in result["absences"]:
        grouped[_absence_department(absence)] += _absence_days(absence)

    if not grouped:
        return "Aucune absence trouvée ce mois."

    lines = ["Absences par département ce mois :"]
    for department, days in sorted(grouped.items(), key=lambda item: item[1], reverse=True):
        lines.append(f"- {department} : {days} jour(s)")
    return "\n".join(lines)


def _execute_absence_anomalies_month() -> str:
    result = _current_month_absences()
    if not result["ok"]:
        return result["message"]

    grouped = _days_by_employee(result["absences"])
    anomalies = sorted(
        [(employee_name, days) for employee_name, days in grouped.items() if days > 5],
        key=lambda item: item[1],
        reverse=True,
    )

    if not anomalies:
        return "Aucune anomalie d’absence ce mois."

    lines = ["Anomalies d’absence ce mois :"]
    for employee_name, days in anomalies:
        lines.append(f"- ⚠️ {employee_name} : {days} jour(s)")
    return "\n".join(lines)


def execute_absence_tool(plan: Dict[str, Any]) -> str:
    action_name = plan.get("action_name") or plan.get("intent")
    arguments = plan.get("arguments") or plan
    print("INTENT:", action_name)
    print("PARAMS:", arguments)

    if action_name == ABSENCES_TODAY:
        return _execute_absences_today()
    if action_name == ABSENCES_TODAY_BY_DEPARTMENT:
        return _execute_absences_today_by_department(arguments)
    if action_name == EMPLOYEE_ABSENCE_DAYS:
        return _execute_employee_absence_days(arguments)
    if action_name == ABSENCES_BETWEEN_DATES:
        return _execute_absences_between_dates(arguments)
    if action_name == ABSENCES_MONTH_BY_DEPARTMENT:
        return _execute_absences_month_by_department(arguments)
    if action_name == TOP_ABSENT_EMPLOYEES:
        return _execute_top_absent_employees()
    if action_name == TOTAL_ABSENCES_TODAY:
        return _execute_total_absences_today()
    if action_name == TOTAL_ABSENCE_DAYS_MONTH:
        return _execute_total_absence_days_month()
    if action_name == ABSENCES_BY_DEPARTMENT:
        return _execute_absences_by_department()
    if action_name == ABSENCE_ANOMALIES_MONTH:
        return _execute_absence_anomalies_month()

    return "Cette action absence n’est pas encore activée."
