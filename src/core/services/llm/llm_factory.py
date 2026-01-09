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
import os

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


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
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    logger.info(f"Creating OpenAI LLM: {model} (temperature={temperature})")
    return ChatOpenAI(model=model, temperature=temperature, api_key=api_key)


# TODO: Add functions for other providers
# def _create_mistral_llm(model: str, temperature: float) -> ...
# def _create_ollama_llm(model: str, temperature: float) -> ...
