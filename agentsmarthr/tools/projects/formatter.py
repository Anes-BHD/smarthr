from datetime import date
from typing import Any, Dict, List

from clients.project_api_client import normalize_priority, parse_project_date


def _value(value: Any, default: str = "Non renseigné") -> str:
    if value in (None, "", []):
        return default
    return str(value)


def _project_name(project: Dict[str, Any]) -> str:
    return _value(project.get("name"), "Projet sans nom")


def _deadline(project: Dict[str, Any]) -> str:
    return _value(project.get("deadline") or project.get("end_date"))


def _team_text(project: Dict[str, Any]) -> str:
    team = project.get("team") or []
    return ", ".join(str(member) for member in team) if team else "Non renseignée"


def _project_line(project: Dict[str, Any], index: int) -> str:
    return (
        f"{index}. {_project_name(project)} — Client : {_value(project.get('client'))} — "
        f"Priorité : {_value(project.get('priority'))} — Deadline : {_deadline(project)}"
    )


def build_project_recommendation(project: Dict[str, Any]) -> str:
    recommendations = []
    deadline = parse_project_date(project.get("deadline") or project.get("end_date"))
    today = date.today()

    if deadline:
        days_left = (deadline - today).days
        if deadline < today:
            recommendations.append("la deadline est dépassée, il faut vérifier l’avancement du projet en priorité.")
        elif days_left <= 30:
            recommendations.append("la deadline arrive dans moins de 30 jours, un suivi rapproché est recommandé.")

    priority = normalize_priority(project.get("priority"))
    if priority in {"high", "urgent"}:
        recommendations.append("ce projet est prioritaire, il faut le suivre régulièrement.")

    if not project.get("team"):
        recommendations.append("ce projet n’a pas d’équipe assignée.")

    if not project.get("project_leader"):
        recommendations.append("ce projet n’a pas de responsable assigné.")

    opened_tasks = project.get("opened_tasks")
    try:
        opened_count = int(opened_tasks)
    except (TypeError, ValueError):
        opened_count = 0
    if opened_count > 0 and deadline and 0 <= (deadline - today).days <= 30:
        recommendations.append("il reste des tâches ouvertes alors que la deadline est proche.")

    if not recommendations:
        return "Aucune alerte particulière. Le projet peut continuer avec un suivi normal."
    return " ".join(recommendations)


def _with_recommendation(response: str, project: Dict[str, Any]) -> str:
    return response + "\n\nRecommandation :\n" + build_project_recommendation(project)


def format_project_choices(projects: List[Dict[str, Any]]) -> str:
    lines = ["J’ai trouvé plusieurs projets possibles. Pouvez-vous préciser ?"]
    for index, project in enumerate(projects[:5], start=1):
        lines.append(f"{index}. {_project_name(project)} — Client : {_value(project.get('client'))}")
    return "\n".join(lines)


def format_project_list(projects: List[Dict[str, Any]]) -> str:
    if not projects:
        return "Aucun projet trouvé."
    lines = ["Voici les projets trouvés :"]
    lines.extend(_project_line(project, index) for index, project in enumerate(projects, start=1))
    return "\n".join(lines)


def format_list_projects(projects: List[Dict[str, Any]]) -> str:
    return format_project_list(projects)


def format_project_count(count: int) -> str:
    return f"Il y a {count} projet(s)."


def format_count_projects(projects: List[Dict[str, Any]]) -> str:
    return format_project_count(len(projects))


def format_project_details(project: Dict[str, Any]) -> str:
    response = (
        f"Détails du projet {_project_name(project)} :\n"
        f"- Client : {_value(project.get('client'))}\n"
        f"- Début : {_value(project.get('start_date'))}\n"
        f"- Deadline : {_deadline(project)}\n"
        f"- Priorité : {_value(project.get('priority'))}\n"
        f"- Chef de projet : {_value(project.get('project_leader'))}\n"
        f"- Équipe : {_team_text(project)}\n"
        f"- Description : {_value(project.get('description'))}"
    )
    return _with_recommendation(response, project)


def format_project_deadline(project: Dict[str, Any]) -> str:
    response = f"La deadline du projet {_project_name(project)} est : {_deadline(project)}."
    return _with_recommendation(response, project)


def format_project_leader(project: Dict[str, Any]) -> str:
    return f"Le chef du projet {_project_name(project)} est : {_value(project.get('project_leader'))}."


def format_project_team(project: Dict[str, Any]) -> str:
    team = project.get("team") or []
    if not team:
        return _with_recommendation(f"L’équipe du projet {_project_name(project)} n’est pas renseignée.", project)
    lines = [f"L’équipe du projet {_project_name(project)} contient :"]
    lines.extend(f"- {member}" for member in team)
    return "\n".join(lines)


def format_project_priority(project: Dict[str, Any]) -> str:
    response = f"La priorité du projet {_project_name(project)} est : {_value(project.get('priority'))}."
    return _with_recommendation(response, project)


def format_projects_by_priority(projects: List[Dict[str, Any]], priority: str) -> str:
    if not projects:
        return f"Aucun projet avec priorité {priority.title()} trouvé."
    lines = [f"Voici les projets avec priorité {priority.title()} :"]
    lines.extend(
        f"{index}. {_project_name(project)} — Deadline : {_deadline(project)} — Client : {_value(project.get('client'))}"
        for index, project in enumerate(projects, start=1)
    )
    return "\n".join(lines)


def format_projects_by_client(projects: List[Dict[str, Any]], client_name: str) -> str:
    if not projects:
        return f"Aucun projet trouvé pour le client {client_name}."
    lines = [f"Voici les projets du client {client_name} :"]
    lines.extend(_project_line(project, index) for index, project in enumerate(projects, start=1))
    return "\n".join(lines)


def format_projects_by_person(projects: List[Dict[str, Any]], person_name: str, mode: str) -> str:
    if mode == "leader":
        title = f"Voici les projets dirigés par {person_name} :"
        empty = f"Aucun projet dirigé par {person_name} trouvé."
    else:
        title = f"Voici les projets où {person_name} est membre :"
        empty = f"Aucun projet trouvé pour {person_name} comme membre."

    if not projects:
        return empty
    lines = [title]
    lines.extend(_project_line(project, index) for index, project in enumerate(projects, start=1))
    return "\n".join(lines)


def format_near_deadline(projects: List[Dict[str, Any]]) -> str:
    if not projects:
        return "Aucun projet proche de la deadline trouvé."
    lines = ["Voici les projets proches de la deadline :"]
    lines.extend(_project_line(project, index) for index, project in enumerate(projects, start=1))
    return "\n".join(lines)


def format_overdue_projects(projects: List[Dict[str, Any]]) -> str:
    if not projects:
        return "Aucun projet en retard trouvé."
    lines = ["Voici les projets en retard :"]
    lines.extend(
        f"{index}. {_project_name(project)} — Deadline : {_deadline(project)} — Priorité : {_value(project.get('priority'))}"
        for index, project in enumerate(projects, start=1)
    )
    return "\n".join(lines)


def format_project_recommendation(project_or_projects: Dict[str, Any] | List[Dict[str, Any]]) -> str:
    if isinstance(project_or_projects, dict):
        return "Recommandation :\n" + build_project_recommendation(project_or_projects)

    projects = project_or_projects
    if not projects:
        return "Recommandation :\nAucun projet trouvé à analyser."

    overdue = [project for project in projects if parse_project_date(project.get("deadline")) and parse_project_date(project.get("deadline")) < date.today()]
    if overdue:
        project = overdue[0]
        return (
            "Recommandation :\n"
            f"Le projet {_project_name(project)} a une deadline dépassée. "
            "Je recommande de vérifier son avancement et de le traiter en priorité."
        )

    high_priority = [project for project in projects if normalize_priority(project.get("priority")) in {"high", "urgent"}]
    if high_priority:
        project = high_priority[0]
        return (
            "Recommandation :\n"
            f"Le projet {_project_name(project)} est prioritaire. Je recommande de le suivre régulièrement."
        )

    near = [
        project
        for project in projects
        if parse_project_date(project.get("deadline")) and 0 <= (parse_project_date(project.get("deadline")) - date.today()).days <= 30
    ]
    if near:
        project = near[0]
        return (
            "Recommandation :\n"
            f"Le projet {_project_name(project)} se termine bientôt. Je recommande un suivi rapproché."
        )

    return "Recommandation :\nAucun projet critique détecté pour le moment."
