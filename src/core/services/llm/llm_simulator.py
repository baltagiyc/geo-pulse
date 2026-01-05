"""
LLM Simulator Service.

Simulates LLM responses (ChatGPT, Gemini, etc.) based on web search results.
Uses structured output to extract response and sources automatically.
"""

import logging
import os

from langchain_openai import ChatOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.graph.state import LLMResponse, SearchResult

logger = logging.getLogger(__name__)


def _format_search_results(search_results: list[SearchResult]) -> str:
    """
    Format search results for the prompt. Because LLM cannot read Pydantic object.

    Simple format: title, URL, and snippet for each result.
    """
    if not search_results:
        return "No search results available."

    formatted = []
    for result in search_results:
        formatted.append(f"Title: {result.title}\n" f"URL: {result.url}\n" f"Snippet: {result.snippet}")

    return "\n\n".join(formatted)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def simulate_llm_response(
    question: str,
    search_results: list[SearchResult],
    llm_provider: str = "gpt-4",
    brand: str = "",
) -> LLMResponse:
    """
    Simulate an LLM response based on search results.

    This function simulates how ChatGPT (or other LLMs) would respond to a question
    using the provided web search results. The LLM can use both the search results
    and its own knowledge to provide a comprehensive, critical answer.

    Uses with_structured_output to automatically extract:
    - The response text
    - The sources (URLs) cited by the LLM

    Args:
        question: The user's question
        search_results: List of SearchResult objects from web search
        llm_provider: LLM provider name (e.g., "gpt-4", "gemini") - for now only "gpt-4" supported
        brand: Optional brand name for context in the prompt

    Returns:
        LLMResponse object with response text and cited sources

    Raises:
        ValueError: If API key is missing
        Exception: If LLM call fails after retries
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    try:
        # Initialize LLM with temperature 0.7 for realistic behavior
        llm = ChatOpenAI(model="gpt-4", temperature=0.7, api_key=api_key)

        # Use structured output to guarantee LLMResponse format
        structured_llm = llm.with_structured_output(LLMResponse)

        # Format search results for the prompt
        formatted_results = _format_search_results(search_results)

        # Build simple, natural prompt
        prompt = f"""{question}

Here are some web search results related to this question:

{formatted_results}

Based on these search results and your knowledge, provide a comprehensive answer.
Cite the sources you use by including their URLs."""

        # Call LLM with structured output
        response = structured_llm.invoke(prompt)

        # Set llm_name based on provider
        response.llm_name = llm_provider

        logger.info(f"Generated LLM response for question: {question[:50]}...")
        logger.info(f"Response cites {len(response.sources)} sources")

        return response

    except Exception as e:
        logger.error(f"Failed to simulate LLM response for question '{question}': {str(e)}")
        raise
