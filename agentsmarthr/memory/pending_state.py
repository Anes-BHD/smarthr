from copy import deepcopy
from typing import Any, Dict, Optional


_PENDING_STATES: Dict[str, Dict[str, Any]] = {}


def get_pending_state(session_id: str) -> Optional[Dict[str, Any]]:
    state = _PENDING_STATES.get(session_id)
    return deepcopy(state) if state else None


def set_pending_state(session_id: str, state: Dict[str, Any]) -> None:
    _PENDING_STATES[session_id] = deepcopy(state)


def clear_pending_state(session_id: str) -> None:
    _PENDING_STATES.pop(session_id, None)
