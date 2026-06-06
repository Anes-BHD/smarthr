import re
import unicodedata
from typing import Any, Dict

import httpx

from config import (
    ENABLE_RESPONSE_HUMANIZER,
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
)


OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

HUMANIZER_PROMPT = """
Tu es un assistant RH professionnel SmartHR.
Réécris la réponse brute pour la rendre plus naturelle, claire et humaine.

Contraintes :
- Garde toutes les données exactement identiques.
- N’invente aucune information.
- Ne change pas les IDs, emails, téléphones, dates, statuts, noms ou nombres.
- Ne change pas le sens.
- Ne rajoute pas de recommandation si elle n’existe pas déjà.
- Réponds en français.
- Sois concis.
"""

SKIP_MARKERS = (
    "voulez-vous confirmer",
    "voulez vous confirmer",
    "oui/non",
    "impossible de",
    "erreur",
    "cette action",
    "non activée",
    "non activee",
    "introuvable",
    "réinitialisé",
    "reinitialise",
    "modifié avec succès",
    "modifie avec succes",
    "créé avec succès",
    "cree avec succes",
    "supprimé avec succès",
    "supprime avec succes",
    "mis à jour avec succès",
    "mis a jour avec succes",
    "succès",
    "succes",
)


def _normalize_text(value: str) -> str:
    text = (value or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.split())


def _should_skip(raw_response: str) -> bool:
    text = _normalize_text(raw_response)
    return not text or any(marker in text for marker in SKIP_MARKERS)


def _protected_tokens(value: str) -> set[str]:
    text = value or ""
    patterns = [
        r"\b[\w.+-]+@[\w.-]+\.\w+\b",
        r"#?\bTKT[-\s]?\d+\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{1,2}/\d{1,2}/\d{4}\b",
    ]
    tokens: set[str] = set()
    for pattern in patterns:
        tokens.update(match.group(0).strip() for match in re.finditer(pattern, text, flags=re.IGNORECASE))

    for match in re.finditer(r"\b\d+\b", text):
        token = match.group(0).strip()
        next_char = text[match.end() : match.end() + 1]
        if len(token) == 1 and next_char == ".":
            continue
        tokens.add(token)

    return {token for token in tokens if token}


def _keeps_protected_data(raw_response: str, final_response: str) -> bool:
    normalized_final = _normalize_text(final_response)
    for token in _protected_tokens(raw_response):
        if _normalize_text(token) not in normalized_final:
            return False
    return True


def _memory_context(memory: Dict[str, Any] | None) -> str:
    memory = memory or {}
    return (
        "Contexte compact :\n"
        f"employee={memory.get('last_employee') or 'null'}\n"
        f"ticket={memory.get('last_ticket') or 'null'}\n"
        f"project={memory.get('last_project') or 'null'}"
    )


def _is_max_tokens_budget_error(response: httpx.Response | None) -> bool:
    if response is None or response.status_code != 402:
        return False
    body = (response.text or "").lower()
    return "max_tokens" in body or "fewer max_tokens" in body or "can only afford" in body


def _call_openrouter(payload: Dict[str, Any]) -> Dict[str, Any] | None:
    try:
        response = httpx.post(
            OPENROUTER_ENDPOINT,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=20,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as exc:
        print(f"[RESPONSE_HUMANIZER ERROR] {exc}")
        print(f"[RESPONSE_HUMANIZER STATUS] {exc.response.status_code}")
        print(f"[RESPONSE_HUMANIZER BODY] {exc.response.text}")
        if _is_max_tokens_budget_error(exc.response) and payload.get("max_tokens") != 100:
            print("[RESPONSE_HUMANIZER RETRY] max_tokens=100")
            retry_payload = dict(payload)
            retry_payload["max_tokens"] = 100
            return _call_openrouter(retry_payload)
        return None
    except (httpx.HTTPError, ValueError) as exc:
        print(f"[RESPONSE_HUMANIZER ERROR] {exc}")
        return None


def humanize_response(
    raw_response: str,
    user_message: str,
    tool: str | None = None,
    action: str | None = None,
    memory: dict | None = None,
) -> str:
    if not raw_response:
        return raw_response
    if not ENABLE_RESPONSE_HUMANIZER or not OPENROUTER_API_KEY:
        return raw_response
    if _should_skip(raw_response):
        return raw_response

    user_content = (
        f"Outil : {tool or 'null'}\n"
        f"Action : {action or 'null'}\n"
        f"{_memory_context(memory)}\n\n"
        f"Réponse brute :\n{raw_response}\n\n"
        f"Message utilisateur :\n{user_message}\n\n"
        "Réponse humanisée :"
    )

    payload = _call_openrouter(
        {
            "model": OPENROUTER_MODEL,
            "temperature": 0.2,
            "max_tokens": 220,
            "messages": [
                {"role": "system", "content": HUMANIZER_PROMPT},
                {"role": "user", "content": user_content},
            ],
        }
    )
    if payload is None:
        return raw_response
    humanized = payload.get("choices", [{}])[0].get("message", {}).get("content", "")

    final_response = (humanized or "").strip()
    if not final_response:
        return raw_response
    if not _keeps_protected_data(raw_response, final_response):
        print("[RESPONSE_HUMANIZER SKIPPED] protected data changed or removed")
        return raw_response
    return final_response
