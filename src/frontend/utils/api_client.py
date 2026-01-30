"""HTTP client utilities for the frontend."""

from dataclasses import dataclass

import httpx

from src.frontend.utils.config import get_api_base_url


@dataclass
class APIError(Exception):
    """Custom exception for API errors."""

    status_code: int
    detail: str


def run_audit(
    brand: str,
    llm_provider: str,
    include_details: bool,
    access_code: str | None = None,
    openai_api_key: str | None = None,
    google_api_key: str | None = None,
) -> dict:
    """Call the /api/audit endpoint and return the result."""
    api_base_url = get_api_base_url()
    url = f"{api_base_url}/api/audit"

    payload = {
        "brand": brand,
        "llm_provider": llm_provider,
        "include_details": include_details,
        "access_code": access_code,
        "openai_api_key": openai_api_key,
        "google_api_key": google_api_key,
    }

    with httpx.Client(timeout=600.0) as client:
        response = client.post(url, json=payload)

    if response.status_code >= 400:
        detail = "Unknown error"
        try:
            detail = response.json().get("detail", detail)
        except Exception:  # noqa: BLE001 - fallback for non-JSON errors
            detail = response.text or detail

        raise APIError(status_code=response.status_code, detail=detail)

    return response.json()
