"""Frontend configuration utilities."""

import os


def get_api_base_url() -> str:
    """Return the base URL for the FastAPI backend."""
    return os.getenv("API_URL", "http://localhost:8000").rstrip("/")
