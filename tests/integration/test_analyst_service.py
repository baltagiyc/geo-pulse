"""
Integration tests for brand visibility analyst service.

Tests with REAL API calls to verify end-to-end functionality.
These tests are EXPENSIVE and SLOW - only run manually, NOT in CI/CD.

Usage:
    python tests/integration/test_analyst_service.py
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import os

from dotenv import load_dotenv

from src.core.services.analysis.analyst_service import analyze_brand_visibility

# Load .env for API keys
load_dotenv()


def test_analyze_brand_visibility_real_api():
    """
    Integration test with REAL OpenAI API call.

    This test:
    - Calls the real OpenAI API (costs money)
    - Shows the actual analysis results (score + recommendations)
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

    # Prepare test data (simulating real graph output)
    brand = "Nike"
    questions = [
        "What are the best Nike running shoes compared to Adidas?",
        "What are the main complaints and weaknesses about Nike products?",
    ]
    llm_responses = {
        "What are the best Nike running shoes compared to Adidas?": {
            "llm_name": "gpt-4",
            "response": "Nike and Adidas both offer excellent running shoes. Nike's Air Zoom Pegasus is popular for daily training, while Adidas offers the Adizero series for competitive running. Both brands excel in different aspects.",
            "sources": [
                "https://www.runnersworld.com/nike-vs-adidas",
                "https://www.nike.com/running-shoes",
            ],
        },
        "What are the main complaints and weaknesses about Nike products?": {
            "llm_name": "gpt-4",
            "response": "Common complaints about Nike include: high pricing compared to competitors, some durability issues with certain models, and concerns about sustainability practices. Customers also mention that sizing can be inconsistent.",
            "sources": [
                "https://www.reddit.com/r/running/nike-complaints",
                "https://www.consumerreports.org/nike-review",
            ],
        },
    }
    search_results = {
        "What are the best Nike running shoes compared to Adidas?": [
            {
                "title": "Nike vs Adidas",
                "url": "https://www.runnersworld.com/nike-vs-adidas",
                "snippet": "Comparison...",
                "domain": "runnersworld.com",
            },
            {
                "title": "Nike Running",
                "url": "https://www.nike.com/running-shoes",
                "snippet": "Official site...",
                "domain": "nike.com",
            },
            {
                "title": "Amazon Reviews",
                "url": "https://www.amazon.com/nike-shoes",
                "snippet": "Customer reviews...",
                "domain": "amazon.com",
            },
        ],
        "What are the main complaints and weaknesses about Nike products?": [
            {
                "title": "Reddit Discussion",
                "url": "https://www.reddit.com/r/running/nike-complaints",
                "snippet": "User complaints...",
                "domain": "reddit.com",
            },
            {
                "title": "Consumer Reports",
                "url": "https://www.consumerreports.org/nike-review",
                "snippet": "Review...",
                "domain": "consumerreports.org",
            },
            {
                "title": "Trustpilot",
                "url": "https://www.trustpilot.com/nike",
                "snippet": "Reviews...",
                "domain": "trustpilot.com",
            },
        ],
    }

    print(f"Brand: {brand}")
    print(f"Questions: {len(questions)}")
    print(f"LLM Responses: {len(llm_responses)}")
    print(f"Search Results: {len(search_results)} questions")
    print()

    try:
        score, recommendations = analyze_brand_visibility(
            brand=brand,
            questions=questions,
            llm_responses=llm_responses,
            search_results=search_results,
        )

        # Verify results
        assert isinstance(score, float), f"Expected float, got {type(score)}"
        assert 0.0 <= score <= 1.0, f"Score should be between 0.0 and 1.0, got {score}"
        assert isinstance(recommendations, list), "Recommendations should be a list"

        # Show analysis results (this is why we run integration tests!)
        print("\n======================================================================")
        print(f"✅ SUCCESS! Analysis completed for '{brand}':")
        print("======================================================================")
        print(f"\n📊 Reputation Score: {score:.2f}/1.0")
        print(f"\n💡 Recommendations ({len(recommendations)}):")
        print(f"   {'='*70}")
        for i, rec in enumerate(recommendations, 1):
            print(f"\n   {i}. {rec.title} [{rec.priority.upper()} priority]")
            print(f"      {rec.description}")
        print(f"\n   {'='*70}")
        print("\n======================================================================")
        print("✅ Integration test passed!")
        print("======================================================================")
        return True

    except Exception as e:
        print(f"\n❌ Integration test failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 Integration Tests: Brand Visibility Analyst Service")
    print("=" * 50)
    print("⚠️  WARNING: These tests call REAL APIs and cost money!")
    print("   Only run manually, NOT in CI/CD pipelines.")
    print("=" * 50)
    print()

    success = test_analyze_brand_visibility_real_api()

    if success:
        print("\n🎉 All integration tests passed!")
    else:
        print("\n❌ Integration tests failed")
        sys.exit(1)
