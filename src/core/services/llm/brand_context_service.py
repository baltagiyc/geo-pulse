"""
Brand Context Service.

Generates a factual summary of a brand using web search and LLM.
Helps prevent hallucinations when generating questions for unknown brands.
"""

import logging

from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.config import CONTEXT_LLM_TEMPERATURE, DEFAULT_CONTEXT_LLM, DEFAULT_MAX_SEARCH_RESULTS
from src.core.services.llm.llm_factory import create_llm
from src.core.services.search.search_factory import create_search_tool
from src.core.services.utils import format_search_results_for_prompt

logger = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_brand_context(
    brand: str, context_llm: str = DEFAULT_CONTEXT_LLM, openai_api_key: str | None = None
) -> str:
    """
    Generate a factual summary of a brand using web search and LLM.

    Args:
        brand: Name of the brand to summarize
        context_llm: LLM specification in format "provider:model" (default: "openai:gpt-4.1-mini")

    Returns:
        Factual summary string (2-3 sentences)

    Raises:
        ValueError: If provider is not supported or API key is missing
        Exception: If LLM call fails after retries
    """
    try:
        # use search factory so we can switch tools easily later (bing/google/perplexity)
        search_function = create_search_tool("tavily")
        search_results = search_function(
            f"{brand} company products services",
            max_results=DEFAULT_MAX_SEARCH_RESULTS,
        )
        if not search_results:
            logger.warning(f"No search results found for brand context: {brand}")
            return ""

        formatted_results = format_search_results_for_prompt(search_results)

        llm_kwargs = {"api_key": openai_api_key} if openai_api_key else {}
        llm = create_llm(context_llm, temperature=CONTEXT_LLM_TEMPERATURE, **llm_kwargs)

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
