from fastapi import Header, HTTPException
import httpx
from config import SMARTHR_AGENT_TOKEN, SMARTHR_BACKEND_URL


async def verify_admin_guard(authorization: str | None = Header(default=None)) -> None:
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    expected = f"Bearer {SMARTHR_AGENT_TOKEN}"
    if authorization == expected:
        return
        
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(
                f"{SMARTHR_BACKEND_URL}/api/v1/auth/me",
                headers={"Authorization": authorization, "Accept": "application/json"},
                timeout=5.0
            )
            if res.status_code == 200:
                return
            raise HTTPException(status_code=401, detail=f"Backend Error: {res.status_code} - {res.text}")
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Connection Error: {str(e)}")
