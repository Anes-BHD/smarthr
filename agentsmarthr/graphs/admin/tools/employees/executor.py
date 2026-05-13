import json
import re
from typing import Any, Dict, List, Optional

from clients import department_api_client, designation_api_client, employee_api_client, php_api_client
from memory.pending_state import clear_pending_state, get_pending_state, set_pending_state


READ_ACTION = "get_employee_info"
FULL_READ_ACTION = "get_employee_full_info"
CREATE_ACTION = "create_employee"
UPDATE_ACTION = "update_employee"
DELETE_ACTION = "delete_employee"
ANALYTICS_ACTION = "employee_analytics"
SUPPORTED_ACTIONS = {
    READ_ACTION,
    FULL_READ_ACTION,
    CREATE_ACTION,
    UPDATE_ACTION,
    DELETE_ACTION,
    ANALYTICS_ACTION,
}
SUPPORTED_FIELDS = {
    "phone",
    "email",
    "address",
    "designation",
    "department",
    "firstname",
    "lastname",
    "full_name",
    "status",
    "joining_date",
}
CREATE_REQUIRED_FIELDS = [
    "firstname",
    "lastname",
    "email",
    "phone",
    "department_name",
    "designation_name",
]
UPDATE_FIELDS = {
    "firstname",
    "lastname",
    "email",
    "phone",
    "department_name",
    "designation_name",
}
ACTION_DISABLED_MESSAGE = "Cette action n’est pas encore activée dans cette phase."
UNSUPPORTED_FIELD_MESSAGE = "Je peux lire seulement : téléphone, email, adresse, designation, département, nom complet et statut."


FIELD_LABELS = {
    "phone": "Le téléphone de {name} est : {value}",
    "email": "L’email de {name} est : {value}",
    "address": "L’adresse de {name} est : {value}",
    "designation": "La designation de {name} est : {value}",
    "department": "Le département de {name} est : {value}",
    "firstname": "Le prénom de {name} est : {value}",
    "lastname": "Le nom de {name} est : {value}",
    "full_name": "Le nom complet de {name} est : {value}",
    "status": "Le statut de {name} est : {value}",
    "joining_date": "La date d’entrée de {name} est : {value}",
}


def _as_dict(plan: Any) -> Dict[str, Any]:
    if isinstance(plan, dict):
        return plan
    if hasattr(plan, "__dict__"):
        return dict(plan.__dict__)
    return {}


def _clean(value: Any) -> str:
    return str(value).strip() if value not in (None, "") else ""


def _employee_id(employee: Dict[str, Any]) -> Optional[Any]:
    return employee.get("id") or employee.get("employee_id")


def _employee_name(employee: Dict[str, Any], fallback: str = "cet employé") -> str:
    return str(employee_api_client.get_employee_field(employee, "full_name") or fallback)


def _id_from_record(record: Dict[str, Any]) -> Optional[Any]:
    return record.get("id") or record.get("value")


def _api_error_message(error: php_api_client.SmartHRApiError) -> str:
    details = error.details
    parsed: Any = None

    if isinstance(details, str):
        try:
            parsed = json.loads(details)
        except json.JSONDecodeError:
            parsed = None
    elif isinstance(details, dict):
        parsed = details

    if isinstance(parsed, dict):
        message = parsed.get("message")
        if message:
            return str(message)

        errors = parsed.get("errors")
        if isinstance(errors, dict):
            for values in errors.values():
                if isinstance(values, list) and values:
                    return str(values[0])
                if values:
                    return str(values)

    if details:
        return str(details)

    return error.message


def _find_employee_or_message(employee_name: str, use_search: bool = False) -> Dict[str, Any]:
    result = employee_api_client.find_employee_by_name(employee_name, use_search=use_search)
    status = result.get("status")

    if status == "not_found":
        return {"ok": False, "message": f"Je n’ai trouvé aucun employé nommé {employee_name}."}
    if status == "multiple":
        return {"ok": False, "message": employee_api_client.MULTIPLE_EMPLOYEES_MESSAGE}
    if status != "found":
        return {"ok": False, "message": "Je n’ai pas pu trouver cet employé."}

    employee = result.get("employee") or {}
    employee_id = _employee_id(employee)
    if not employee_id:
        return {"ok": False, "message": "Je n’ai pas trouvé l’identifiant Laravel de cet employé."}

    return {"ok": True, "employee": employee, "employee_id": employee_id}


def _execute_read(plan: Dict[str, Any]) -> str:
    arguments = plan.get("arguments") or {}
    employee_name = _clean(arguments.get("employee_name"))
    field = _clean(arguments.get("field")).lower()

    if not employee_name:
        return "Quel employé voulez-vous consulter ?"
    if not field:
        return "Quelle information voulez-vous consulter ? téléphone, email, adresse, designation ou département ?"
    if field not in SUPPORTED_FIELDS:
        return UNSUPPORTED_FIELD_MESSAGE

    result = employee_api_client.find_employee_by_name(employee_name)
    status = result.get("status")

    if status == "missing_name":
        return "Quel employé voulez-vous consulter ?"
    if status == "not_found":
        return f"Je n’ai trouvé aucun employé nommé {employee_name}."
    if status == "multiple":
        return employee_api_client.MULTIPLE_EMPLOYEES_MESSAGE
    if status != "found":
        return "Je n’ai pas pu lire les informations de cet employé."

    employee = result.get("employee") or {}
    value = employee_api_client.get_employee_field(employee, field)
    display_name = _employee_name(employee, employee_name)

    if value in (None, ""):
        return f"Je n’ai pas trouvé la valeur {field} pour {display_name}."

    return FIELD_LABELS[field].format(name=display_name, value=value)


def _candidate_label(employee: Dict[str, Any], index: int) -> str:
    name = _employee_name(employee, "Employé sans nom")
    email = employee_api_client.get_employee_field(employee, "email")
    return f"{index}. {name}" + (f" - {email}" if email else "")


def _multiple_employees_message(candidates: List[Dict[str, Any]]) -> str:
    lines = ["J’ai trouvé plusieurs employés :"]
    for index, employee in enumerate(candidates, start=1):
        lines.append(_candidate_label(employee, index))
    lines.append("Donnez le numéro ou le nom complet.")
    return "\n".join(lines)


def _format_full_info(employee: Dict[str, Any]) -> str:
    firstname = employee_api_client.get_employee_field(employee, "firstname")
    lastname = employee_api_client.get_employee_field(employee, "lastname")
    full_name = _clean(employee_api_client.get_employee_field(employee, "full_name"))
    if not full_name:
        full_name = f"{_clean(firstname)} {_clean(lastname)}".strip()

    fields = [
        ("Nom complet", full_name),
        ("Email", employee_api_client.get_employee_field(employee, "email")),
        ("Téléphone", employee_api_client.get_employee_field(employee, "phone")),
        ("Département", employee_api_client.get_employee_field(employee, "department")),
        ("Poste", employee_api_client.get_employee_field(employee, "designation")),
        ("Status", employee_api_client.get_employee_field(employee, "status")),
        ("Date d'entrée", employee_api_client.get_employee_field(employee, "joining_date")),
    ]

    return "\n".join(f"{label} : {value if value not in (None, '') else 'Non renseigné'}" for label, value in fields)


def _execute_full_read(plan: Dict[str, Any]) -> str:
    session_id = _clean(plan.get("_session_id")) or "default"
    arguments = plan.get("arguments") or plan
    selected_employee = plan.get("_selected_employee")
    if isinstance(selected_employee, dict):
        clear_pending_state(session_id)
        return _format_full_info(selected_employee)

    employee_name = _clean(arguments.get("employee_name"))

    if not employee_name:
        return "Quel employé voulez-vous consulter ?"

    result = employee_api_client.find_employee_by_name(employee_name, use_search=True)
    status = result.get("status")

    if status == "not_found":
        return "Employé introuvable"
    if status == "multiple":
        candidates = result.get("employees") or []
        set_pending_state(
            session_id,
            {
                "pending_action": FULL_READ_ACTION,
                "awaiting_disambiguation": True,
                "disambiguation_type": "employee",
                "candidates": candidates,
                "original_query": plan.get("_raw_message") or employee_name,
            },
        )
        return _multiple_employees_message(candidates)
    if status != "found":
        return "Employé introuvable"

    employee = result.get("employee") or {}
    clear_pending_state(session_id)
    return _format_full_info(employee)


def _slot_arguments(arguments: Dict[str, Any]) -> Dict[str, str]:
    return {
        "firstname": _clean(arguments.get("firstname")),
        "lastname": _clean(arguments.get("lastname")),
        "email": _clean(arguments.get("email")),
        "phone": _clean(arguments.get("phone")),
        "department_name": _clean(arguments.get("department_name") or arguments.get("department")),
        "designation_name": _clean(arguments.get("designation_name") or arguments.get("designation")),
    }


def _find_label_value(text: str, labels: List[str], stop_labels: List[str]) -> str:
    lowered = text.lower()
    label_match = None
    for label in labels:
        match = re.search(r"(^|\s)" + re.escape(label.lower()) + r"\s+", lowered)
        if match and (label_match is None or match.end() < label_match.end()):
            label_match = match

    if not label_match:
        return ""

    start = label_match.end()
    end = len(text)
    for stop_label in stop_labels:
        stop_match = re.search(r"\s" + re.escape(stop_label.lower()) + r"\s+", lowered[start:])
        if stop_match:
            end = min(end, start + stop_match.start())

    return text[start:end].strip(" :,-")


def _fallback_slots_from_text(raw_message: str, missing_fields: List[str]) -> Dict[str, str]:
    text = _clean(raw_message)
    if not text:
        return {}

    all_labels = [
        "firstname",
        "prenom",
        "prénom",
        "lastname",
        "nom",
        "email",
        "mail",
        "phone",
        "tel",
        "telephone",
        "téléphone",
        "department",
        "departement",
        "département",
        "service",
        "designation",
        "poste",
        "fonction",
    ]
    slots: Dict[str, str] = {}

    if "firstname" in missing_fields:
        slots["firstname"] = _find_label_value(text, ["firstname", "prenom", "prénom"], all_labels)
    if "lastname" in missing_fields:
        slots["lastname"] = _find_label_value(text, ["lastname", "nom"], all_labels)
    if "email" in missing_fields:
        email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
        slots["email"] = email_match.group(0) if email_match else _find_label_value(text, ["email", "mail"], all_labels)
    if "phone" in missing_fields:
        slots["phone"] = _find_label_value(text, ["phone", "tel", "telephone", "téléphone"], all_labels)
    if "department_name" in missing_fields:
        slots["department_name"] = _find_label_value(text, ["department", "departement", "département", "service"], all_labels)
    if "designation_name" in missing_fields:
        slots["designation_name"] = _find_label_value(text, ["designation", "poste", "fonction"], all_labels)

    useful_slots = {key: value for key, value in slots.items() if value}
    if useful_slots:
        return useful_slots

    if len(missing_fields) == 1:
        return {missing_fields[0]: text}

    if missing_fields == ["lastname", "designation_name"]:
        parts = text.split()
        if len(parts) >= 2:
            return {"lastname": " ".join(parts[:-1]), "designation_name": parts[-1]}

    return {}


def _missing_fields(slots: Dict[str, str]) -> List[str]:
    return [field for field in CREATE_REQUIRED_FIELDS if not _clean(slots.get(field))]


def _missing_message(missing: List[str], slots: Dict[str, str]) -> str:
    firstname = slots.get("firstname") or "cet employé"

    if len(missing) > 1:
        readable = [field.replace("_name", "") for field in missing]
        return f"Il manque : {', '.join(readable)}. Pouvez-vous les fournir ?"

    field = missing[0]
    if field == "firstname":
        return "Quel est le prénom de l’employé ?"
    if field == "lastname":
        return f"Quel est le nom de famille de {firstname} ?"
    if field == "email":
        return f"Quel est l’email de {firstname} ?"
    if field == "phone":
        return f"Quel est le téléphone de {firstname} ?"
    if field == "department_name":
        return f"Quel est le département de {firstname} ?"
    if field == "designation_name":
        return f"Quelle est la designation de {firstname} ?"

    return "Pouvez-vous fournir les informations manquantes ?"


def _build_create_payload(slots: Dict[str, str], department_id: Any, designation_id: Any) -> Dict[str, Any]:
    return {
        "firstname": slots["firstname"],
        "lastname": slots["lastname"],
        "email": slots["email"],
        "phone": slots["phone"],
        "department": department_id,
        "designation": designation_id,
        "status": 1,
        "password": "password",
        "password_confirmation": "password",
    }


def _create_confirmation_message(slots: Dict[str, str]) -> str:
    return (
        "Je vais créer cet employé :\n\n"
        f"Prénom : {slots['firstname']}\n"
        f"Nom : {slots['lastname']}\n"
        f"Email : {slots['email']}\n"
        f"Téléphone : {slots['phone']}\n"
        f"Département : {slots['department_name']}\n"
        f"Designation : {slots['designation_name']}\n\n"
        "Confirmez-vous la création ? oui/non"
    )


def _resolve_department(name: str) -> Dict[str, Any]:
    result = department_api_client.find_department_by_name(name)
    if result.get("status") == "not_found":
        return {"ok": False, "message": f"Je n’ai pas trouvé le département {name}. Veuillez choisir un département existant."}
    if result.get("status") == "multiple":
        return {"ok": False, "message": "J’ai trouvé plusieurs départements avec ce nom. Pouvez-vous préciser ?"}

    department = result.get("department") or {}
    department_id = _id_from_record(department)
    if not department_id:
        return {"ok": False, "message": f"Je n’ai pas trouvé le département {name}. Veuillez choisir un département existant."}

    return {"ok": True, "id": department_id}


def _resolve_designation(name: str) -> Dict[str, Any]:
    result = designation_api_client.find_designation_by_name(name)
    if result.get("status") == "not_found":
        return {"ok": False, "message": f"Je n’ai pas trouvé la designation {name}. Veuillez choisir une designation existante."}
    if result.get("status") == "multiple":
        return {"ok": False, "message": "J’ai trouvé plusieurs designations avec ce nom. Pouvez-vous préciser ?"}

    designation = result.get("designation") or {}
    designation_id = _id_from_record(designation)
    if not designation_id:
        return {"ok": False, "message": f"Je n’ai pas trouvé la designation {name}. Veuillez choisir une designation existante."}

    return {"ok": True, "id": designation_id}


def _relation_value(employee: Dict[str, Any], field: str) -> Any:
    employee_detail = employee.get("employee_detail") or {}
    relation = employee_detail.get(field)
    if isinstance(relation, dict):
        return relation.get("id") or relation.get("name")
    if relation not in (None, ""):
        return relation

    direct_relation = employee.get(field)
    if isinstance(direct_relation, dict):
        return direct_relation.get("id") or direct_relation.get("name")
    if direct_relation not in (None, ""):
        return direct_relation

    return employee_api_client.get_employee_field(employee, field)


def _department_payload_value(value: Any) -> Any:
    if value in (None, ""):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)

    result = _resolve_department(str(value))
    if result.get("ok"):
        return result["id"]

    return value


def _designation_payload_value(value: Any) -> Any:
    if value in (None, ""):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)

    result = _resolve_designation(str(value))
    if result.get("ok"):
        return result["id"]

    return value


def _status_payload_value(employee: Dict[str, Any]) -> Any:
    if employee.get("status") not in (None, ""):
        return employee.get("status")
    if employee.get("employment_status") not in (None, ""):
        return employee.get("employment_status")
    if employee.get("is_active") is not None:
        return 1 if employee.get("is_active") else 0
    return "active"


def _confirm_create(session_id: str) -> str:
    pending = get_pending_state(session_id)
    if not pending or pending.get("pending_action") != CREATE_ACTION:
        return "Aucune création d’employé n’est en attente."

    payload = pending.get("payload") or {}
    slots = pending.get("pending_slots") or {}
    full_name = f"{slots.get('firstname') or payload.get('firstname') or ''} {slots.get('lastname') or payload.get('lastname') or ''}".strip()

    try:
        employee_api_client.create_employee(payload)
    except php_api_client.SmartHRApiError as error:
        clear_pending_state(session_id)
        return f"Laravel a refusé la création : {_api_error_message(error)}"

    clear_pending_state(session_id)
    return f"Employé {full_name} créé avec succès."


def _execute_create(plan: Dict[str, Any]) -> str:
    session_id = _clean(plan.get("_session_id")) or "default"

    if plan.get("_confirmed"):
        return _confirm_create(session_id)

    pending = get_pending_state(session_id) or {}
    previous_slots = pending.get("pending_slots") or {}
    missing_before = pending.get("missing_fields") or []
    raw_message = _clean(plan.get("_raw_message"))
    arguments = plan.get("arguments") or {}

    slots = {**previous_slots, **{key: value for key, value in _slot_arguments(arguments).items() if value}}
    slots.update({key: value for key, value in _fallback_slots_from_text(raw_message, missing_before).items() if value})

    missing = _missing_fields(slots)
    if missing:
        set_pending_state(session_id, {"pending_action": CREATE_ACTION, "pending_slots": slots, "missing_fields": missing, "awaiting_confirmation": False})
        return _missing_message(missing, slots)

    set_pending_state(session_id, {"pending_action": CREATE_ACTION, "pending_slots": slots, "missing_fields": [], "awaiting_confirmation": False})

    department_result = _resolve_department(slots["department_name"])
    if not department_result["ok"]:
        return department_result["message"]

    designation_result = _resolve_designation(slots["designation_name"])
    if not designation_result["ok"]:
        return designation_result["message"]

    payload = _build_create_payload(slots, department_result["id"], designation_result["id"])
    set_pending_state(
        session_id,
        {
            "pending_action": CREATE_ACTION,
            "pending_slots": slots,
            "missing_fields": [],
            "awaiting_confirmation": True,
            "payload": payload,
        },
    )

    return _create_confirmation_message(slots)


def _update_fields_from_arguments(arguments: Dict[str, Any]) -> Dict[str, str]:
    fields = arguments.get("fields")
    if not isinstance(fields, dict):
        fields = {}

    combined = {**fields}
    for key in UPDATE_FIELDS:
        if key in arguments:
            combined[key] = arguments.get(key)

    if "department" in combined and "department_name" not in combined:
        combined["department_name"] = combined.pop("department")
    if "designation" in combined and "designation_name" not in combined:
        combined["designation_name"] = combined.pop("designation")

    return {key: _clean(value) for key, value in combined.items() if key in UPDATE_FIELDS}


def _fallback_update_fields(raw_message: str, missing_fields: List[str]) -> Dict[str, str]:
    text = _clean(raw_message)
    if not text:
        return {}

    if len(missing_fields) == 1:
        return {missing_fields[0]: text}

    return _fallback_slots_from_text(text, missing_fields)


def _update_missing_message(employee_name: str, fields: Dict[str, str]) -> str:
    if not employee_name:
        return "Quel employé voulez-vous modifier ?"
    if not fields:
        return "Quelle information voulez-vous modifier ? firstname, lastname, email, phone, department ou designation ?"

    missing_values = [field for field, value in fields.items() if not value]
    if len(missing_values) == 1:
        readable = missing_values[0].replace("_name", "")
        return f"Quelle est la nouvelle valeur pour {readable} ?"
    if missing_values:
        readable = [field.replace("_name", "") for field in missing_values]
        return f"Il manque les nouvelles valeurs pour : {', '.join(readable)}."

    return ""


def _build_update_payload(employee: Dict[str, Any], fields: Dict[str, str]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "firstname": employee_api_client.get_employee_field(employee, "firstname"),
        "lastname": employee_api_client.get_employee_field(employee, "lastname"),
        "email": employee_api_client.get_employee_field(employee, "email"),
        "phone": employee_api_client.get_employee_field(employee, "phone"),
        "department": _department_payload_value(_relation_value(employee, "department")),
        "designation": _designation_payload_value(_relation_value(employee, "designation")),
        "status": _status_payload_value(employee),
    }

    for key in ("firstname", "lastname", "email", "phone"):
        if fields.get(key):
            payload[key] = fields[key]

    if fields.get("department_name"):
        department_result = _resolve_department(fields["department_name"])
        if not department_result["ok"]:
            raise ValueError(department_result["message"])
        payload["department"] = department_result["id"]

    if fields.get("designation_name"):
        designation_result = _resolve_designation(fields["designation_name"])
        if not designation_result["ok"]:
            raise ValueError(designation_result["message"])
        payload["designation"] = designation_result["id"]

    return payload


def _update_confirmation_message(employee_name: str, fields: Dict[str, str]) -> str:
    lines = []
    for key, value in fields.items():
        if value:
            lines.append(f"{key.replace('_name', '')} : {value}")

    return (
        f"Je vais modifier l’employé {employee_name} :\n\n"
        + "\n".join(lines)
        + "\n\nConfirmez-vous la modification ? oui/non"
    )


def _confirm_update(session_id: str) -> str:
    pending = get_pending_state(session_id)
    if not pending or pending.get("pending_action") != UPDATE_ACTION:
        return "Aucune modification d’employé n’est en attente."

    payload = pending.get("payload") or {}
    target = pending.get("target_employee") or {}
    employee_id = target.get("id")
    employee_name = target.get("name") or "cet employé"

    try:
        print("UPDATE PAYLOAD:", payload)
        employee_api_client.update_employee(employee_id, payload)
    except php_api_client.SmartHRApiError as error:
        clear_pending_state(session_id)
        return f"Laravel a refusé la modification : {_api_error_message(error)}"

    clear_pending_state(session_id)
    return f"Employé {employee_name} modifié avec succès."


def _execute_update(plan: Dict[str, Any]) -> str:
    session_id = _clean(plan.get("_session_id")) or "default"

    if plan.get("_confirmed"):
        return _confirm_update(session_id)

    pending = get_pending_state(session_id) or {}
    previous_slots = pending.get("pending_slots") or {}
    raw_message = _clean(plan.get("_raw_message"))
    arguments = plan.get("arguments") or plan

    employee_name = _clean(arguments.get("employee_name")) or _clean(previous_slots.get("employee_name"))
    fields = {**(previous_slots.get("fields") or {}), **_update_fields_from_arguments(arguments)}
    missing_before = pending.get("missing_fields") or [field for field, value in fields.items() if not value]
    if pending.get("pending_action") == UPDATE_ACTION:
        fields.update({key: value for key, value in _fallback_update_fields(raw_message, missing_before).items() if value})

    missing_message = _update_missing_message(employee_name, fields)
    if missing_message:
        missing_fields = [field for field, value in fields.items() if not value]
        set_pending_state(
            session_id,
            {
                "pending_action": UPDATE_ACTION,
                "pending_slots": {"employee_name": employee_name, "fields": fields},
                "missing_fields": missing_fields,
                "awaiting_confirmation": False,
            },
        )
        return missing_message

    target = _find_employee_or_message(employee_name, use_search=True)
    if not target["ok"]:
        return target["message"]

    try:
        payload = _build_update_payload(target["employee"], fields)
    except ValueError as error:
        return str(error)

    display_name = _employee_name(target["employee"], employee_name)
    set_pending_state(
        session_id,
        {
            "pending_action": UPDATE_ACTION,
            "pending_slots": {"employee_name": employee_name, "fields": fields},
            "missing_fields": [],
            "awaiting_confirmation": True,
            "target_employee": {"id": target["employee_id"], "name": display_name},
            "payload": payload,
        },
    )
    return _update_confirmation_message(display_name, fields)


def _confirm_delete(session_id: str) -> str:
    pending = get_pending_state(session_id)
    if not pending or pending.get("pending_action") != DELETE_ACTION:
        return "Aucune suppression d’employé n’est en attente."

    target = pending.get("target_employee") or {}
    employee_id = target.get("id")
    employee_name = target.get("name") or "cet employé"

    try:
        employee_api_client.delete_employee(employee_id)
    except php_api_client.SmartHRApiError as error:
        clear_pending_state(session_id)
        return f"Laravel a refusé la suppression : {_api_error_message(error)}"

    clear_pending_state(session_id)
    return f"Employé {employee_name} supprimé avec succès."


def _execute_delete(plan: Dict[str, Any]) -> str:
    session_id = _clean(plan.get("_session_id")) or "default"

    if plan.get("_confirmed"):
        return _confirm_delete(session_id)

    arguments = plan.get("arguments") or plan
    employee_name = _clean(arguments.get("employee_name"))
    if not employee_name:
        return "Quel employé voulez-vous supprimer ?"

    target = _find_employee_or_message(employee_name)
    if not target["ok"]:
        return target["message"]

    display_name = _employee_name(target["employee"], employee_name)
    set_pending_state(
        session_id,
        {
            "pending_action": DELETE_ACTION,
            "pending_slots": {"employee_name": employee_name},
            "missing_fields": [],
            "awaiting_confirmation": True,
            "target_employee": {"id": target["employee_id"], "name": display_name},
        },
    )
    return f"Je vais supprimer l’employé {display_name}.\n\nConfirmez-vous la suppression ? oui/non"


def _matches_filter(value: Any, expected: str) -> bool:
    return _clean(expected).lower() in _clean(value).lower()


def _employee_line(employee: Dict[str, Any]) -> str:
    return _employee_name(employee, _clean(employee.get("email")) or "Employé sans nom")


def _group_employees(employees: List[Dict[str, Any]], field: str) -> str:
    groups: Dict[str, List[str]] = {}
    for employee in employees:
        value = employee_api_client.get_employee_field(employee, field) or "Non renseigné"
        groups.setdefault(str(value), []).append(_employee_line(employee))

    lines = []
    for group_name in sorted(groups):
        lines.append(f"{group_name} : {', '.join(groups[group_name])}")

    return "\n".join(lines) if lines else "Aucun employé trouvé."


def _execute_analytics(plan: Dict[str, Any]) -> str:
    arguments = plan.get("arguments") or plan
    metric = _clean(arguments.get("metric")).lower() or "total_count"
    department_name = _clean(arguments.get("department_name") or arguments.get("department"))
    designation_name = _clean(arguments.get("designation_name") or arguments.get("designation"))

    try:
        employees = employee_api_client.list_employees()
    except php_api_client.SmartHRApiError as error:
        return f"Laravel a refusé l’analyse : {_api_error_message(error)}"

    if metric == "total_count":
        return f"Il y a {len(employees)} employé(s)."

    if metric in {"count_by_department", "list_by_department"}:
        if not department_name:
            return "Quel département voulez-vous analyser ?"
        filtered = [employee for employee in employees if _matches_filter(employee_api_client.get_employee_field(employee, "department"), department_name)]
        if metric == "count_by_department":
            return f"Il y a {len(filtered)} employé(s) dans {department_name}."
        names = ", ".join(_employee_line(employee) for employee in filtered)
        return f"Employés du département {department_name} : {names or 'aucun'}."

    if metric in {"count_by_designation", "list_by_designation"}:
        if not designation_name:
            return "Quelle designation voulez-vous analyser ?"
        filtered = [employee for employee in employees if _matches_filter(employee_api_client.get_employee_field(employee, "designation"), designation_name)]
        if metric == "count_by_designation":
            return f"Il y a {len(filtered)} employé(s) avec la designation {designation_name}."
        names = ", ".join(_employee_line(employee) for employee in filtered)
        return f"Employés avec la designation {designation_name} : {names or 'aucun'}."

    if metric == "group_by_department":
        return "Employés par département :\n" + _group_employees(employees, "department")

    if metric == "group_by_designation":
        return "Employés par designation :\n" + _group_employees(employees, "designation")

    return "Je peux analyser : total, par département, ou par designation."


def execute_employee_tool(plan: Any) -> str:
    plan_dict = _as_dict(plan)
    action_name = plan_dict.get("action_name") or plan_dict.get("intent")

    if action_name not in SUPPORTED_ACTIONS:
        return ACTION_DISABLED_MESSAGE

    if action_name == READ_ACTION:
        return _execute_read(plan_dict)
    if action_name == FULL_READ_ACTION:
        return _execute_full_read(plan_dict)
    if action_name == CREATE_ACTION:
        return _execute_create(plan_dict)
    if action_name == UPDATE_ACTION:
        return _execute_update(plan_dict)
    if action_name == DELETE_ACTION:
        return _execute_delete(plan_dict)

    return _execute_analytics(plan_dict)
