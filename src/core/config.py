"""
Centralized configuration defaults for GEO Pulse.

These values act as sane defaults for the graph and services.
They can be overridden by API inputs or config mechanisms.
"""

DEFAULT_NUM_QUESTIONS = 2
DEFAULT_MAX_SEARCH_RESULTS = 5

QUESTION_LLM_TEMPERATURE = 0.7
SIMULATION_LLM_TEMPERATURE = 0.7
CONTEXT_LLM_TEMPERATURE = 0.3
ANALYSIS_LLM_TEMPERATURE = 0.3

DEFAULT_QUESTION_LLM = "openai:gpt-4o-mini"
DEFAULT_CONTEXT_LLM = "openai:gpt-4o-mini"
DEFAULT_SIMULATION_LLM = "openai:gpt-4"
DEFAULT_ANALYSIS_LLM = "openai:gpt-4"
