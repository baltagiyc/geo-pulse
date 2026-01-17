"""
Integration tests for brand context service.

Tests with REAL API calls to verify end-to-end functionality.
These tests are EXPENSIVE and SLOW - only run manually, NOT in CI/CD.

Usage:
    python tests/integration/test_brand_context_service.py
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import os

from dotenv import load_dotenv

from src.core.services.llm.brand_context_service import generate_brand_context

# Load .env for API keys
load_dotenv()


def test_generate_brand_context_real_api():
    """
    Integration test with REAL API calls.

    This test:
    - Calls the real Tavily API (search)
    - Calls the real OpenAI API (LLM summary)
    - Shows the generated brand context
    - Verifies end-to-end functionality

    Only run this manually to verify everything works.
    DO NOT run in CI/CD (too expensive).
    """
    # Check if API keys are available
    openai_key = os.getenv("OPENAI_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    if not openai_key:
        print("❌ OPENAI_API_KEY not found in .env")
        print("   Please add your OpenAI API key to .env file")
        return False
    if not tavily_key:
        print("❌ TAVILY_API_KEY not found in .env")
        print("   Please add your Tavily API key to .env file")
        return False

    print("🔗 Testing with REAL Tavily + OpenAI APIs...")
    print("⚠️  This will make real API calls (costs money)")
    print("-" * 50)

    brand = "SeDomicilier"
    print(f"Generating brand context for: {brand}")

    try:
        context = generate_brand_context(brand)

        assert isinstance(context, str), f"Expected str, got {type(context)}"
        assert len(context) > 0, "Brand context cannot be empty"

        print("\n" + "=" * 70)
        print(f"✅ SUCCESS! Generated brand context for '{brand}':")
        print("=" * 70)
        print(context)
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
    print("🧪 Integration Tests: Brand Context Service")
    print("=" * 50)
    print("⚠️  WARNING: These tests call REAL APIs and cost money!")
    print("   Only run manually, NOT in CI/CD pipelines.")
    print("=" * 50)
    print()

    success = test_generate_brand_context_real_api()

    if success:
        print("\n🎉 All integration tests passed!")
    else:
        print("\n❌ Integration tests failed")
        sys.exit(1)
