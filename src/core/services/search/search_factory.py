"""
Search Factory.

Generic factory pattern for creating search tool instances from different providers.
This factory can be used for any search operation in the GEO audit workflow.

Supports Tavily, Bing, Google Custom Search, and other providers.
Format: "provider" or "provider:tool" (e.g., "tavily", "bing", "google")

This is a generic utility that can be reused across different services:
- search_executor_node: Search tool for web searches
- API endpoints: Allow users to choose their preferred search engine
"""

import logging
from collections.abc import Callable

from src.core.graph.state import SearchResult
from src.core.services.search.tavily_service import search_with_tavily

logger = logging.getLogger(__name__)

# Type alias for search functions
SearchFunction = Callable[[str, int], list[SearchResult]]

# Mapping of LLM providers to their default search tools
# This ensures we simulate the real behavior of each LLM:
# - ChatGPT uses Bing Search API
# - Gemini uses Google Search (via Google SGE)
# - Claude has no built-in web search
# - Perplexity has its own integrated search engine
LLM_TO_SEARCH_TOOL_MAPPING = {
    # OpenAI models
    "chatgpt": "bing",
    "gpt-4": "bing",
    "gpt-4o": "bing",
    "gpt-4o-mini": "bing",
    "gpt-3.5-turbo": "bing",
    # Google models
    "gemini": "google",
    "gemini-pro": "google",
    "gemini-ultra": "google",
    # Anthropic models
    "claude": None,  # Claude has no built-in web search
    "claude-3": None,
    "claude-3-opus": None,
    "claude-3-sonnet": None,
    # Perplexity (special case: combines search + LLM response)
    "perplexity": "perplexity",
    # Default fallback
    "default": "tavily",  # Use Tavily for unknown LLMs or testing
}


def get_search_tool_for_llm(llm_provider: str) -> str:
    """
    Get the appropriate search tool for a given LLM provider.

    This function maps each LLM to its real-world search tool:
    - ChatGPT/GPT-4 -> Bing Search API
    - Gemini -> Google Search API
    - Claude -> None (no built-in web search)
    - Perplexity -> Perplexity (special case: search + LLM combined)

    For now, returns "tavily" for all LLMs as a default.
    Future: will return the correct search tool based on the mapping above.

    Args:
        llm_provider: LLM provider name (e.g., "chatgpt", "gpt-4", "gemini", "perplexity")

    Returns:
        Search tool specification (e.g., "bing", "google", "tavily", "perplexity")
    """
    # Normalize the provider name
    provider_lower = llm_provider.lower().strip()

    # Check if we have a mapping for this provider
    search_tool = LLM_TO_SEARCH_TOOL_MAPPING.get(provider_lower)

    # If no mapping found or provider doesn't support web search, use default
    if search_tool is None:
        logger.info(
            f"No search tool mapping for '{llm_provider}' or provider doesn't support web search. "
            f"Using Tavily as default."
        )
        return LLM_TO_SEARCH_TOOL_MAPPING["default"]

    # TODO: Once Bing, Google, and Perplexity are implemented, return the mapped search tool
    # For now, always return Tavily as default
    logger.info(
        f"LLM '{llm_provider}' should use '{search_tool}' search tool, "
        f"but using Tavily as default (not yet implemented)"
    )
    return LLM_TO_SEARCH_TOOL_MAPPING["default"]


def create_search_tool(search_tool_spec: str = "tavily") -> SearchFunction:
    """
    Create a search function based on provider specification.

    Format: "provider" or "provider:tool"
    Examples:
        - "tavily" (default)
        - "bing" (to be implemented)
        - "google" (to be implemented)
        - "perplexity" (to be implemented - special case: search + LLM response)

    Args:
        search_tool_spec: Search tool specification (default: "tavily")

    Returns:
        SearchFunction: A function that takes (query: str, max_results: int) and returns list[SearchResult]

    Raises:
        ValueError: If provider is not supported or API key is missing
    """
    # Normalize: remove any ":" separator for now (future: "bing:v7", "google:custom", etc.)
    provider = search_tool_spec.split(":")[0].lower()

    if provider == "tavily":
        return _create_tavily_search()
    elif provider == "bing":
        # TODO: Implement Bing Search API support
        # Bing format: {webPages: {value: [{name, url, snippet, displayUrl}]}}
        # Need to transform: name -> title, snippet -> snippet, extract domain from url
        raise ValueError("Bing provider not yet implemented. Supported providers: tavily")
    elif provider == "google":
        # TODO: Implement Google Custom Search API support
        # Google format: {items: [{title, link, snippet}]}
        # Need to transform: title -> title, link -> url, snippet -> snippet, extract domain
        raise ValueError("Google provider not yet implemented. Supported providers: tavily")
    elif provider == "perplexity":
        # TODO: Implement Perplexity support
        # Perplexity is special: it combines search + LLM response in one call
        # This will require a different node in the graph (bypasses search + llm_simulator)
        # For now, we treat it as a search tool that returns enriched results
        raise ValueError(
            "Perplexity provider not yet implemented. Supported providers: tavily. "
            "Note: Perplexity requires special handling as it combines search + LLM response."
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}. Supported providers: tavily")


def _create_tavily_search() -> SearchFunction:
    """
    Create a Tavily search function.

    Returns:
        SearchFunction: Function that searches using Tavily API

    Raises:
        ValueError: If TAVILY_API_KEY is missing
    """
    logger.info("Creating Tavily search tool")
    return search_with_tavily


# TODO: Add functions for other providers
# def _create_bing_search() -> SearchFunction:
#     """
#     Create a Bing search function.
#
#     Bing Search API format:
#         {
#             "webPages": {
#                 "value": [
#                     {
#                         "name": "...",        # -> title
#                         "url": "https://...", # -> url
#                         "snippet": "...",     # -> snippet (already correct)
#                         "displayUrl": "..."
#                     }
#                 ]
#             }
#         }
#
#     Returns:
#         SearchFunction: Function that searches using Bing API
#     """
#     pass
#
#
# def _create_google_search() -> SearchFunction:
#     """
#     Create a Google Custom Search function.
#
#     Google Custom Search API format:
#         {
#             "items": [
#                 {
#                     "title": "...",
#                     "link": "https://...",  # -> url
#                     "snippet": "..."
#                 }
#             ]
#         }
#
#     Returns:
#         SearchFunction: Function that searches using Google Custom Search API
#     """
#     pass
#
#
# def _create_perplexity_search() -> SearchFunction:
#     """
#     Create a Perplexity search function.
#
#     NOTE: Perplexity is special - it combines search + LLM response.
#     This might require a different approach in the graph:
#     - Option 1: Return search results + LLM response in one call
#     - Option 2: Create a special node that bypasses search + llm_simulator
#
#     Returns:
#         SearchFunction: Function that searches using Perplexity API
#     """
#     pass
