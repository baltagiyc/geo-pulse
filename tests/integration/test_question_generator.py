"""
Integration tests for question generator service.

Tests with REAL API calls to verify end-to-end functionality.
These tests are EXPENSIVE and SLOW - only run manually, NOT in CI/CD.

Usage:
    python tests/integration/test_question_generator.py
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
import os
from src.core.services.llm.question_generator import generate_questions

# Load .env for API keys
load_dotenv()


def test_generate_questions_real_api():
    """
    Integration test with REAL OpenAI API call.
    
    This test:
    - Calls the real OpenAI API (costs money)
    - Shows the actual questions generated
    - Verifies end-to-end functionality
    
    Only run this manually to verify everything works.
    DO NOT run in CI/CD (too expensive).
    """
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env")
        print("   Please add your OpenAI API key to .env file")
        return False
    
    print("🔗 Testing with REAL OpenAI API...")
    print("⚠️  This will make a real API call (costs money)")
    print("-" * 50)
    
    # Test with a simple brand
    brand = "Nike"
    print(f"Generating questions for brand: {brand}")
    
    try:
        questions = generate_questions(brand, num_questions=5)
        
        # Verify results
        assert isinstance(questions, list), f"Expected list, got {type(questions)}"
        assert len(questions) >= 3, f"Expected at least 3 questions, got {len(questions)}"
        assert len(questions) <= 10, f"Expected at most 10 questions, got {len(questions)}"
        
        # Verify all questions are strings
        for question in questions:
            assert isinstance(question, str), f"Expected string, got {type(question)}"
            assert len(question) > 0, "Question cannot be empty"
        
        # Show generated questions (this is why we run integration tests!)
        print("\n" + "=" * 70)
        print(f"✅ SUCCESS! Generated {len(questions)} questions for '{brand}':")
        print("=" * 70)
        print()
        for i, q in enumerate(questions, 1):
            print(f"   {i}. {q}")
            print()
        
        print("=" * 70)
        print("✅ Integration test passed!")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 Integration Tests: Question Generator Service")
    print("=" * 50)
    print("⚠️  WARNING: These tests call REAL APIs and cost money!")
    print("   Only run manually, NOT in CI/CD pipelines.")
    print("=" * 50)
    print()
    
    success = test_generate_questions_real_api()
    
    if success:
        print("\n🎉 All integration tests passed!")
    else:
        print("\n❌ Integration tests failed")
        sys.exit(1)

