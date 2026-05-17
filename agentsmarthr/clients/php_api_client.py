from typing import Any, Dict, Optional
from urllib.parse import urljoin

import httpx
from contextvars import ContextVar

from config import SMARTHR_BACKEND_TOKEN, SMARTHR_BACKEND_URL

request_token: ContextVar[str] = ContextVar("request_token", default="")


class SmartHRApiError(Exception):
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class PhpApiClient:
    def __init__(
        self,
        base_url: str = SMARTHR_BACKEND_URL,
        token: str = SMARTHR_BACKEND_TOKEN,
        timeout: int = 15,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        token = request_token.get() or f"Bearer {self.token}"
        return {
            "Authorization": token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _url(self, path: str) -> str:
        return urljoin(f"{self.base_url}/", path.lstrip("/"))

    def _request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        try:
            response = httpx.request(
                method,
                self._url(path),
                headers=self._headers(),
                json=json,
                timeout=self.timeout,
            )
        except httpx.RequestError as error:
            raise SmartHRApiError("Backend inaccessible", details=str(error)) from error

        if response.status_code == 401:
            raise SmartHRApiError("Unauthorized", status_code=401, details=response.text)
        if response.status_code == 404:
            raise SmartHRApiError("Not Found", status_code=404, details=response.text)
        if response.status_code >= 400:
            raise SmartHRApiError(
                f"Laravel API error ({response.status_code})",
                status_code=response.status_code,
                details=response.text,
            )

        if not response.content:
            return None

        try:
            return response.json()
        except ValueError:
            return response.text

    def get(self, path: str) -> Any:
        return self._request("GET", path)

    def post(self, path: str, json: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("POST", path, json=json)

    def patch(self, path: str, json: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("PATCH", path, json=json)

    def delete(self, path: str) -> Any:
        return self._request("DELETE", path)


default_client = PhpApiClient()


def get(path: str) -> Any:
    return default_client.get(path)


def post(path: str, json: Optional[Dict[str, Any]] = None) -> Any:
    return default_client.post(path, json=json)


def patch(path: str, json: Optional[Dict[str, Any]] = None) -> Any:
    return default_client.patch(path, json=json)


def delete(path: str) -> Any:
    return default_client.delete(path)
