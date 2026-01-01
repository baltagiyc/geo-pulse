"""
Integration tests for Tavily search service.

Tests with REAL API calls to verify end-to-end functionality.
These tests are EXPENSIVE and SLOW - only run manually, NOT in CI/CD.

Usage:
    python tests/integration/test_tavily_service.py
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
import os
from src.core.services.search.tavily_service import search_with_tavily

# Load .env for API keys
load_dotenv()


def test_search_with_tavily_real_api():
    """
    Integration test with REAL Tavily API call.
    
    This test:
    - Calls the real Tavily API (costs money)
    - Shows the actual search results
    - Verifies end-to-end functionality
    
    Only run this manually to verify everything works.
    DO NOT run in CI/CD (too expensive).
    """
    # Check if API key is available
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        print("❌ TAVILY_API_KEY not found in .env")
        print("   Please add your Tavily API key to .env file")
        return False
    
    print("🔗 Testing with REAL Tavily API...")
    print("⚠️  This will make a real API call (costs money)")
    print("-" * 50)
    
    # Test with a simple query
    query = "What are the best Nike running shoes?"
    print(f"Searching for: {query}")
    
    try:
        results = search_with_tavily(query, max_results=5)
        
        # Verify results
        assert isinstance(results, list), f"Expected list, got {type(results)}"
        assert len(results) > 0, "Expected at least 1 result"
        assert len(results) <= 5, f"Expected at most 5 results, got {len(results)}"
        
        # Verify all results are SearchResult objects
        for result in results:
            assert hasattr(result, 'title'), "Result should have title"
            assert hasattr(result, 'url'), "Result should have url"
            assert hasattr(result, 'snippet'), "Result should have snippet"
            assert hasattr(result, 'domain'), "Result should have domain"
            assert len(result.title) > 0, "Title cannot be empty"
            assert len(result.url) > 0, "URL cannot be empty"
            assert len(result.domain) > 0, "Domain cannot be empty"
        
        # Show search results (this is why we run integration tests!)
        print("\n" + "=" * 70)
        print(f"✅ SUCCESS! Found {len(results)} results for '{query}':")
        print("=" * 70)
        print()
        for i, result in enumerate(results, 1):
            print(f"   {i}. {result.title}")
            print(f"      URL: {result.url}")
            print(f"      Domain: {result.domain}")
            print(f"      Snippet: {result.snippet[:100]}..." if len(result.snippet) > 100 else f"      Snippet: {result.snippet}")
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
    print("🧪 Integration Tests: Tavily Search Service")
    print("=" * 70)
    print("⚠️  WARNING: These tests call REAL APIs and cost money!")
    print("   Only run manually, NOT in CI/CD pipelines.")
    print("=" * 70)
    print()
    
    success = test_search_with_tavily_real_api()
    
    if success:
        print("\n🎉 All integration tests passed!")
    else:
        print("\n❌ Integration tests failed")
        sys.exit(1)

