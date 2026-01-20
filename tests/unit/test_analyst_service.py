"""
Unit tests for brand visibility analyst service.

Tests the analysis logic in isolation using mocks.
These tests are FAST, FREE, and run in CI/CD pipelines.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.config import ANALYSIS_LLM_TEMPERATURE, DEFAULT_ANALYSIS_LLM
from src.core.graph.state import Recommendation
from src.core.services.analysis.analyst_service import (
    AnalysisResponse,
    _extract_domains_from_sources,
    _format_llm_responses_for_analysis,
    analyze_brand_visibility,
)


def test_extract_domains_from_sources():
    """Test domain extraction using SearchResult Pydantic model."""
    search_results = {
        "Question 1": [
            {
                "title": "Nike",
                "url": "https://nike.com",
                "snippet": "...",
                "domain": "nike.com",
            },
            {
                "title": "Adidas",
                "url": "https://adidas.com",
                "snippet": "...",
                "domain": "adidas.com",
            },
        ],
        "Question 2": [
            {
                "title": "Nike",
                "url": "https://nike.com",
                "snippet": "...",
                "domain": "nike.com",
            },
        ],
    }

    domain_counts = _extract_domains_from_sources(search_results)

    assert domain_counts["nike.com"] == 2
    assert domain_counts["adidas.com"] == 1


def test_format_llm_responses_for_analysis():
    """Test formatting of LLM responses with sources."""
    questions = ["What are the best Nike products?", "What are Nike's weaknesses?"]
    llm_responses = {
        "What are the best Nike products?": {
            "llm_name": "gpt-4",
            "response": "Nike offers excellent products...",
            "sources": ["https://nike.com", "https://reviews.com"],
        },
        "What are Nike's weaknesses?": {
            "llm_name": "gpt-4",
            "response": "Nike has some pricing concerns...",
            "sources": ["https://reddit.com"],
        },
    }
    search_results = {
        "What are the best Nike products?": [
            {
                "title": "Nike",
                "url": "https://nike.com",
                "snippet": "...",
                "domain": "nike.com",
            },
            {
                "title": "Reviews",
                "url": "https://reviews.com",
                "snippet": "...",
                "domain": "reviews.com",
            },
            {
                "title": "Amazon",
                "url": "https://amazon.com",
                "snippet": "...",
                "domain": "amazon.com",
            },
        ],
        "What are Nike's weaknesses?": [
            {
                "title": "Reddit",
                "url": "https://reddit.com",
                "snippet": "...",
                "domain": "reddit.com",
            },
        ],
    }

    formatted = _format_llm_responses_for_analysis(questions, llm_responses, search_results)

    # Check that questions are included
    assert "What are the best Nike products?" in formatted
    assert "What are Nike's weaknesses?" in formatted

    # Check that responses are included
    assert "Nike offers excellent products" in formatted
    assert "Nike has some pricing concerns" in formatted

    # Check that sources are categorized
    assert "SOURCES CITED BY LLM" in formatted
    assert "AVAILABLE SOURCES NOT CITED" in formatted
    assert "nike.com" in formatted
    assert "amazon.com" in formatted  # Should be in non-cited


@patch("src.core.services.analysis.analyst_service.create_llm")
def test_analyze_brand_visibility_with_mock(mock_create_llm):
    """
    Test brand visibility analysis with mocked LLM (for CI/CD).

    This test doesn't call the real API, so it's free and fast.
    """
    # Mock the LLM response
    mock_llm_instance = MagicMock()
    mock_structured_llm = MagicMock()

    # Mock the structured output response
    mock_response = AnalysisResponse(
        reputation_score=0.75,
        recommendations=[
            Recommendation(
                title="Address pricing concerns",
                description="Improve pricing strategy based on negative feedback",
                priority="high",
            ),
            Recommendation(
                title="Improve visibility on Reddit",
                description="Reddit appears in search results but is not cited",
                priority="medium",
            ),
        ],
    )
    mock_structured_llm.invoke.return_value = mock_response

    # Mock the chain: create_llm() -> with_structured_output() -> invoke()
    mock_llm_instance.with_structured_output.return_value = mock_structured_llm
    mock_create_llm.return_value = mock_llm_instance

    # Prepare test data
    questions = ["What are the best Nike products?", "What are Nike's weaknesses?"]
    llm_responses = {
        "What are the best Nike products?": {
            "llm_name": "gpt-4",
            "response": "Nike offers excellent products...",
            "sources": ["https://nike.com"],
        },
        "What are Nike's weaknesses?": {
            "llm_name": "gpt-4",
            "response": "Nike has pricing concerns...",
            "sources": ["https://reddit.com"],
        },
    }
    search_results = {
        "What are the best Nike products?": [
            {
                "title": "Nike",
                "url": "https://nike.com",
                "snippet": "...",
                "domain": "nike.com",
            },
        ],
        "What are Nike's weaknesses?": [
            {
                "title": "Reddit",
                "url": "https://reddit.com",
                "snippet": "...",
                "domain": "reddit.com",
            },
        ],
    }

    # Mock API key
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        score, recommendations = analyze_brand_visibility(
            brand="Nike",
            questions=questions,
            llm_responses=llm_responses,
            search_results=search_results,
        )

    # Verify results
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0
    assert score == 0.75
    assert isinstance(recommendations, list)
    assert len(recommendations) == 2
    assert all(isinstance(r, Recommendation) for r in recommendations)
    assert recommendations[0].title == "Address pricing concerns"
    assert recommendations[0].priority == "high"

    # Verify LLM was called correctly
    mock_create_llm.assert_called_once_with(llm_spec=DEFAULT_ANALYSIS_LLM, temperature=ANALYSIS_LLM_TEMPERATURE)
    mock_structured_llm.invoke.assert_called_once()


@patch("src.core.services.analysis.analyst_service.create_llm")
def test_analyze_brand_visibility_empty_data(mock_create_llm):
    """Test that empty data is handled correctly."""
    mock_llm_instance = MagicMock()
    mock_structured_llm = MagicMock()

    mock_response = AnalysisResponse(reputation_score=0.0, recommendations=[])
    mock_structured_llm.invoke.return_value = mock_response
    mock_llm_instance.with_structured_output.return_value = mock_structured_llm
    mock_create_llm.return_value = mock_llm_instance

    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        score, recommendations = analyze_brand_visibility(
            brand="Nike", questions=[], llm_responses={}, search_results={}
        )

    assert score == 0.0
    assert len(recommendations) == 0


if __name__ == "__main__":
    print("🧪 Unit Tests: Brand Visibility Analyst Service (with mocks)")
    print("-" * 50)

    test_extract_domains_from_sources()
    print("✅ Extract domains from sources test passed")

    test_format_llm_responses_for_analysis()
    print("✅ Format LLM responses for analysis test passed")

    test_analyze_brand_visibility_with_mock()
    print("✅ Mock brand visibility analysis test passed (no API call, free)")

    test_analyze_brand_visibility_empty_data()
    print("✅ Empty data handling test passed")

    print("\n" + "-" * 50)
    print("✅ All unit tests passed!")
    print("\n💡 Note: For integration tests with real API calls,")
    print("   run: python tests/integration/test_analyst_service.py")
