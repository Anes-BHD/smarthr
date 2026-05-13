ABSENCE_PROMPT = '''
Absence tool intents:

Use these actions for employee absence questions.
Return ONLY valid JSON.

Allowed absence actions:
- absences_today
- absences_today_by_department
- employee_absence_days
- absences_between_dates
- absences_month_by_department
- top_absent_employees
- total_absences_today
- total_absence_days_month
- absences_by_department
- absence_anomalies_month

Examples:
Important routing rule:
- If the user asks who is absent today AND mentions a department with "dans", use absences_today_by_department.
- Do not use absences_by_department for "aujourd’hui dans {department}".

User: qui est absent aujourd’hui ?
JSON:
{
  "handled": true,
  "tool_name": "absence",
  "action_name": "absences_today",
  "arguments": {},
  "confidence": 0.95,
  "reason": "absences today requested"
}

User: qui est absent aujourd’hui dans RH ?
JSON:
{
  "handled": true,
  "tool_name": "absence",
  "action_name": "absences_today_by_department",
  "arguments": {
    "department": "RH"
  },
  "confidence": 0.95,
  "reason": "today absences filtered by department"
}

User: liste des absents aujourd’hui dans Human Resources
JSON:
{
  "handled": true,
  "tool_name": "absence",
  "action_name": "absences_today_by_department",
  "arguments": {
    "department": "Human Resources"
  },
  "confidence": 0.95,
  "reason": "today absences filtered by department"
}

User: combien de jours Ahmed est absent cette semaine ?
JSON:
{
  "handled": true,
  "tool_name": "absence",
  "action_name": "employee_absence_days",
  "arguments": {
    "employee_name": "Ahmed",
    "period": "week"
  },
  "confidence": 0.95,
  "reason": "weekly absence count requested"
}

User: nombre de jours absent de Sarra ce mois-ci
JSON:
{
  "handled": true,
  "tool_name": "absence",
  "action_name": "employee_absence_days",
  "arguments": {
    "employee_name": "Sarra",
    "period": "month"
  },
  "confidence": 0.95,
  "reason": "monthly absence count requested"
}

User: liste des absents entre 2026-05-01 et 2026-05-10
JSON:
{
  "handled": true,
  "tool_name": "absence",
  "action_name": "absences_between_dates",
  "arguments": {
    "start_date": "2026-05-01",
    "end_date": "2026-05-10"
  },
  "confidence": 0.95,
  "reason": "absence date range requested"
}

User: absences dans IT ce mois
JSON:
{
  "handled": true,
  "tool_name": "absence",
  "action_name": "absences_month_by_department",
  "arguments": {
    "department": "IT"
  },
  "confidence": 0.95,
  "reason": "monthly absences filtered by department"
}

User: top absences
JSON:
{
  "handled": true,
  "tool_name": "absence",
  "action_name": "top_absent_employees",
  "arguments": {},
  "confidence": 0.95,
  "reason": "top absent employees requested"
}

User: combien d’absents aujourd’hui ?
JSON:
{
  "handled": true,
  "tool_name": "absence",
  "action_name": "total_absences_today",
  "arguments": {},
  "confidence": 0.95,
  "reason": "total absences today requested"
}

User: total jours absence ce mois
JSON:
{
  "handled": true,
  "tool_name": "absence",
  "action_name": "total_absence_days_month",
  "arguments": {},
  "confidence": 0.95,
  "reason": "total absence days month requested"
}

User: absences par département
JSON:
{
  "handled": true,
  "tool_name": "absence",
  "action_name": "absences_by_department",
  "arguments": {},
  "confidence": 0.95,
  "reason": "absence grouping by department requested"
}

User: anomalies absences ce mois
JSON:
{
  "handled": true,
  "tool_name": "absence",
  "action_name": "absence_anomalies_month",
  "arguments": {},
  "confidence": 0.95,
  "reason": "monthly absence anomalies requested"
}
'''
