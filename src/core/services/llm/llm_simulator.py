"""
LLM Simulator Service.

Simulates LLM responses (ChatGPT, Gemini, etc.) based on web search results.
Uses structured output to extract response and sources automatically.
"""

import logging

from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.graph.state import LLMResponse, SearchResult
from src.core.services.llm.llm_factory import create_llm, get_simulation_llm_for_provider
from src.core.services.utils import format_search_results_for_prompt

logger = logging.getLogger(__name__)


def _extract_llm_name_from_spec(llm_spec: str) -> str:
    """
    Extract LLM name from factory specification.

    Examples:
        "openai:gpt-4" -> "gpt-4"
        "openai:gpt-4o-mini" -> "gpt-4o-mini"
        "gpt-4" -> "gpt-4" (already simple format)
        "gemini" -> "gemini" (already simple format)

    Args:
        llm_spec: LLM specification (format "provider:model" or just "model")

    Returns:
        LLM name for metadata (e.g., "gpt-4", "gemini")
    """
    if ":" in llm_spec:
        # Factory format: "openai:gpt-4" -> extract "gpt-4"
        _, model = llm_spec.split(":", 1)
        return model
    else:
        # Simple format: "gpt-4" -> return as is
        return llm_spec


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def simulate_llm_response(
    question: str,
    search_results: list[SearchResult],
    llm_spec: str = "openai:gpt-4",
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
        llm_spec: LLM specification. Accepts two formats:
                  - Factory format: "openai:gpt-4", "openai:gpt-4o-mini" (recommended)
                  - Simple format: "gpt-4", "gemini" (will be converted via helper)
                  Default: "openai:gpt-4"
        brand: Optional brand name for context in the prompt

    Returns:
        LLMResponse object with response text and cited sources

    Raises:
        ValueError: If provider is not supported or API key is missing
        Exception: If LLM call fails after retries
    """
    try:
        # If llm_spec is in factory format (contains ":"), use it directly
        # Otherwise, convert using helper function
        if ":" in llm_spec:
            factory_llm_spec = llm_spec
        else:
            factory_llm_spec = get_simulation_llm_for_provider(llm_spec)

        llm = create_llm(llm_spec=factory_llm_spec, temperature=0.7)

        structured_llm = llm.with_structured_output(LLMResponse)

        formatted_results = format_search_results_for_prompt(search_results)

        brand_context = f" (about {brand})" if brand else ""

        prompt = f"""You are simulating how a real LLM (like ChatGPT) would respond to a user's question{brand_context}.

User's question: {question}

IMPORTANT: You have been provided with REAL, CURRENT web search results below. These results are up-to-date and contain the information needed to answer the question. You MUST use these search results to provide your answer. Do NOT say you don't have access to real-time data - you have it right here.

Web search results:
{formatted_results}

Instructions:
1. Use the search results above to answer the user's question comprehensively
2. You can also use your general knowledge to provide context, but prioritize the search results
3. Cite the specific URLs from the search results that you use in your answer
4. Provide a detailed, helpful answer as a real LLM assistant would
5. Do NOT mention that you don't have access to real-time data - you have been provided with current search results"""

        response = structured_llm.invoke(prompt)

        # Extract LLM name from spec for metadata (e.g., "openai:gpt-4" -> "gpt-4")
        response.llm_name = _extract_llm_name_from_spec(llm_spec)

        logger.info(f"Generated LLM response for question: {question[:50]}...")
        logger.info(f"Response cites {len(response.sources)} sources")

        return response

    except Exception as e:
        logger.error(f"Failed to simulate LLM response for question '{question}': {str(e)}")
        raise
