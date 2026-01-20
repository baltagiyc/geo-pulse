"""
LLM Factory.

Generic factory pattern for creating LLM instances from different providers.
This factory can be used for any LLM operation (question generation, simulation, analysis, etc.).

Supports OpenAI, Mistral, Ollama, and other providers.
Format: "provider:model" (e.g., "openai:gpt-4o-mini", "mistral:mistral-small", "ollama:llama2")

This is a generic utility that can be reused across different services:
- question_generator: LLM for generating questions
- llm_simulator: LLM for simulating responses
- analyst_service: LLM for analyzing responses
"""

import logging

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from src.core.config import get_openai_api_key

logger = logging.getLogger(__name__)

# Mapping of LLM provider names to their factory format
# This ensures we convert user-friendly names (e.g., "gpt-4", "gemini") to factory format (e.g., "openai:gpt-4")
LLM_PROVIDER_TO_FACTORY_MAPPING = {
    # OpenAI models
    "chatgpt": "openai:gpt-4",
    "gpt-4": "openai:gpt-4",
    "gpt-4o": "openai:gpt-4o",
    "gpt-4o-mini": "openai:gpt-4o-mini",
    "gpt-3.5-turbo": "openai:gpt-3.5-turbo",
    # Google models (to be implemented)
    "gemini": "openai:gpt-4",  # TODO: Change to "google:gemini" when implemented
    "gemini-pro": "openai:gpt-4",  # TODO: Change to "google:gemini-pro" when implemented
    # Anthropic models (to be implemented)
    "claude": "openai:gpt-4",  # TODO: Change to "anthropic:claude" when implemented
    "claude-3": "openai:gpt-4",  # TODO: Change to "anthropic:claude-3" when implemented
    # Default fallback
    "default": "openai:gpt-4",
}


def get_simulation_llm_for_provider(llm_provider: str) -> str:
    """
    Convert LLM provider name to factory format.

    This function maps user-friendly provider names (e.g., "gpt-4", "gemini")
    to factory format (e.g., "openai:gpt-4", "google:gemini").

    For now, returns "openai:gpt-4" for all providers as default.
    Future: will return the correct factory format based on the mapping above.

    Args:
        llm_provider: LLM provider name (e.g., "gpt-4", "gemini", "claude")

    Returns:
        Factory format LLM specification (e.g., "openai:gpt-4", "google:gemini")
    """
    provider_lower = llm_provider.lower().strip()

    simulation_llm = LLM_PROVIDER_TO_FACTORY_MAPPING.get(provider_lower)

    if simulation_llm is None:
        logger.info(f"No factory mapping for '{llm_provider}'. Using default: 'openai:gpt-4'")
        return LLM_PROVIDER_TO_FACTORY_MAPPING["default"]

    # TODO: Once other providers (Google, Anthropic) are implemented, return the mapped value
    # For now, always return OpenAI as default
    if simulation_llm != LLM_PROVIDER_TO_FACTORY_MAPPING["default"]:
        logger.info(
            f"LLM provider '{llm_provider}' should use '{simulation_llm}', "
            f"but using 'openai:gpt-4' as default (not yet implemented)"
        )
    return LLM_PROVIDER_TO_FACTORY_MAPPING["default"]


def create_llm(llm_spec: str = "openai:gpt-4o-mini", temperature: float = 0.7) -> BaseChatModel:
    """
    Create an LLM instance based on provider and model specification.

    Format: "provider:model"
    Examples:
        - "openai:gpt-4o-mini"
        - "openai:gpt-4"
        - "mistral:mistral-small" (to be implemented)
        - "ollama:llama2" (to be implemented)

    Args:
        llm_spec: LLM specification in format "provider:model" (default: "openai:gpt-4o-mini")
        temperature: Temperature for the LLM (default: 0.7)

    Returns:
        BaseChatModel instance

    Raises:
        ValueError: If provider is not supported or API key is missing
        ValueError: If llm_spec format is invalid
    """
    if ":" not in llm_spec:
        raise ValueError(f"Invalid llm_spec format: {llm_spec}. Expected format: 'provider:model'")

    provider, model = llm_spec.split(":", 1)

    if provider == "openai":
        return _create_openai_llm(model, temperature)
    elif provider == "mistral":
        # TODO: Implement Mistral support
        raise ValueError("Mistral provider not yet implemented. Supported providers: openai")
    elif provider == "ollama":
        # TODO: Implement Ollama support
        raise ValueError("Ollama provider not yet implemented. Supported providers: openai")
    else:
        raise ValueError(f"Unsupported provider: {provider}. Supported providers: openai")


def _create_openai_llm(model: str, temperature: float) -> ChatOpenAI:
    """
    Create an OpenAI LLM instance.

    Args:
        model: OpenAI model name (e.g., "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo")
        temperature: Temperature for the LLM

    Returns:
        ChatOpenAI instance

    Raises:
        ValueError: If OPENAI_API_KEY is missing
    """
    api_key = get_openai_api_key()

    logger.info(f"Creating OpenAI LLM: {model} (temperature={temperature})")
    return ChatOpenAI(model=model, temperature=temperature, api_key=api_key)


# TODO: Add functions for other providers
# def _create_mistral_llm(model: str, temperature: float) -> ...
# def _create_ollama_llm(model: str, temperature: float) -> ...
