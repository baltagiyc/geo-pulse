"""
Unit tests for brand context service.

Tests the brand context generation logic in isolation using mocks.
These tests are FAST, FREE, and run in CI/CD pipelines.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.graph.state import SearchResult
from src.core.services.llm.brand_context_service import (
    _format_search_results_for_context,
    generate_brand_context,
)


def test_format_search_results_for_context():
    """Test formatting of search results for context prompt."""
    search_results = [
        SearchResult(
            title="Brevo Official Site",
            url="https://www.brevo.com",
            snippet="Brevo is a CRM suite with email and automation tools.",
            domain="brevo.com",
        ),
        SearchResult(
            title="Brevo Reviews",
            url="https://www.g2.com/products/brevo",
            snippet="User reviews and ratings for Brevo.",
            domain="g2.com",
        ),
    ]

    formatted = _format_search_results_for_context(search_results)

    assert "Brevo Official Site" in formatted
    assert "https://www.brevo.com" in formatted
    assert "CRM suite" in formatted
    assert "Brevo Reviews" in formatted
    assert "https://www.g2.com/products/brevo" in formatted


def test_format_search_results_for_context_empty():
    """Test formatting with empty search results."""
    formatted = _format_search_results_for_context([])
    assert formatted == "No search results available."


@patch("src.core.services.llm.brand_context_service.search_with_tavily")
@patch("src.core.services.llm.brand_context_service.create_llm")
def test_generate_brand_context_with_mock(mock_create_llm, mock_search_with_tavily):
    """
    Test brand context generation with mocked search and LLM (for CI/CD).

    This test doesn't call the real API, so it's free and fast.
    """
    mock_search_with_tavily.return_value = [
        SearchResult(
            title="Brevo Official Site",
            url="https://www.brevo.com",
            snippet="Brevo is a CRM suite with email and automation tools.",
            domain="brevo.com",
        )
    ]

    mock_llm_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Brevo is a CRM and marketing automation platform."
    mock_llm_instance.invoke.return_value = mock_response
    mock_create_llm.return_value = mock_llm_instance

    result = generate_brand_context("Brevo")

    assert isinstance(result, str)
    assert "Brevo" in result

    mock_search_with_tavily.assert_called_once_with("Brevo company products services", max_results=5)
    mock_create_llm.assert_called_once_with("openai:gpt-4o-mini", temperature=0.3)
    mock_llm_instance.invoke.assert_called_once()


@patch("src.core.services.llm.brand_context_service.search_with_tavily")
@patch("src.core.services.llm.brand_context_service.create_llm")
def test_generate_brand_context_no_results(mock_create_llm, mock_search_with_tavily):
    """Test that empty search results return an empty context."""
    mock_search_with_tavily.return_value = []

    result = generate_brand_context("UnknownBrand")

    assert result == ""
    mock_search_with_tavily.assert_called_once_with("UnknownBrand company products services", max_results=5)
    mock_create_llm.assert_not_called()


if __name__ == "__main__":
    print("🧪 Unit Tests: Brand Context Service (with mocks)")
    print("-" * 50)

    test_format_search_results_for_context()
    print("✅ Format search results test passed")

    test_format_search_results_for_context_empty()
    print("✅ Empty search results formatting test passed")

    test_generate_brand_context_with_mock()
    print("✅ Mock brand context generation test passed (no API call, free)")

    test_generate_brand_context_no_results()
    print("✅ Empty results handling test passed")

    print("\n" + "-" * 50)
    print("✅ All unit tests passed!")
    print("\n💡 Note: For integration tests with real API calls,")
    print("   run: python tests/integration/test_brand_context_service.py")
