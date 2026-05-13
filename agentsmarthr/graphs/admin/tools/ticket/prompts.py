TICKET_PROMPT = '''
Ticket tool intents:

Use these actions for ticket questions.
Return ONLY valid JSON.

Allowed ticket actions:
- tickets_count_by_status
- tickets_count_open
- tickets_count_by_priority
- tickets_by_employee
- tickets_by_employee_list
- last_ticket_employee
- last_ticket_date_employee
- open_tickets_list
- tickets_today
- tickets_week
- tickets_month
- tickets_count_month
- employee_most_tickets
- employee_created_most_tickets
- tickets_by_status_stats
- tickets_by_priority_stats
- tickets_list_by_priority
- tickets_by_employee_and_priority
- last_ticket_employee_by_priority
- employee_open_tickets_count
- recent_tickets_employee
- most_recent_ticket
- search_tickets
- create_ticket
- update_ticket_status
- assign_ticket

Rules:
- If the phrase contains "liste", return a list intent.
- If the phrase contains "combien", return a count intent.
- Extract employee_name when present.
- Existing ticket intents have priority over search_tickets:
  tickets HIGH, tickets ouverts, tickets de Ahmed, dernier ticket de Ahmed,
  tickets ce mois, tickets par statut, tickets par priorité.
- Use search_tickets only for textual search in ticket content.
- For search_tickets, extract the word or phrase after:
  cherche, recherche, trouve, contenant, avec sujet, description, parlent de.
- If the search phrase contains "sujet", set fields to ["subject"].
- If the search phrase contains "description", set fields to ["description"].
- Otherwise omit fields or set fields to ["all"].
- Priority synonyms:
  urgent, urgents, critique, critical, haute priorité => HIGH
  moyenne priorité => MEDIUM
  basse priorité => LOW

Examples:
User: combien de tickets CLOSED
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "tickets_count_by_status",
  "arguments": {
    "status": "CLOSED"
  },
  "confidence": 0.95,
  "reason": "ticket count by status requested"
}

User: combien de tickets sont ouverts ?
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "tickets_count_open",
  "arguments": {
    "status": "OPEN"
  },
  "confidence": 0.95,
  "reason": "open tickets count requested"
}

User: nombre de tickets ouverts
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "tickets_count_open",
  "arguments": {
    "status": "OPEN"
  },
  "confidence": 0.95,
  "reason": "open tickets count requested"
}

User: combien de tickets OPEN ?
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "tickets_count_open",
  "arguments": {
    "status": "OPEN"
  },
  "confidence": 0.95,
  "reason": "open tickets count requested"
}

User: combien de tickets sont en HIGH priorité ?
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "tickets_count_by_priority",
  "arguments": {
    "priority": "HIGH"
  },
  "confidence": 0.95,
  "reason": "ticket count by priority requested"
}

User: combien de tickets urgents ?
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "tickets_count_by_priority",
  "arguments": {
    "priority": "HIGH"
  },
  "confidence": 0.95,
  "reason": "urgent means high priority"
}

User: combien de tickets a Ahmed
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "tickets_by_employee",
  "arguments": {
    "employee_name": "Ahmed"
  },
  "confidence": 0.95,
  "reason": "tickets by employee requested"
}

User: liste les tickets de Ahmed
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "tickets_by_employee_list",
  "arguments": {
    "employee_name": "Ahmed"
  },
  "confidence": 0.95,
  "reason": "ticket list by employee requested"
}

User: tickets de Sarra
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "tickets_by_employee_list",
  "arguments": {
    "employee_name": "Sarra"
  },
  "confidence": 0.9,
  "reason": "ticket list by employee requested"
}

User: dernier ticket de Ahmed
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "last_ticket_employee",
  "arguments": {
    "employee_name": "Ahmed"
  },
  "confidence": 0.95,
  "reason": "last ticket by employee requested"
}

User: quelle est la date du dernier ticket de Ahmed
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "last_ticket_date_employee",
  "arguments": {
    "employee_name": "Ahmed"
  },
  "confidence": 0.95,
  "reason": "last ticket date requested"
}

User: liste des tickets ouverts
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "open_tickets_list",
  "arguments": {},
  "confidence": 0.95,
  "reason": "open tickets list requested"
}

User: tickets aujourd’hui
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "tickets_today",
  "arguments": {},
  "confidence": 0.95,
  "reason": "tickets today requested"
}

User: tickets cette semaine
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "tickets_week",
  "arguments": {},
  "confidence": 0.95,
  "reason": "tickets this week requested"
}

User: tickets ce mois
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "tickets_month",
  "arguments": {},
  "confidence": 0.95,
  "reason": "tickets this month requested"
}

User: combien de tickets ce mois
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "tickets_count_month",
  "arguments": {},
  "confidence": 0.95,
  "reason": "ticket count this month requested"
}

User: qui a le plus de tickets ?
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "employee_most_tickets",
  "arguments": {},
  "confidence": 0.95,
  "reason": "employee with most tickets requested"
}

User: quel employé crée le plus de tickets ?
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "employee_created_most_tickets",
  "arguments": {},
  "confidence": 0.95,
  "reason": "top ticket creator requested"
}

User: tickets par statut
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "tickets_by_status_stats",
  "arguments": {},
  "confidence": 0.95,
  "reason": "ticket stats by status requested"
}

User: tickets par priorité
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "tickets_by_priority_stats",
  "arguments": {},
  "confidence": 0.95,
  "reason": "ticket stats by priority requested"
}

User: liste les tickets HIGH
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "tickets_list_by_priority",
  "arguments": {
    "priority": "HIGH"
  },
  "confidence": 0.95,
  "reason": "ticket list by priority requested"
}

User: liste les tickets urgents
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "tickets_list_by_priority",
  "arguments": {
    "priority": "HIGH"
  },
  "confidence": 0.95,
  "reason": "urgent means high priority"
}

User: tickets HIGH de Ahmed
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "tickets_by_employee_and_priority",
  "arguments": {
    "employee_name": "Ahmed",
    "priority": "HIGH"
  },
  "confidence": 0.95,
  "reason": "employee tickets by priority requested"
}

User: tickets critiques Ahmed
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "tickets_by_employee_and_priority",
  "arguments": {
    "employee_name": "Ahmed",
    "priority": "HIGH"
  },
  "confidence": 0.9,
  "reason": "critical means high priority"
}

User: tickets urgents de Sarra
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "tickets_by_employee_and_priority",
  "arguments": {
    "employee_name": "Sarra",
    "priority": "HIGH"
  },
  "confidence": 0.95,
  "reason": "urgent employee tickets requested"
}

User: quel est le dernier ticket HIGH de Ahmed ?
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "last_ticket_employee_by_priority",
  "arguments": {
    "employee_name": "Ahmed",
    "priority": "HIGH"
  },
  "confidence": 0.95,
  "reason": "last employee ticket by priority requested"
}

User: dernier ticket urgent de Sarra
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "last_ticket_employee_by_priority",
  "arguments": {
    "employee_name": "Sarra",
    "priority": "HIGH"
  },
  "confidence": 0.95,
  "reason": "last urgent employee ticket requested"
}

User: combien de tickets ouverts Ahmed a ?
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "employee_open_tickets_count",
  "arguments": {
    "employee_name": "Ahmed",
    "status": "OPEN"
  },
  "confidence": 0.95,
  "reason": "employee open ticket count requested"
}

User: Ahmed a combien de tickets OPEN ?
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "employee_open_tickets_count",
  "arguments": {
    "employee_name": "Ahmed",
    "status": "OPEN"
  },
  "confidence": 0.95,
  "reason": "employee open ticket count requested"
}

User: tickets ouverts de Ahmed
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "employee_open_tickets_count",
  "arguments": {
    "employee_name": "Ahmed",
    "status": "OPEN"
  },
  "confidence": 0.9,
  "reason": "employee open ticket count requested"
}

User: tickets actifs de Ahmed
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "employee_open_tickets_count",
  "arguments": {
    "employee_name": "Ahmed",
    "status": "OPEN"
  },
  "confidence": 0.85,
  "reason": "employee active ticket load requested"
}

User: donne moi les tickets récents de Sedki
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "recent_tickets_employee",
  "arguments": {
    "employee_name": "Sedki",
    "limit": 5
  },
  "confidence": 0.95,
  "reason": "recent employee tickets requested"
}

User: quel ticket est le plus récent ?
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "most_recent_ticket",
  "arguments": {},
  "confidence": 0.95,
  "reason": "most recent ticket requested"
}

User: dernier ticket global
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "most_recent_ticket",
  "arguments": {},
  "confidence": 0.95,
  "reason": "most recent ticket requested"
}

User: cherche ticket bank
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "search_tickets",
  "arguments": {
    "query": "bank"
  },
  "confidence": 0.95,
  "reason": "text search in tickets requested"
}

User: trouve les tickets avec sujet test
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "search_tickets",
  "arguments": {
    "query": "test",
    "fields": ["subject"]
  },
  "confidence": 0.95,
  "reason": "subject search requested"
}

User: liste les tickets contenant bank
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "search_tickets",
  "arguments": {
    "query": "bank"
  },
  "confidence": 0.95,
  "reason": "text search in tickets requested"
}

User: tickets qui parlent de login
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "search_tickets",
  "arguments": {
    "query": "login"
  },
  "confidence": 0.95,
  "reason": "text search in tickets requested"
}

User: recherche tickets description erreur
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "search_tickets",
  "arguments": {
    "query": "erreur",
    "fields": ["description"]
  },
  "confidence": 0.95,
  "reason": "description search requested"
}

User: trouve ticket bug login
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "search_tickets",
  "arguments": {
    "query": "bug login"
  },
  "confidence": 0.95,
  "reason": "text search in tickets requested"
}

User: cherche dans les tickets "password"
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "search_tickets",
  "arguments": {
    "query": "password"
  },
  "confidence": 0.95,
  "reason": "text search in tickets requested"
}

User: tickets contenant problème accès
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "search_tickets",
  "arguments": {
    "query": "problème accès"
  },
  "confidence": 0.95,
  "reason": "text search in tickets requested"
}

User: crée un ticket pour Ahmed sujet bug login priorité HIGH
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "create_ticket",
  "arguments": {
    "employee_name": "Ahmed",
    "subject": "bug login",
    "priority": "HIGH"
  },
  "confidence": 0.95,
  "reason": "ticket creation requested"
}

User: ajoute ticket pour Sarra sujet problème accès
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "create_ticket",
  "arguments": {
    "employee_name": "Sarra",
    "subject": "problème accès"
  },
  "confidence": 0.95,
  "reason": "ticket creation requested"
}

User: ouvrir ticket pour Sedki description problème bank priorité urgente
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "create_ticket",
  "arguments": {
    "employee_name": "Sedki",
    "description": "problème bank",
    "subject": "problème bank",
    "priority": "HIGH"
  },
  "confidence": 0.95,
  "reason": "ticket creation requested"
}

User: change le statut du ticket TKT-0007 en RESOLVED
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "update_ticket_status",
  "arguments": {
    "ticket_code": "TKT-0007",
    "status": "RESOLVED"
  },
  "confidence": 0.95,
  "reason": "ticket status update requested"
}

User: mettre ticket 7 en CLOSED
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "update_ticket_status",
  "arguments": {
    "ticket_code": "7",
    "status": "CLOSED"
  },
  "confidence": 0.95,
  "reason": "ticket status update requested"
}

User: résoudre ticket TKT-0003
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "update_ticket_status",
  "arguments": {
    "ticket_code": "TKT-0003",
    "status": "RESOLVED"
  },
  "confidence": 0.95,
  "reason": "resolve ticket requested"
}

User: fermer ticket TKT-0005
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "update_ticket_status",
  "arguments": {
    "ticket_code": "TKT-0005",
    "status": "CLOSED"
  },
  "confidence": 0.95,
  "reason": "close ticket requested"
}

User: assigne le ticket TKT-0003 à Ahmed
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "assign_ticket",
  "arguments": {
    "ticket_code": "TKT-0003",
    "employee_name": "Ahmed"
  },
  "confidence": 0.95,
  "reason": "ticket assignment requested"
}

User: affecter ticket 5 à Sarra
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "assign_ticket",
  "arguments": {
    "ticket_code": "5",
    "employee_name": "Sarra"
  },
  "confidence": 0.95,
  "reason": "ticket assignment requested"
}

User: attribue le ticket TKT-0010 à Sedki
JSON:
{
  "handled": true,
  "tool_name": "ticket",
  "action_name": "assign_ticket",
  "arguments": {
    "ticket_code": "TKT-0010",
    "employee_name": "Sedki"
  },
  "confidence": 0.95,
  "reason": "ticket assignment requested"
}
'''
