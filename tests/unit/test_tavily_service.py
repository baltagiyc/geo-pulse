"""
Unit tests for Tavily search service.

Tests the search logic in isolation using mocks.
These tests are FAST, FREE, and run in CI/CD pipelines.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.graph.state import SearchResult
from src.core.services.search.tavily_service import (
    _transform_tavily_result,
    search_with_tavily,
)


def test_transform_tavily_result():
    """Test transformation of Tavily result to SearchResult."""
    tavily_result = {
        "title": "Nike Official Site",
        "url": "https://www.nike.com/products",
        "content": "Best running shoes for athletes",
        "score": 0.95,
    }

    result = _transform_tavily_result(tavily_result)

    assert isinstance(result, SearchResult)
    assert result.title == "Nike Official Site"
    assert result.url == "https://www.nike.com/products"
    assert result.snippet == "Best running shoes for athletes"
    assert result.domain == "www.nike.com"


def test_transform_tavily_result_domain_extraction():
    """Test domain extraction from various URL formats."""
    test_cases = [
        ("https://www.nike.com/products", "www.nike.com"),
        ("https://nike.com", "nike.com"),
        ("http://blog.nike.com/article", "blog.nike.com"),
        ("https://example.com/path/to/page", "example.com"),
    ]

    for url, expected_domain in test_cases:
        tavily_result = {"title": "Test", "url": url, "content": "Test content"}
        result = _transform_tavily_result(tavily_result)
        assert result.domain == expected_domain, f"Failed for URL: {url}"


@patch("src.core.services.search.tavily_service.TavilySearch")
@patch.dict("os.environ", {"TAVILY_API_KEY": "test-key"})
def test_search_with_tavily_mock(mock_tavily_class):
    """
    Test search with mocked Tavily (for CI/CD).

    This test doesn't call the real API, so it's free and fast.
    """
    # Mock Tavily response (Tavily returns a dict with "results" key)
    mock_tavily_instance = MagicMock()
    mock_tavily_instance.invoke.return_value = {
        "results": [
            {
                "title": "Nike Official Site",
                "url": "https://www.nike.com",
                "content": "Best running shoes",
                "score": 0.95,
            },
            {
                "title": "Nike Reviews",
                "url": "https://reviews.nike.com",
                "content": "Customer reviews",
                "score": 0.90,
            },
        ]
    }

    mock_tavily_class.return_value = mock_tavily_instance

    # Execute search
    results = search_with_tavily("test query", max_results=5)

    # Verify results
    assert isinstance(results, list)
    assert len(results) == 2
    assert all(isinstance(r, SearchResult) for r in results)
    assert results[0].title == "Nike Official Site"
    assert results[0].domain == "www.nike.com"

    # Verify Tavily was called correctly
    mock_tavily_class.assert_called_once_with(tavily_api_key="test-key", max_results=5)
    mock_tavily_instance.invoke.assert_called_once_with("test query")


@patch("src.core.services.search.tavily_service.TavilySearch")
@patch.dict("os.environ", {"TAVILY_API_KEY": "test-key"})
def test_search_with_tavily_empty_results(mock_tavily_class):
    """Test that empty results are handled correctly."""
    mock_tavily_instance = MagicMock()
    mock_tavily_instance.invoke.return_value = {"results": []}  # Empty results

    mock_tavily_class.return_value = mock_tavily_instance

    results = search_with_tavily("test query")

    # Should return empty list
    assert isinstance(results, list)
    assert len(results) == 0


if __name__ == "__main__":
    print("🧪 Unit Tests: Tavily Search Service (with mocks)")
    print("-" * 50)

    test_transform_tavily_result()
    print("✅ Transform Tavily result test passed")

    test_transform_tavily_result_domain_extraction()
    print("✅ Domain extraction test passed")

    test_search_with_tavily_mock()
    print("✅ Mock search test passed (no API call, free)")

    test_search_with_tavily_empty_results()
    print("✅ Empty results handling test passed")

    print("\n" + "-" * 50)
    print("✅ All unit tests passed!")
    print("\n💡 Note: For integration tests with real API calls,")
    print("   run: python tests/integration/test_tavily_service.py")
