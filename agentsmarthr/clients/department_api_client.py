from typing import Any, Dict, List

from clients import php_api_client


def _extract_items(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    if not isinstance(payload, dict):
        return []

    for key in ("data", "departments", "items", "results"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]

    data = payload.get("data")
    if isinstance(data, dict):
        for key in ("data", "departments", "items", "results"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]

    return []


def list_departments() -> List[Dict[str, Any]]:
    return _extract_items(php_api_client.get("/api/v1/departments"))


def find_department_by_name(name: str) -> Dict[str, Any]:
    searched_name = (name or "").strip().lower()
    if not searched_name:
        return {"status": "not_found", "department": None}

    departments = list_departments()
    exact_matches = [
        department
        for department in departments
        if str(department.get("name", "")).strip().lower() == searched_name
    ]
    if len(exact_matches) == 1:
        return {"status": "found", "department": exact_matches[0]}
    if len(exact_matches) > 1:
        return {"status": "multiple", "departments": exact_matches}

    contains_matches = [
        department
        for department in departments
        if searched_name in str(department.get("name", "")).strip().lower()
    ]
    if len(contains_matches) == 1:
        return {"status": "found", "department": contains_matches[0]}
    if len(contains_matches) > 1:
        return {"status": "multiple", "departments": contains_matches}

    return {"status": "not_found", "department": None}
