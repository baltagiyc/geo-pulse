"""
Unit tests for LLM simulator service.

Tests the LLM simulation logic in isolation using mocks.
These tests are FAST, FREE, and run in CI/CD pipelines.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.services.llm.llm_simulator import simulate_llm_response, _format_search_results
from src.core.graph.state import LLMResponse, SearchResult


def test_format_search_results():
    """Test formatting of search results for prompt."""
    search_results = [
        SearchResult(
            title="Nike Official Site",
            url="https://www.nike.com",
            snippet="Best running shoes for athletes",
            domain="nike.com"
        ),
        SearchResult(
            title="Nike Reviews",
            url="https://reviews.nike.com",
            snippet="Customer reviews and ratings",
            domain="reviews.nike.com"
        )
    ]
    
    formatted = _format_search_results(search_results)
    
    assert "Nike Official Site" in formatted
    assert "https://www.nike.com" in formatted
    assert "Best running shoes" in formatted
    assert "Nike Reviews" in formatted
    assert "https://reviews.nike.com" in formatted


def test_format_search_results_empty():
    """Test formatting with empty search results."""
    formatted = _format_search_results([])
    assert formatted == "No search results available."


@patch('src.core.services.llm.llm_simulator.ChatOpenAI')
def test_simulate_llm_response_with_mock(mock_chat_openai):
    """
    Test LLM simulation with mocked LLM (for CI/CD).
    
    This test doesn't call the real API, so it's free and fast.
    """
    # Mock the LLM response
    mock_llm_instance = MagicMock()
    mock_structured_llm = MagicMock()
    
    # Mock the structured output response
    mock_response = LLMResponse(
        llm_name="gpt-4",
        response="Nike is a leading brand in athletic footwear with excellent quality and innovation.",
        sources=["https://www.nike.com", "https://reviews.nike.com"]
    )
    mock_structured_llm.invoke.return_value = mock_response
    
    # Mock the chain: ChatOpenAI() -> with_structured_output() -> invoke()
    mock_llm_instance.with_structured_output.return_value = mock_structured_llm
    mock_chat_openai.return_value = mock_llm_instance
    
    # Prepare test data
    search_results = [
        SearchResult(
            title="Nike Official Site",
            url="https://www.nike.com",
            snippet="Best running shoes",
            domain="nike.com"
        )
    ]
    
    # Mock API key
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        result = simulate_llm_response(
            question="What are the best Nike products?",
            search_results=search_results,
            llm_provider="gpt-4",
            brand="Nike"
        )
    
    # Verify results
    assert isinstance(result, LLMResponse)
    assert result.llm_name == "gpt-4"
    assert len(result.response) > 0
    assert len(result.sources) > 0
    assert "https://www.nike.com" in result.sources
    
    # Verify LLM was called correctly
    mock_chat_openai.assert_called_once()
    mock_structured_llm.invoke.assert_called_once()
    
    # Verify temperature is set to 0.7
    call_args = mock_chat_openai.call_args
    assert call_args.kwargs['temperature'] == 0.7


@patch('src.core.services.llm.llm_simulator.ChatOpenAI')
def test_simulate_llm_response_empty_results(mock_chat_openai):
    """Test that empty search results are handled correctly."""
    mock_llm_instance = MagicMock()
    mock_structured_llm = MagicMock()
    
    mock_response = LLMResponse(
        llm_name="gpt-4",
        response="I don't have enough information to answer this question.",
        sources=[]
    )
    mock_structured_llm.invoke.return_value = mock_response
    mock_llm_instance.with_structured_output.return_value = mock_structured_llm
    mock_chat_openai.return_value = mock_llm_instance
    
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        result = simulate_llm_response(
            question="What are the best Nike products?",
            search_results=[],
            llm_provider="gpt-4"
        )
    
    assert isinstance(result, LLMResponse)
    assert len(result.sources) == 0


if __name__ == "__main__":
    print("🧪 Unit Tests: LLM Simulator Service (with mocks)")
    print("-" * 50)
    
    test_format_search_results()
    print("✅ Format search results test passed")
    
    test_format_search_results_empty()
    print("✅ Empty search results formatting test passed")
    
    test_simulate_llm_response_with_mock()
    print("✅ Mock LLM simulation test passed (no API call, free)")
    
    test_simulate_llm_response_empty_results()
    print("✅ Empty results handling test passed")
    
    print("\n" + "-" * 50)
    print("✅ All unit tests passed!")
    print("\n💡 Note: For integration tests with real API calls,")
    print("   run: python tests/integration/test_llm_simulator.py")

