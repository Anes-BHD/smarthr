import json
import os
from copy import deepcopy
from typing import Any, Dict, Optional

_TTL = 600  # 10 minutes

try:
    import redis as _redis_lib

    _redis_url = os.getenv("REDIS_URL") or (
        f"redis://:{os.getenv('REDIS_PASSWORD', '')}@"
        f"{os.getenv('REDIS_HOST', 'smarthr-redis')}:"
        f"{os.getenv('REDIS_PORT', '6379')}/0"
    )
    _redis: Optional[Any] = _redis_lib.Redis.from_url(_redis_url, decode_responses=True, socket_connect_timeout=2)
    _redis.ping()
except Exception:
    _redis = None

_LOCAL: Dict[str, Dict[str, Any]] = {}


def _key(session_id: str) -> str:
    return f"agent:pending:{session_id}"


def get_pending_state(session_id: str) -> Optional[Dict[str, Any]]:
    if _redis:
        raw = _redis.get(_key(session_id))
        return json.loads(raw) if raw else None
    state = _LOCAL.get(session_id)
    return deepcopy(state) if state else None


def set_pending_state(session_id: str, state: Dict[str, Any]) -> None:
    if _redis:
        _redis.setex(_key(session_id), _TTL, json.dumps(state))
        return
    _LOCAL[session_id] = deepcopy(state)


def clear_pending_state(session_id: str) -> None:
    if _redis:
        _redis.delete(_key(session_id))
        return
    _LOCAL.pop(session_id, None)
