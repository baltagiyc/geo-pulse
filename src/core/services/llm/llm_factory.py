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
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from src.core.config import get_google_api_key, get_openai_api_key

logger = logging.getLogger(__name__)

# Mapping of LLM provider names to their factory format
# This ensures we convert user-friendly names (e.g., "gpt-4", "gemini") to factory format (e.g., "openai:gpt-4")
LLM_PROVIDER_TO_FACTORY_MAPPING = {
    # OpenAI models (latest first)
    "gpt-5.2-pro": "openai:gpt-5.2-pro",  # ChatGPT Pro mode (Max reasoning)
    "gpt-5.2": "openai:gpt-5.2",  # ChatGPT Plus/Free mode (Flagship model)
    "gpt-5.1": "openai:gpt-5.1",  # High-performance 2025 model
    "gpt-5": "openai:gpt-5",  # Advanced reasoning 2025 model
    "o3": "openai:o3",  # Latest reasoning model (Plus/Pro)
    "o1": "openai:o1",  # OpenAI's primary reasoning model
    "gpt-4.5": "openai:gpt-4.5",  # API-optimized previous generation
    "gpt-4.1": "openai:gpt-4.1",  # API-optimized previous generation
    "gpt-4.1-mini": "openai:gpt-4.1-mini",  # Lightweight API-optimized model
    "gpt-4o": "openai:gpt-4o",  # Classic flagship
    "gpt-4o-mini": "openai:gpt-4o-mini",
    "chatgpt": "openai:gpt-5.2",
    "gpt-4": "openai:gpt-4",
    "gpt-3.5-turbo": "openai:gpt-3.5-turbo",
    "gemini": "google:gemini-3-pro-preview",  # Default Gemini (Pro mode - most intelligent, Dec 2025)
    "gemini-pro": "google:gemini-3-pro-preview",  # Pro mode - most intelligent model
    "gemini-3-pro": "google:gemini-3-pro-preview",  # Pro mode - most intelligent model
    # 2. Latest & Fastest (December 2025)
    "gemini-flash": "google:gemini-3-flash-preview",  # Flash mode - fast and balanced (Dec 2025)
    "gemini-3-flash": "google:gemini-3-flash-preview",  # Flash mode - fast and balanced
    # 3. Stable & Reliable (June 2025)
    "gemini-reasoning": "google:gemini-2.5-pro",  # Reasoning mode - stable release (June 2025)
    "gemini-2.5-pro": "google:gemini-2.5-pro",  # Stable Pro model (June 2025)
    "gemini-2.5-flash": "google:gemini-2.5-flash",  # Stable Flash model (June 2025) - fast and reliable
    # Anthropic models (to be implemented)
    "claude": "",  # TODO: Change to "anthropic:claude" when implemented
    "default": "openai:gpt-5.2",
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

    default_llm = LLM_PROVIDER_TO_FACTORY_MAPPING["default"]
    if simulation_llm is None:
        logger.info(f"No factory mapping for '{llm_provider}'. Using default: '{default_llm}'")
        return default_llm

    if simulation_llm == "":
        logger.info(f"LLM provider '{llm_provider}' not yet implemented. Using default: '{default_llm}'")
        return default_llm

    return simulation_llm


def create_llm(
    llm_spec: str = "openai:gpt-4o-mini",
    temperature: float = 0.7,
    api_key: str | None = None,
) -> BaseChatModel:
    """
    Create an LLM instance based on provider and model specification.

    Format: "provider:model"


    Args:
        llm_spec: LLM specification in format "provider:model" (default: "openai:gpt-4o-mini")
        temperature: Temperature for the LLM (default: 0.7)
        api_key: Optional API key override (OpenAI or Google depending on provider)

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
        return _create_openai_llm(model, temperature, api_key=api_key)
    elif provider == "google":
        return _create_google_llm(model, temperature, api_key=api_key)
    elif provider == "mistral":
        # TODO: Implement Mistral support
        raise ValueError("Mistral provider not yet implemented. Supported providers: openai, google")
    elif provider == "ollama":
        # TODO: Implement Ollama support
        raise ValueError("Ollama provider not yet implemented. Supported providers: openai, google")
    else:
        raise ValueError(f"Unsupported provider: {provider}. Supported providers: openai, google")


def _create_openai_llm(model: str, temperature: float, api_key: str | None = None) -> ChatOpenAI:
    """
    Create an OpenAI LLM instance.

    Args:
        model: OpenAI model name (e.g., "gpt-5.2", "gpt-5")
        temperature: Temperature for the LLM
        api_key: Optional OpenAI API key override

    Returns:
        ChatOpenAI instance

    Raises:
        ValueError: If OPENAI_API_KEY is missing
    """
    api_key = api_key or get_openai_api_key()

    logger.info(f"Creating OpenAI LLM: {model} (temperature={temperature})")
    return ChatOpenAI(model=model, temperature=temperature, api_key=api_key)


def _create_google_llm(model: str, temperature: float, api_key: str | None = None) -> ChatGoogleGenerativeAI:
    """
    Create a Google Gemini LLM instance.

    Args:
        model: Google Gemini model name (e.g., "gemini-3-pro-preview", "gemini-3-flash-preview", "gemini-2.5-pro")
        temperature: Temperature for the LLM
        api_key: Optional Google API key override

    Returns:
        ChatGoogleGenerativeAI instance

    Raises:
        ValueError: If GOOGLE_API_KEY is missing
    """
    api_key = api_key or get_google_api_key()

    logger.info(f"Creating Google Gemini LLM: {model} (temperature={temperature})")
    return ChatGoogleGenerativeAI(model=model, temperature=temperature, google_api_key=api_key)


# TODO: Add functions for other providers
# def _create_mistral_llm(model: str, temperature: float) -> ...
# def _create_ollama_llm(model: str, temperature: float) -> ...
