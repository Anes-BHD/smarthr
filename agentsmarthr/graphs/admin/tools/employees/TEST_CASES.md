# Employee Phase 1 Read Test Cases

These user phrases must be planned as:

```json
{
  "tool_name": "employees",
  "action_name": "get_employee_info"
}
```

- donne moi tel de Ahmed
- quelle est la designation de Ahmed
- je veux voir designation de Ahmed
- poste de Ahmed
- Ahmed travaille comme quoi
- donne moi mail de Ahmed
- adresse de Ahmed
- department de Ahmed
- statut de Ahmed

Phase 1 READ must keep returning `get_employee_info`.

Full READ examples must return `get_employee_full_info`:

- donne moi info de Ahmed
- info employé Ahmed
- détails de Ahmed
- profile de Ahmed
- full info employee Ahmed

Phase 2 CREATE examples:

- ajoute employe Ahmed Ben Ali email ahmed2@test.com tel 12345678 department IT Department designation Développeur Web
- ajoute employe Sami email sami@test.com tel 99999999 department IT Department
- lastname Trabelsi designation Développeur Web
- oui
- non

Unsupported actions outside READ, CREATE, UPDATE, DELETE, and ANALYTICS must still be rejected.

Phase 3 UPDATE examples:

- modifier phone de sedki à 55555555
- change email de sedki à sedki2@test.com
- changer department de sedki à IT Department
- modifier designation de sedki à Developer
- change phone de sedki
- 55555555
- oui
- non

Phase 3 DELETE examples:

- supprimer employé sedki
- delete employee sedki
- efface sedki
- oui
- non

Phase 3 ANALYTICS examples:

- combien d’employés
- nombre employés dans IT
- liste employés du département IT
- combien de Developer
- liste employés par department
- liste employés par designation

Absence tool examples:

- qui est absent aujourd’hui ?
- liste des absents aujourd’hui
- employés absents aujourd’hui
- combien de jours Ahmed est absent cette semaine ?
- nombre de jours absent de Sarra cette semaine
- combien de jours Ahmed est absent ce mois ?
- nombre de jours absent de Sarra ce mois-ci
- liste des absents entre 2026-05-01 et 2026-05-10
- qui est absent entre 01/05/2026 et 10/05/2026
- qui est absent aujourd’hui dans RH ?
- liste des absents aujourd’hui dans Human Resources
- absences dans IT ce mois

Ticket tool examples:

- combien de tickets OPEN
- combien de tickets a Ahmed
- dernier ticket de Ahmed
- liste des tickets ouverts
- liste les tickets de Ahmed
- tickets de Sarra
- quelle est la date du dernier ticket de Ahmed
- tickets aujourd’hui
- tickets cette semaine
- tickets ce mois
- combien de tickets ce mois

## Tickets Phase 3 — Statistiques

- combien de tickets sont ouverts ?
- combien de tickets OPEN ?
- combien de tickets sont en HIGH priorité ?
- combien de tickets urgents ?
- qui a le plus de tickets ?
- quel employé crée le plus de tickets ?
- tickets par statut
- tickets par priorité

## Tickets Phase 4 — Priorité + combinaisons

- liste les tickets HIGH
- liste les tickets urgents
- tickets HIGH de Ahmed
- tickets urgents de Sarra
- quel est le dernier ticket HIGH de Ahmed ?
- dernier ticket urgent de Sarra
- combien de tickets ouverts Ahmed a ?
- Ahmed a combien de tickets OPEN ?
- donne moi les tickets récents de Sedki
- derniers tickets de Ahmed
- quel ticket est le plus récent ?
- dernier ticket global

## Tickets Phase 5 — Recherche intelligente

- cherche ticket bank
- trouve les tickets avec sujet test
- liste les tickets contenant "bank"
- tickets qui parlent de login
- recherche tickets description erreur
- trouve ticket bug login
- cherche dans les tickets password
- tickets contenant problème accès

Anti-régression tickets :

- liste les tickets HIGH
- tickets HIGH de Ahmed
- combien de tickets ouverts Ahmed a ?
- tickets de Ahmed
- dernier ticket de Ahmed

## Tickets Phase 6 — Automatisation

### Create ticket

- crée un ticket pour Ahmed sujet bug login priorité HIGH
- ajoute ticket pour Sarra sujet problème accès
- ouvrir ticket pour Sedki description problème bank priorité urgente

### Update status

- change le statut du ticket TKT-0007 en RESOLVED
- mettre ticket 7 en CLOSED
- résoudre ticket TKT-0003
- fermer ticket TKT-0005

### Assign ticket

- assigne le ticket TKT-0003 à Ahmed
- affecter ticket 5 à Sarra
- attribue le ticket TKT-0010 à Sedki

### Confirmation

- oui
- non

### Anti-régression

- cherche ticket bank
- liste les tickets HIGH
- tickets par priorité
- dernier ticket de Ahmed
- combien de tickets OPEN

### Matching strict ticket_code

- assigne le ticket TKT-0019 à oussama
- assigne le ticket #TKT-0019 à oussama
- change le statut du ticket TKT-0019 en RESOLVED
- ticket 19 ne doit pas matcher TKT-0021
- TKT-0019 ne doit jamais matcher TKT-0021

### Status mapping Laravel

- change le statut du ticket TKT-0022 en RESOLVED
- résoudre ticket TKT-0022
- change le statut du ticket TKT-0022 en IN_PROGRESS
- fermer ticket TKT-0022

## Tickets Recommendations

- ouvrir ticket pour Sedki description problème bank priorité urgente
- liste les tickets urgents
- liste les tickets HIGH
- combien de tickets ouverts Ahmed a ?
- assigne le ticket TKT-0003 à Ahmed

Vérifier :

- réponse normale toujours présente
- recommandation ajoutée
- pas de recommandation inventée
- pas de régression phases 1 à 6
