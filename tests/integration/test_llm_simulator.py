"""
Integration tests for LLM simulator service.

Tests with REAL API calls to verify end-to-end functionality.
These tests are EXPENSIVE and SLOW - only run manually, NOT in CI/CD.

Usage:
    python tests/integration/test_llm_simulator.py
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
import os
from src.core.services.llm.llm_simulator import simulate_llm_response
from src.core.graph.state import SearchResult, LLMResponse

# Load .env for API keys
load_dotenv()


def test_simulate_llm_response_real_api():
    """
    Integration test with REAL OpenAI API call.
    
    This test:
    - Calls the real OpenAI API (costs money)
    - Shows the actual LLM response generated
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
    
    # Prepare test data
    question = "What are the best Nike running shoes?"
    search_results = [
        SearchResult(
            title="Nike Air Zoom Pegasus 40 Review",
            url="https://www.runnersworld.com/nike-pegasus-40",
            snippet="The Nike Air Zoom Pegasus 40 is one of the most popular running shoes for daily training.",
            domain="runnersworld.com"
        ),
        SearchResult(
            title="Best Nike Running Shoes 2024",
            url="https://www.nike.com/running-shoes",
            snippet="Discover our top-rated running shoes for every type of runner.",
            domain="nike.com"
        ),
        SearchResult(
            title="Nike vs Adidas Running Shoes",
            url="https://www.gearpatrol.com/nike-vs-adidas",
            snippet="Both brands offer excellent options, but Nike excels in cushioning technology.",
            domain="gearpatrol.com"
        )
    ]
    
    print(f"Question: {question}")
    print(f"Search results: {len(search_results)} results")
    print()
    
    try:
        result = simulate_llm_response(
            question=question,
            search_results=search_results,
            llm_provider="gpt-4",
            brand="Nike"
        )
        
        # Verify results
        assert isinstance(result, LLMResponse), f"Expected LLMResponse, got {type(result)}"
        assert result.llm_name == "gpt-4", f"Expected llm_name='gpt-4', got '{result.llm_name}'"
        assert len(result.response) > 0, "Response should not be empty"
        assert isinstance(result.sources, list), "Sources should be a list"
        
        # Show generated response (this is why we run integration tests!)
        print(f"\n======================================================================")
        print(f"✅ SUCCESS! Generated LLM response:")
        print(f"======================================================================")
        print(f"\nLLM Provider: {result.llm_name}")
        print(f"\nResponse ({len(result.response)} characters):")
        print(f"{result.response}")
        print(f"\nSources cited ({len(result.sources)}):")
        for i, source in enumerate(result.sources, 1):
            print(f"   {i}. {source}")
        print(f"\n======================================================================")
        print(f"✅ Integration test passed!")
        print(f"======================================================================")
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 Integration Tests: LLM Simulator Service")
    print("=" * 50)
    print("⚠️  WARNING: These tests call REAL APIs and cost money!")
    print("   Only run manually, NOT in CI/CD pipelines.")
    print("=" * 50)
    print()
    
    success = test_simulate_llm_response_real_api()
    
    if success:
        print("\n🎉 All integration tests passed!")
    else:
        print("\n❌ Integration tests failed")
        sys.exit(1)

