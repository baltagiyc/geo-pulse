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

from src.core.config import CONTEXT_LLM_TEMPERATURE, DEFAULT_CONTEXT_LLM, DEFAULT_MAX_SEARCH_RESULTS
from src.core.graph.state import SearchResult
from src.core.services.llm.brand_context_service import generate_brand_context
from src.core.services.utils import format_search_results_for_prompt


def test_format_search_results_for_prompt():
    """Test formatting of search results for prompt."""
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

    formatted = format_search_results_for_prompt(search_results)

    assert "Brevo Official Site" in formatted
    assert "https://www.brevo.com" in formatted
    assert "CRM suite" in formatted
    assert "Brevo Reviews" in formatted
    assert "https://www.g2.com/products/brevo" in formatted


def test_format_search_results_for_prompt_empty():
    """Test formatting with empty search results."""
    formatted = format_search_results_for_prompt([])
    assert formatted == "No search results available."


@patch("src.core.services.llm.brand_context_service.create_search_tool")
@patch("src.core.services.llm.brand_context_service.create_llm")
def test_generate_brand_context_with_mock(mock_create_llm, mock_create_search_tool):
    """
    Test brand context generation with mocked search and LLM (for CI/CD).

    This test doesn't call the real API, so it's free and fast.
    """
    mock_search_function = MagicMock()
    mock_search_function.return_value = [
        SearchResult(
            title="Brevo Official Site",
            url="https://www.brevo.com",
            snippet="Brevo is a CRM suite with email and automation tools.",
            domain="brevo.com",
        )
    ]
    mock_create_search_tool.return_value = mock_search_function

    mock_llm_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Brevo is a CRM and marketing automation platform."
    mock_llm_instance.invoke.return_value = mock_response
    mock_create_llm.return_value = mock_llm_instance

    result = generate_brand_context("Brevo")

    assert isinstance(result, str)
    assert "Brevo" in result

    mock_create_search_tool.assert_called_once_with("tavily")
    mock_search_function.assert_called_once_with(
        "Brevo company products services",
        max_results=DEFAULT_MAX_SEARCH_RESULTS,
    )
    mock_create_llm.assert_called_once_with(DEFAULT_CONTEXT_LLM, temperature=CONTEXT_LLM_TEMPERATURE)
    mock_llm_instance.invoke.assert_called_once()


@patch("src.core.services.llm.brand_context_service.create_search_tool")
@patch("src.core.services.llm.brand_context_service.create_llm")
def test_generate_brand_context_no_results(mock_create_llm, mock_create_search_tool):
    """Test that empty search results return an empty context."""
    mock_search_function = MagicMock()
    mock_search_function.return_value = []
    mock_create_search_tool.return_value = mock_search_function

    result = generate_brand_context("UnknownBrand")

    assert result == ""
    mock_create_search_tool.assert_called_once_with("tavily")
    mock_search_function.assert_called_once_with(
        "UnknownBrand company products services",
        max_results=DEFAULT_MAX_SEARCH_RESULTS,
    )
    mock_create_llm.assert_not_called()


if __name__ == "__main__":
    print("🧪 Unit Tests: Brand Context Service (with mocks)")
    print("-" * 50)

    test_format_search_results_for_prompt()
    print("✅ Format search results test passed")

    test_format_search_results_for_prompt_empty()
    print("✅ Empty search results formatting test passed")

    test_generate_brand_context_with_mock()
    print("✅ Mock brand context generation test passed (no API call, free)")

    test_generate_brand_context_no_results()
    print("✅ Empty results handling test passed")

    print("\n" + "-" * 50)
    print("✅ All unit tests passed!")
    print("\n💡 Note: For integration tests with real API calls,")
    print("   run: python tests/integration/test_brand_context_service.py")
