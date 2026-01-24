"""
Centralized configuration defaults for GEO Pulse.

These values act as sane defaults for the graph and services.
They can be overridden by API inputs or config mechanisms.
"""

import os

DEFAULT_NUM_QUESTIONS = 2
DEFAULT_MAX_SEARCH_RESULTS = 5

QUESTION_LLM_TEMPERATURE = 0.7
SIMULATION_LLM_TEMPERATURE = 0.7
CONTEXT_LLM_TEMPERATURE = 0.3
ANALYSIS_LLM_TEMPERATURE = 0.3

DEFAULT_QUESTION_LLM = "openai:gpt-4.1-mini"  
DEFAULT_CONTEXT_LLM = "openai:gpt-4.1-mini"  
DEFAULT_SIMULATION_LLM = "openai:gpt-5.2"
DEFAULT_ANALYSIS_LLM = "openai:gpt-4.1"  


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
