import json
import unicodedata
from typing import Any, Dict

import httpx

from config import ENABLE_LLM_ROUTER, OPENROUTER_API_KEY, OPENROUTER_MODEL


OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

GATE_PROMPT = """
Tu es une couche de routage conversationnelle pour SmartHR.

Classe le message utilisateur dans UNE catégorie :
- business
- chitchat
- offtopic

Définitions :
business :
demande liée aux employés, tickets, absences, projets, RH, clients,
statistiques, recommandations ou actions SmartHR.

chitchat :
salutations, remerciements, petite conversation ou question sur l’assistant.

offtopic :
demande sans rapport avec SmartHR.

Règles importantes :
- En cas de doute → business.
- Si le message utilise un contexte mémoire ("son téléphone", "ce ticket"),
  utiliser la mémoire.
- Ne pas classifier offtopic si le message peut concerner SmartHR.

Réponds uniquement en JSON strict :
{
  "category": "business|chitchat|offtopic",
  "response": null,
  "confidence": 0.0
}
"""


CHITCHAT_RESPONSES = {
    "greeting": "Bonjour ! Je suis votre assistant SmartHR. Je peux vous aider avec les employés, tickets, absences et projets.",
    "thanks": "Avec plaisir ! Je reste disponible pour vous aider sur SmartHR.",
    "identity": "Je suis l’assistant intelligent SmartHR. Je peux vous aider avec les employés, tickets, absences, projets et recommandations RH.",
    "help": "Je peux vous aider avec les employés, tickets, absences, projets, statistiques et recommandations SmartHR.",
}

OFFTOPIC_RESPONSE = "Je suis spécialisé dans SmartHR. Je peux vous aider avec les employés, tickets, absences, projets et recommandations RH."


def _normalize(value: str) -> str:
    text = (value or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.replace("-", " ").replace("_", " ").split())


def _result(category: str, response: str | None, confidence: float) -> Dict[str, Any]:
    return {
        "category": category,
        "response": response,
        "confidence": confidence,
    }


def _memory_context(memory: Dict[str, Any] | None) -> str:
    memory = memory or {}
    return (
        "Mémoire session :\n"
        f"last_employee: {memory.get('last_employee') or 'null'}\n"
        f"last_project: {memory.get('last_project') or 'null'}\n"
        f"last_ticket: {memory.get('last_ticket') or 'null'}\n"
        f"last_tool: {memory.get('last_tool') or 'null'}\n"
        f"last_action: {memory.get('last_action') or 'null'}"
    )


def _looks_business(text: str, memory: Dict[str, Any] | None) -> bool:
    tokens = set(text.split())
    business_terms = {
        "employe",
        "employes",
        "employee",
        "employees",
        "ticket",
        "tickets",
        "absence",
        "absences",
        "absent",
        "absents",
        "projet",
        "projets",
        "project",
        "projects",
        "client",
        "clients",
        "rh",
        "smarthr",
        "statistique",
        "statistiques",
        "recommandation",
        "recommandations",
        "telephone",
        "phone",
        "email",
        "mail",
        "designation",
        "departement",
        "department",
        "deadline",
        "priorite",
        "priority",
        "statut",
        "status",
        "closed",
        "open",
        "inprogress",
    }
    if any(term in text for term in business_terms):
        return True

    memory = memory or {}
    employee_pronouns = {"son", "sa", "ses", "lui"}
    employee_phrases = {"cet employe", "cette personne"}
    if memory.get("last_employee") and (
        any(ref in tokens for ref in employee_pronouns)
        or any(ref in text for ref in employee_phrases)
    ):
        return True
    if memory.get("last_project") and any(ref in text for ref in ("ce projet", "son projet", "sa deadline", "projet actuel")):
        return True
    if memory.get("last_ticket") and any(ref in text for ref in ("ce ticket", "son ticket", "son statut", "ticket actuel")):
        return True
    return False


def _fallback_classify(user_message: str, memory: Dict[str, Any] | None = None) -> Dict[str, Any]:
    text = _normalize(user_message)
    if not text:
        return _result("chitchat", CHITCHAT_RESPONSES["help"], 0.8)

    if _looks_business(text, memory):
        return _result("business", None, 0.9)

    if text in {"salut", "bonjour", "bonsoir", "hello", "hi", "salam"}:
        return _result("chitchat", CHITCHAT_RESPONSES["greeting"], 0.95)

    if text in {"merci", "merci beaucoup", "thanks", "thank you"}:
        return _result("chitchat", CHITCHAT_RESPONSES["thanks"], 0.95)

    if any(phrase in text for phrase in ("ca va", "ça va", "qui es tu", "qui es-tu", "tu es qui", "tu fais quoi")):
        return _result("chitchat", CHITCHAT_RESPONSES["identity"], 0.9)

    if any(phrase in text for phrase in ("aide moi", "aide-moi", "que peux tu faire", "que peux-tu faire", "help")):
        return _result("chitchat", CHITCHAT_RESPONSES["help"], 0.9)

    offtopic_terms = {
        "recette",
        "crypto",
        "meteo",
        "film",
        "blague politique",
        "musique",
        "sport",
    }
    if any(term in text for term in offtopic_terms):
        return _result("offtopic", OFFTOPIC_RESPONSE, 0.85)

    return _result("business", None, 0.5)


def _normalize_llm_result(data: Dict[str, Any], user_message: str, memory: Dict[str, Any] | None) -> Dict[str, Any]:
    category = str(data.get("category") or "").strip().lower()
    if category not in {"business", "chitchat", "offtopic"}:
        return _fallback_classify(user_message, memory)

    if category == "business":
        return _result("business", None, float(data.get("confidence") or 0.7))

    fallback = _fallback_classify(user_message, memory)
    response = data.get("response") or fallback.get("response")
    confidence = float(data.get("confidence") or fallback.get("confidence") or 0.7)
    return _result(category, response, confidence)


def classify_message(user_message: str, memory: Dict[str, Any] | None = None) -> Dict[str, Any]:
    fallback = _fallback_classify(user_message, memory)
    if fallback["category"] == "business":
        return fallback

    if not ENABLE_LLM_ROUTER or not OPENROUTER_API_KEY:
        return fallback

    try:
        response = httpx.post(
            OPENROUTER_ENDPOINT,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENROUTER_MODEL,
                "temperature": 0,
                "max_tokens": 250,
                "messages": [
                    {"role": "system", "content": GATE_PROMPT},
                    {"role": "system", "content": _memory_context(memory)},
                    {"role": "user", "content": user_message},
                ],
            },
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
        content = payload.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        data = json.loads(content)
        if not isinstance(data, dict):
            return fallback
        return _normalize_llm_result(data, user_message, memory)
    except (httpx.HTTPError, ValueError, json.JSONDecodeError):
        return fallback
