import json
import logging
import time
from typing import Any, Dict

import httpx

logger = logging.getLogger(__name__)

from config import OPENROUTER_API_KEY, OPENROUTER_MODEL
from graphs.admin.tools.absence.prompts import ABSENCE_PROMPT
from graphs.admin.tools.employees.prompts import EMPLOYEES_PROMPT
from graphs.admin.tools.ticket.prompts import TICKET_PROMPT
from tools.projects.prompt import PROJECTS_PROMPT


OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_ERROR_MESSAGE = "Erreur OpenRouter : impossible de comprendre la demande."

_ROUTING_HEADER = '''
You are a smart HR assistant router. For every user message, pick EXACTLY ONE tool and return valid JSON.

Routing rules — choose the tool based on the topic:
- employees : anything about an employee's info, phone, email, department, designation, status, address, create/update/delete employee, employee count, employee list.
- absence   : anything about absences, absent employees, absence days, absence periods.
- ticket    : anything about tickets, TKT codes, ticket status, ticket priority, create/update/assign ticket.
- projects  : anything about projects, deadlines, project team, project leader, project priority.

Never mix tools. Return ONLY valid JSON — no markdown, no explanation.

'''

PLANNER_PROMPT = _ROUTING_HEADER + EMPLOYEES_PROMPT + "\n\n" + ABSENCE_PROMPT + "\n\n" + TICKET_PROMPT + "\n\n" + PROJECTS_PROMPT


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
        "max_tokens": 512,
        "messages": [
            {"role": "system", "content": PLANNER_PROMPT},
            {"role": "user", "content": user_message},
        ],
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = None
    for attempt in range(2):
        try:
            response = httpx.post(OPENROUTER_ENDPOINT, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            break
        except httpx.HTTPStatusError as error:
            logger.error(
                "OpenRouter HTTP %s — key_set=%s model=%s body=%.200s",
                error.response.status_code,
                bool(OPENROUTER_API_KEY),
                OPENROUTER_MODEL,
                error.response.text,
            )
            if attempt == 0 and error.response.status_code == 429:
                time.sleep(1.5)
                continue
            return _error_plan()  # 401/402/4xx: no point retrying
        except (httpx.HTTPError, ValueError) as error:
            logger.error("OpenRouter request failed — %s: %s", type(error).__name__, error)
            return _error_plan()

    if data is None:
        return _error_plan()

    content = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
    # Strip markdown code fences that some models add around JSON
    stripped = content.strip()
    if stripped.startswith("```"):
        stripped = stripped.split("```", 2)[1]
        if stripped.startswith("json"):
            stripped = stripped[4:]
        stripped = stripped.rsplit("```", 1)[0].strip()
        content = stripped
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return _error_plan()

    if not isinstance(parsed, dict):
        return _error_plan()

    return parsed
