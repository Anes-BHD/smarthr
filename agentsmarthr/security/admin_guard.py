from fastapi import Header, HTTPException

from config import SMARTHR_AGENT_TOKEN


def verify_admin_guard(authorization: str | None = Header(default=None)) -> None:
    expected = f"Bearer {SMARTHR_AGENT_TOKEN}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")
