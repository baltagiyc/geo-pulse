"""Frontend configuration utilities."""

import os


def get_api_base_url() -> str:
    """Return the base URL for the FastAPI backend."""
    return os.getenv("API_URL", "http://localhost:8000").rstrip("/")


def is_hf_space() -> bool:
    """Return True when running in Hugging Face Spaces."""
    return bool(os.getenv("SPACE_ID"))
