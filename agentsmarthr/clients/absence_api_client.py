from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from clients import php_api_client


def _extract_absences(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    if not isinstance(payload, dict):
        return []

    for key in ("data", "absences", "items", "results"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]

    data = payload.get("data")
    if isinstance(data, dict):
        for key in ("data", "absences", "items", "results"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]

    return []


def list_absences(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    employee_id: Optional[Any] = None,
    status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    params = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    if employee_id:
        params["employee_id"] = employee_id
    if status:
        params["status"] = status

    query = f"?{urlencode(params)}" if params else ""
    payload = php_api_client.get(f"/api/v1/absences{query}")
    return _extract_absences(payload)
