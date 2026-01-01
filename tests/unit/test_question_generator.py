"""
Unit tests for question generator service.

Tests the question generation logic in isolation.
Uses mocks to avoid real API calls (for CI/CD).

These tests are FAST, FREE, and run in CI/CD pipelines.
"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import os
from src.core.services.llm.question_generator import generate_questions, QuestionsResponse


def test_questions_response_model():
    """Test that QuestionsResponse validates correctly."""
    # Valid response
    response = QuestionsResponse(questions=[
        "What are the best Nike products?",
        "Where to buy Nike?",
        "Nike vs Adidas?"
    ])
    assert len(response.questions) == 3
    assert isinstance(response.questions, list)
    
    # Invalid response (too few questions)
    try:
        QuestionsResponse(questions=["Only one question"])
        assert False, "Should have raised ValidationError"
    except Exception:
        assert True


@patch('src.core.services.llm.question_generator.ChatOpenAI')
def test_generate_questions_with_mock(mock_chat_openai):
    """
    Test question generation with mocked LLM (for CI/CD).
    
    This test doesn't call the real API, so it's free and fast.
    Used in CI/CD pipelines.
    """
    # Mock the LLM response
    mock_llm_instance = MagicMock()
    mock_structured_llm = MagicMock()
    
    # Mock the structured output response
    mock_response = QuestionsResponse(questions=[
        "What are the best Nike products?",
        "Where to buy Nike shoes?",
        "How does Nike compare to Adidas?",
        "What are Nike's most popular items?",
        "Is Nike a good brand for running?"
    ])
    mock_structured_llm.invoke.return_value = mock_response
    
    # Mock the chain: ChatOpenAI() -> with_structured_output() -> invoke()
    mock_llm_instance.with_structured_output.return_value = mock_structured_llm
    mock_chat_openai.return_value = mock_llm_instance
    
    # Mock API key
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
        brand = "Nike"
        questions = generate_questions(brand, num_questions=5)
    
    # Verify results
    assert isinstance(questions, list)
    assert len(questions) == 5
    assert all(isinstance(q, str) for q in questions)
    assert "Nike" in questions[0]
    
    # Verify LLM was called correctly
    mock_chat_openai.assert_called_once()
    mock_structured_llm.invoke.assert_called_once()


if __name__ == "__main__":
    print("🧪 Unit Tests: Question Generator Service (with mocks)")
    print("-" * 50)
    
    test_questions_response_model()
    print("✅ QuestionsResponse model test passed")
    
    print("\n" + "-" * 50)
    test_generate_questions_with_mock()
    print("✅ Mock test passed (no API call, free)")
    
    print("\n" + "-" * 50)
    print("✅ All unit tests passed!")
    print("\n💡 Note: For integration tests with real API calls,")
    print("   run: python tests/integration/test_question_generator.py")

