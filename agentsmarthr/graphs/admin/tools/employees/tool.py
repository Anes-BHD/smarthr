from .prompts import EMPLOYEES_PROMPT


TOOL_DEFINITION = {
    "name": "employees",
    "schema": {
        "actions": [
            "get_employee_info",
            "get_employee_full_info",
            "create_employee",
            "update_employee",
            "delete_employee",
            "employee_analytics",
        ],
    },
    "prompt": EMPLOYEES_PROMPT,
}
