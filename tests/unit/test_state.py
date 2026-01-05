"""
Unit tests for State models.

These tests verify that Pydantic models validate correctly
and that the State structure is correct.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from pydantic import ValidationError

from src.core.graph.state import LLMResponse, Recommendation, SearchResult


def test_search_result_validation():
    """Test that SearchResult validates correctly."""
    # Valid SearchResult
    result = SearchResult(
        title="Nike Air Zoom",
        url="https://nike.com",
        snippet="Best running shoes",
        domain="nike.com",
    )
    assert result.title == "Nike Air Zoom"
    assert result.domain == "nike.com"

    # Invalid SearchResult (missing required fields)
    try:
        SearchResult(title="Nike")  # Missing url, snippet, domain
        assert False, "Should have raised ValidationError"
    except ValidationError:
        assert True


def test_llm_response_validation():
    """Test that LLMResponse validates correctly."""
    # Valid LLMResponse
    response = LLMResponse(
        llm_name="chatgpt",
        response="Nike is a great brand",
        sources=["https://nike.com"],
    )
    assert response.llm_name == "chatgpt"
    assert len(response.sources) == 1

    # LLMResponse with default empty sources
    response_empty = LLMResponse(llm_name="gemini", response="Test response")
    assert response_empty.sources == []


def test_recommendation_validation():
    """Test that Recommendation validates correctly."""
    # Valid Recommendation
    rec = Recommendation(title="Improve SEO", description="Add more keywords", priority="high")
    assert rec.priority == "high"

    # Recommendation with default priority
    rec_default = Recommendation(title="Test", description="Test description")
    assert rec_default.priority == "medium"


if __name__ == "__main__":
    test_search_result_validation()
    test_llm_response_validation()
    test_recommendation_validation()
    print("✅ All unit tests passed!")
