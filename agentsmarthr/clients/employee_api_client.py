from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import quote

from clients import php_api_client


MULTIPLE_EMPLOYEES_MESSAGE = "J’ai trouvé plusieurs employés avec ce nom. Pouvez-vous préciser ?"


def _extract_employees(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return [employee for employee in payload if isinstance(employee, dict)]

    if not isinstance(payload, dict):
        return []

    for key in ("data", "employees", "items", "results"):
        value = payload.get(key)
        if isinstance(value, list):
            return [employee for employee in value if isinstance(employee, dict)]

    data = payload.get("data")
    if isinstance(data, dict):
        for key in ("data", "employees", "items", "results"):
            value = data.get(key)
            if isinstance(value, list):
                return [employee for employee in value if isinstance(employee, dict)]

    return []


def _nested_dict(employee: Dict[str, Any], key: str) -> Dict[str, Any]:
    value = employee.get(key)
    return value if isinstance(value, dict) else {}


def _candidate_sources(employee: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    yield employee
    yield _nested_dict(employee, "user")
    yield _nested_dict(employee, "employee_details")
    yield _nested_dict(employee, "details")


def _first_value(employee: Dict[str, Any], keys: Iterable[str]) -> Optional[Any]:
    for source in _candidate_sources(employee):
        for key in keys:
            value = source.get(key)
            if value not in (None, ""):
                return value
    return None


def _employee_text(employee: Dict[str, Any]) -> str:
    user = _nested_dict(employee, "user")
    values = [
        _first_value(employee, ("firstname", "first_name")),
        _first_value(employee, ("lastname", "last_name")),
        _first_value(employee, ("full_name", "name")),
        _first_value(employee, ("email",)),
        user.get("firstname"),
        user.get("lastname"),
        user.get("email"),
    ]
    return " ".join(str(value).lower() for value in values if value)


def _employee_display_name(employee: Dict[str, Any]) -> str:
    full_name = _first_value(employee, ("full_name", "name"))
    if full_name:
        return str(full_name)

    firstname = _first_value(employee, ("firstname", "first_name")) or ""
    lastname = _first_value(employee, ("lastname", "last_name")) or ""
    display_name = f"{firstname} {lastname}".strip()
    return display_name or str(_first_value(employee, ("email",)) or "cet employé")


def list_employees() -> List[Dict[str, Any]]:
    payload = php_api_client.get("/api/v1/employees")
    return _extract_employees(payload)


def search_employees(name: str) -> List[Dict[str, Any]]:
    payload = php_api_client.get(f"/api/v1/employees?search={quote(name or '')}")
    return _extract_employees(payload)


def create_employee(payload: Dict[str, Any]) -> Any:
    return php_api_client.post("/api/v1/employees", json=payload)


def update_employee(employee_id: Any, payload: Dict[str, Any]) -> Any:
    return php_api_client.patch(f"/api/v1/employees/{employee_id}", json=payload)


def delete_employee(employee_id: Any) -> Any:
    return php_api_client.delete(f"/api/v1/employees/{employee_id}")


def _employee_identity_values(employee: Dict[str, Any]) -> List[str]:
    user = _nested_dict(employee, "user")
    values = [
        _first_value(employee, ("firstname", "first_name")),
        _first_value(employee, ("lastname", "last_name")),
        _first_value(employee, ("full_name", "name")),
        _first_value(employee, ("email",)),
        user.get("firstname"),
        user.get("lastname"),
        user.get("email"),
    ]
    return [str(value).strip().lower() for value in values if value]


def find_employee_by_name(name: str, use_search: bool = False) -> Dict[str, Any]:
    searched_name = (name or "").strip().lower()
    if not searched_name:
        return {"status": "missing_name", "employee": None}

    if use_search:
        employees = search_employees(name)
        # Laravel searches individual fields, so "Fatma Gharbi" finds nothing.
        # Retry with the first word and let local matching handle the full name.
        if not employees and " " in searched_name:
            employees = search_employees(searched_name.split()[0])
    else:
        employees = list_employees()
    exact_matches = [
        employee
        for employee in employees
        if searched_name in _employee_identity_values(employee)
    ]
    if len(exact_matches) == 1:
        return {"status": "found", "employee": exact_matches[0]}
    if len(exact_matches) > 1:
        return {
            "status": "multiple",
            "employees": exact_matches,
            "message": MULTIPLE_EMPLOYEES_MESSAGE,
        }

    matches = [
        employee
        for employee in employees
        if searched_name in _employee_text(employee)
    ]

    if not matches:
        return {"status": "not_found", "employee": None}

    if len(matches) > 1:
        return {
            "status": "multiple",
            "employees": matches,
            "message": MULTIPLE_EMPLOYEES_MESSAGE,
        }

    return {"status": "found", "employee": matches[0]}


def get_employee_field(employee: Dict[str, Any], field: str) -> Optional[Any]:
    field = (field or "").lower()

    if field == "phone":
        return employee.get("phone")

    if field == "email":
        return employee.get("email")

    if field == "address":
        return employee.get("address")

    if field == "firstname":
        return employee.get("firstname")

    if field == "lastname":
        return employee.get("lastname")

    if field == "full_name":
        return employee.get("full_name")

    if field == "status":
        return "Actif" if employee.get("is_active") else "Inactif"

    if field == "joining_date":
        return employee.get("joining_date") or employee.get("join_date") or employee.get("date_of_joining")

    employee_detail = employee.get("employee_detail") or {}

    if field == "designation":
        designation = employee_detail.get("designation")
        if isinstance(designation, dict):
            return designation.get("name")
        return designation

    if field == "department":
        department = employee_detail.get("department")
        if isinstance(department, dict):
            return department.get("name")
        return department

    return None
