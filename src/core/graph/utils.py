"""
Utility helpers for the LangGraph state.

Provides conversions between Pydantic models and dicts used in GEOState.
"""

from src.core.graph.state import LLMResponse, Recommendation, SearchResult


def search_results_models_to_dicts(results: list[SearchResult]) -> list[dict]:
    """Convert SearchResult models to dicts for state storage."""
    return [result.model_dump() for result in results]


def search_results_dicts_to_models(results: list[dict]) -> list[SearchResult]:
    """Convert SearchResult dicts from state into models."""
    return [SearchResult.model_validate(result) for result in results]


def llm_response_model_to_dict(response: LLMResponse) -> dict:
    """Convert LLMResponse model to dict for state storage."""
    return response.model_dump()


def llm_response_dict_to_model(response: dict) -> LLMResponse:
    """Convert LLMResponse dict from state into a model."""
    return LLMResponse.model_validate(response)


def recommendations_models_to_dicts(recommendations: list[Recommendation]) -> list[dict]:
    """Convert Recommendation models to dicts for state storage."""
    return [recommendation.model_dump() for recommendation in recommendations]


def recommendations_dicts_to_models(recommendations: list[dict]) -> list[Recommendation]:
    """Convert Recommendation dicts from state into models."""
    return [Recommendation.model_validate(recommendation) for recommendation in recommendations]
