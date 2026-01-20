"""
Tavily Search Service.

Provides web search functionality using Tavily API.
Tavily is optimized for LLM use cases and returns structured JSON results.
"""

import logging
import os
from urllib.parse import urlparse

from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.config import DEFAULT_MAX_SEARCH_RESULTS
from src.core.graph.state import SearchResult

load_dotenv()
logger = logging.getLogger(__name__)


def _transform_tavily_result(tavily_result: dict) -> SearchResult:
    """
    Transform a Tavily result into a SearchResult Pydantic model.

    Why manual parsing instead of structured output?
    - Tavily already returns structured JSON (not free-form text)
    - Simple transformation: just map fields and extract domain
    - No LLM needed: we can parse JSON directly (faster, cheaper)
    - Shows versatility: we know when to use structured output (LLM text)
      vs manual parsing (structured JSON)

    Tavily format:
        {
            "title": "...",
            "url": "https://...",
            "content": "...",  # We map this to "snippet"
            "score": 0.95
        }

    SearchResult format:
        {
            "title": "...",
            "url": "https://...",
            "snippet": "...",  # From Tavily's "content"
            "domain": "example.com"  # Extracted from URL
        }
    """
    url = tavily_result.get("url", "")

    # Extract domain from URL using urlparse
    # Example: "https://www.nike.com/products" -> "www.nike.com"
    domain = urlparse(url).netloc if url else ""

    return SearchResult(
        title=tavily_result.get("title", ""),
        url=url,
        snippet=tavily_result.get("content", ""),  # Tavily uses "content", we use "snippet"
        domain=domain,
    )


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def search_with_tavily(query: str, max_results: int = DEFAULT_MAX_SEARCH_RESULTS) -> list[SearchResult]:
    """
    Search the web using Tavily API.

    Tavily is optimized for LLM use cases and returns structured JSON results.
    We parse these results manually (no structured output needed) because:
    1. Tavily already returns structured JSON
    2. Simple field mapping (content → snippet, extract domain from URL)
    3. No LLM call needed (faster, cheaper)
    4. Demonstrates versatility: manual parsing for structured data,
       structured output for LLM-generated text

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 5)

    Returns:
        List of SearchResult objects validated with Pydantic

    Raises:
        ValueError: If API key is missing
        Exception: If search fails after retries
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY not found in environment variables")

    try:
        search = TavilySearch(tavily_api_key=api_key, max_results=max_results)

        # Execute search
        # Tavily returns a dict with "results" key containing the list
        response = search.invoke(query)
        raw_results = response.get("results", []) if isinstance(response, dict) else response

        # Transform and validate results
        validated_results = []
        for result in raw_results:
            try:
                # Transform Tavily format to SearchResult
                search_result = _transform_tavily_result(result)
                validated_results.append(search_result)
            except Exception as e:
                logger.warning(f"Skipping invalid search result: {str(e)}")
                continue

        logger.info(f"Found {len(validated_results)} valid results for query: {query}")
        return validated_results

    except Exception as e:
        logger.error(f"Tavily search failed for query '{query}': {str(e)}")
        raise
