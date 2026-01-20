"""
Shared utility functions for core services.

Currently contains helpers for formatting search results for LLM prompts.
"""

from collections.abc import Iterable

from src.core.graph.state import SearchResult


def format_search_results_for_prompt(search_results: Iterable[SearchResult]) -> str:
    """
    Format search results for inclusion in an LLM prompt.

    Simple, readable format:
    - Title
    - URL
    - Snippet
    """
    results_list = list(search_results)
    if not results_list:
        return "No search results available."

    formatted: list[str] = []
    for result in results_list:
        formatted.append(f"Title: {result.title}\nURL: {result.url}\nSnippet: {result.snippet}")

    return "\n\n".join(formatted)
