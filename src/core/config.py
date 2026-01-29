"""
Centralized configuration defaults for GEO Pulse.

These values act as sane defaults for the graph and services.
They can be overridden by API inputs or config mechanisms.
"""

import os
import tempfile


def _get_env_int(key: str, default: int) -> int:
    """Helper to read integer from environment."""
    raw = os.getenv(key)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _get_env_float(key: str, default: float) -> float:
    """Helper to read float from environment."""
    raw = os.getenv(key)
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


DEFAULT_NUM_QUESTIONS = _get_env_int("DEFAULT_NUM_QUESTIONS", 3)
DEFAULT_MAX_SEARCH_RESULTS = _get_env_int("DEFAULT_MAX_SEARCH_RESULTS", 5)

QUESTION_LLM_TEMPERATURE = _get_env_float("QUESTION_LLM_TEMPERATURE", 0.7)
SIMULATION_LLM_TEMPERATURE = _get_env_float("SIMULATION_LLM_TEMPERATURE", 0.7)
CONTEXT_LLM_TEMPERATURE = _get_env_float("CONTEXT_LLM_TEMPERATURE", 0.3)
ANALYSIS_LLM_TEMPERATURE = _get_env_float("ANALYSIS_LLM_TEMPERATURE", 0.3)

DEFAULT_QUESTION_LLM = os.getenv("DEFAULT_QUESTION_LLM", "openai:gpt-4.1-mini")
DEFAULT_CONTEXT_LLM = os.getenv("DEFAULT_CONTEXT_LLM", "openai:gpt-4.1-mini")
DEFAULT_SIMULATION_LLM = os.getenv("DEFAULT_SIMULATION_LLM", "openai:gpt-5.2")
DEFAULT_ANALYSIS_LLM = os.getenv("DEFAULT_ANALYSIS_LLM", "openai:gpt-5.2")
DEFAULT_INTERNAL_GEMINI_LLM = os.getenv("DEFAULT_INTERNAL_GEMINI_LLM", "google:gemini-2.5-flash")

ACCESS_CODE_MAX_AUDITS_DEFAULT = 3


def get_openai_api_key() -> str:
    """
    Retrieve the OpenAI API key from environment variables.

    Central helper to avoid duplicating os.getenv logic across services.
    Raises a clear ValueError if the key is missing.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    return api_key


def get_tavily_api_key() -> str:
    """
    Retrieve the Tavily API key from environment variables.

    Central helper to avoid duplicating os.getenv logic across services.
    Raises a clear ValueError if the key is missing.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY not found in environment variables")
    return api_key


def get_google_api_key() -> str:
    """
    Retrieve the Google API key from environment variables.

    Central helper to avoid duplicating os.getenv logic across services.
    Raises a clear ValueError if the key is missing.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    return api_key


def get_access_codes() -> set[str]:
    """
    Retrieve access codes from environment variables.

    Expected format: ACCESS_CODES="CODE1,CODE2,CODE3"
    """
    raw_codes = os.getenv("ACCESS_CODES", "")
    return {code.strip() for code in raw_codes.split(",") if code.strip()}


def get_access_code_max_audits() -> int:
    """Return the maximum audits allowed per access code."""
    raw_value = os.getenv("ACCESS_CODE_MAX_AUDITS")
    if not raw_value:
        return ACCESS_CODE_MAX_AUDITS_DEFAULT
    try:
        value = int(raw_value)
    except ValueError:
        return ACCESS_CODE_MAX_AUDITS_DEFAULT
    return max(value, 0)


def get_access_code_db_path() -> str:
    """Return the SQLite path used for access code quotas."""
    env_path = os.getenv("ACCESS_CODE_DB_PATH")
    if env_path:
        return env_path
    if is_hf_space():
        return "/data/geo_pulse_access_codes.db"
    return os.path.join(tempfile.gettempdir(), "geo_pulse_access_codes.db")


def is_hf_space() -> bool:
    """Return True when running in Hugging Face Spaces."""
    return bool(os.getenv("SPACE_ID"))
