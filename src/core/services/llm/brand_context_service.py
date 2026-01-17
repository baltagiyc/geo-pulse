"""
Brand Context Service.

Generates a factual summary of a brand using web search and LLM.
Helps prevent hallucinations when generating questions for unknown brands.
"""

import logging

from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.graph.state import SearchResult
from src.core.services.llm.llm_factory import create_llm
from src.core.services.search.tavily_service import search_with_tavily

logger = logging.getLogger(__name__)


def _format_search_results_for_context(search_results: list[SearchResult]) -> str:
    """
    Format search results for the context prompt.

    Simple format: title, URL, and snippet for each result.
    """
    if not search_results:
        return "No search results available."

    formatted = []
    for result in search_results:
        formatted.append(f"Title: {result.title}\nURL: {result.url}\nSnippet: {result.snippet}")

    return "\n\n".join(formatted)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_brand_context(brand: str, context_llm: str = "openai:gpt-4o-mini") -> str:
    """
    Generate a factual summary of a brand using web search and LLM.

    Args:
        brand: Name of the brand to summarize
        context_llm: LLM specification in format "provider:model" (default: "openai:gpt-4o-mini")

    Returns:
        Factual summary string (2-3 sentences)

    Raises:
        ValueError: If provider is not supported or API key is missing
        Exception: If LLM call fails after retries
    """
    try:
        search_results = search_with_tavily(f"{brand} company products services", max_results=5)
        if not search_results:
            logger.warning(f"No search results found for brand context: {brand}")
            return ""

        formatted_results = _format_search_results_for_context(search_results)

        llm = create_llm(context_llm, temperature=0.3)

        prompt = f"""You are a fact-checker. Your goal is to provide a factual, neutral summary of what this brand/company does.

Brand name: {brand}

I will provide you with web search results about this brand. Your task is to extract:
1. What industry/sector this brand operates in
2. What products or services they offer
3. A brief factual description (2-3 sentences max)

IMPORTANT:
- Focus ONLY on factual information (what they do, not opinions or reviews)
- Ignore recent news, buzz, or controversies
- If the brand is well-known, provide a concise summary
- If the brand is a startup, extract what you can from the search results
- Keep it neutral and factual

Web search results:
{formatted_results}

Provide a concise, factual summary of what {brand} does."""

        response = llm.invoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)
        context = content.strip()

        logger.info(f"Generated brand context for: {brand}")
        return context

    except Exception as e:
        logger.error(f"Failed to generate brand context for brand '{brand}': {str(e)}")
        raise
