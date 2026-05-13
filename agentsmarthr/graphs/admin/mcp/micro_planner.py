import json
from typing import Any, Dict

import httpx

from config import OPENROUTER_API_KEY, OPENROUTER_MODEL
from graphs.admin.tools.absence.prompts import ABSENCE_PROMPT
from graphs.admin.tools.employees.prompts import EMPLOYEES_PROMPT
from graphs.admin.tools.ticket.prompts import TICKET_PROMPT
from tools.projects.prompt import PROJECTS_PROMPT


OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_ERROR_MESSAGE = "Erreur OpenRouter : impossible de comprendre la demande."
PLANNER_PROMPT = EMPLOYEES_PROMPT + "\n\n" + ABSENCE_PROMPT + "\n\n" + TICKET_PROMPT + "\n\n" + PROJECTS_PROMPT


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


def plan_employee_request(user_message: str) -> Dict[str, Any]:
    payload = {
        "model": OPENROUTER_MODEL,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": PLANNER_PROMPT},
            {"role": "user", "content": user_message},
        ],
    }

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
        data = response.json()
    except (httpx.HTTPError, ValueError):
        return _error_plan()

    content = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return _error_plan()

    if not isinstance(parsed, dict):
        return _error_plan()

    return parsed
