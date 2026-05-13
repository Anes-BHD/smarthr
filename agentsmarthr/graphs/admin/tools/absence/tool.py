from .prompts import ABSENCE_PROMPT


TOOL_DEFINITION = {
    "name": "absence",
    "schema": {
        "actions": [
            "absences_today",
            "absences_today_by_department",
            "employee_absence_days",
            "absences_between_dates",
            "absences_month_by_department",
            "top_absent_employees",
            "total_absences_today",
            "total_absence_days_month",
            "absences_by_department",
            "absence_anomalies_month",
        ],
    },
    "prompt": ABSENCE_PROMPT,
}
