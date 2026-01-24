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
    # OpenAI models (latest first)
    "gpt-5.2": "openai:gpt-5.2",  # Latest model (2025)
    "gpt-5": "openai:gpt-5",  # Advanced model with reasoning capabilities
    "gpt-4.1": "openai:gpt-4.1",  # API-optimized model (better than GPT-4o)
    "gpt-4.1-mini": "openai:gpt-4.1-mini",  # Lightweight API-optimized model
    "gpt-4o": "openai:gpt-4o",  # Flagship model with multimodal support
    "gpt-4o-mini": "openai:gpt-4o-mini",  # Lightweight version
    "chatgpt": "openai:gpt-5.2",  # Default ChatGPT experience (uses latest model)
    "gpt-4": "openai:gpt-4",  # Previous high-intelligence model
    "gpt-3.5-turbo": "openai:gpt-3.5-turbo",  # Fast model for routine tasks
    # Google models (to be implemented)
    "gemini": "",  # TODO: Change to "google:gemini" when implemented
    "gemini-pro": "",  # TODO: Change to "google:gemini-pro" when implemented
    # Anthropic models (to be implemented)
    "claude": "",  # TODO: Change to "anthropic:claude" when implemented
    "default": "openai:gpt-5",
}


def get_simulation_llm_for_provider(llm_provider: str) -> str:
    """
    Convert LLM provider name to factory format for simulation.

    This function maps user-friendly provider names (e.g., "gpt-5.2", "gpt-4o", "gemini")
    to factory format (e.g., "openai:gpt-5.2", "openai:gpt-4o", "google:gemini").

    Used when simulating what a specific LLM (ChatGPT, Gemini, etc.) would respond.
    Returns the actual model to use for simulation.

    Args:
        llm_provider: LLM provider name (e.g., "gpt-5.2", "gpt-4o", "gemini", "claude")

    Returns:
        Factory format LLM specification (e.g., "openai:gpt-5.2", "openai:gpt-4o", "google:gemini")
    """
    provider_lower = llm_provider.lower().strip()

    simulation_llm = LLM_PROVIDER_TO_FACTORY_MAPPING.get(provider_lower)

    # If mapping not found, use default
    if simulation_llm is None:
        logger.info(f"No factory mapping for '{llm_provider}'. Using default: 'openai:gpt-5'")
        return LLM_PROVIDER_TO_FACTORY_MAPPING["default"]

    # If mapping is empty string, provider not yet implemented (e.g., gemini, claude)
    if simulation_llm == "":
        logger.info(
            f"LLM provider '{llm_provider}' not yet implemented. Using default: 'openai:gpt-5'"
        )
        return LLM_PROVIDER_TO_FACTORY_MAPPING["default"]

    # Return the actual mapping (e.g., "gpt-5.2" -> "openai:gpt-5.2")
    return simulation_llm


def create_llm(llm_spec: str = "openai:gpt-4o-mini", temperature: float = 0.7) -> BaseChatModel:
    """
    Create an LLM instance based on provider and model specification.

    Format: "provider:model"


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
        model: OpenAI model name (e.g., "gpt-5.2", "gpt-5")
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
