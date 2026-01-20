"""
Brand Visibility Analyst Service.

Analyzes LLM responses to calculate reputation score and generate recommendations.
Uses LLM to analyze responses, identify weaknesses, competitors, and SEO opportunities.
"""

import logging

from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.config import ANALYSIS_LLM_TEMPERATURE, DEFAULT_ANALYSIS_LLM
from src.core.graph.state import Recommendation
from src.core.graph.utils import search_results_dicts_to_models
from src.core.services.llm.llm_factory import create_llm

logger = logging.getLogger(__name__)


class AnalysisResponse(BaseModel):
    """
    Response from the analysis LLM containing score and recommendations.
    """

    reputation_score: float = Field(description="Overall reputation score from 0.0 to 1.0", ge=0.0, le=1.0)
    recommendations: list[Recommendation] = Field(
        description="List of recommendations to improve brand visibility", default=[]
    )


def _format_llm_responses_for_analysis(
    questions: list[str], llm_responses: dict[str, dict], search_results: dict[str, list[dict]]
) -> str:
    """
    Format LLM responses for the analysis prompt.

    Converts the state's llm_responses dict into a readable format for the LLM.
    Includes all available search results and highlights which ones were cited.
    """
    formatted = []
    for i, question in enumerate(questions, 1):
        response_dict = llm_responses.get(question, {})
        search_results_list = search_results.get(question, [])

        # sources cited by LLM are different than sources founded by tavily
        # the sources not cited by the LLM have the potential to improve the visibility later (will see soon)
        sources_cited = response_dict.get("sources", [])

        # need to extract the pydantic model first
        available_domains = []
        for search_result in search_results_dicts_to_models(search_results_list):
            available_domains.append(
                {"domain": search_result.domain, "url": search_result.url, "title": search_result.title}
            )

        # Separate cited vs non-cited domains
        cited_domains = [d for d in available_domains if d["url"] in sources_cited]
        non_cited_domains = [d for d in available_domains if d["url"] not in sources_cited]

        section = f"Question {i}: {question}\n"

        if response_dict:
            section += f"LLM Response: {response_dict.get('response', 'N/A')}\n\n"

            # Sources cited by LLM (HIGH IMPACT - emphasized)
            if cited_domains:
                section += "✅ SOURCES CITED BY LLM (High Impact):\n"
                for domain_info in cited_domains:
                    section += f"   - {domain_info['domain']} ({domain_info['url']})\n"
                section += "\n"

            # Available sources NOT cited (SEO/GEO opportunities)
            if non_cited_domains:
                section += "📊 AVAILABLE SOURCES NOT CITED (SEO/GEO Opportunities):\n"
                for domain_info in non_cited_domains:
                    section += f"   - {domain_info['domain']} ({domain_info['url']})\n"
                section += "\n"
        else:
            section += "(No response available)\n"

        formatted.append(section)

    return "\n".join(formatted)


def _extract_domains_from_sources(search_results: dict[str, list[dict]]) -> dict[str, int]:
    """
    Extract and count domain occurrences from search results.

    Uses SearchResult Pydantic model to validate and extract domain.
    Returns a dict mapping domain to count of occurrences.
    """
    domain_counts = {}
    for question, results in search_results.items():
        for search_result in search_results_dicts_to_models(results):
            if search_result.domain:
                domain_counts[search_result.domain] = domain_counts.get(search_result.domain, 0) + 1

    return domain_counts


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def analyze_brand_visibility(
    brand: str, questions: list[str], llm_responses: dict[str, dict], search_results: dict[str, list[dict]]
) -> tuple[float, list[Recommendation]]:
    """
    Analyze brand visibility based on LLM responses.

    This function uses an LLM to:
    1. Analyze negative responses (weaknesses, criticisms)
    2. Identify preferred competitors and reasons
    3. Analyze sources/domains most cited (SEO/GEO opportunities)
    4. Calculate overall reputation score (0.0 to 1.0)
    5. Generate actionable recommendations

    Args:
        brand: Name of the brand being audited
        questions: List of questions asked
        llm_responses: Dict mapping question to LLMResponse dict
        search_results: Dict mapping question to list of SearchResult dicts

    Returns:
        Tuple of (reputation_score: float, recommendations: List[Recommendation])

    Raises:
        ValueError: If API key is missing
        Exception: If LLM call fails after retries
    """
    try:
        llm = create_llm(llm_spec=DEFAULT_ANALYSIS_LLM, temperature=ANALYSIS_LLM_TEMPERATURE)

        structured_llm = llm.with_structured_output(AnalysisResponse)

        formatted_responses = _format_llm_responses_for_analysis(questions, llm_responses, search_results)
        domain_counts = _extract_domains_from_sources(search_results)

        top_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        domains_text = "\n".join([f"- {domain}: {count} mentions" for domain, count in top_domains])

        prompt = f"""You are a GEO (Generative Engine Optimization) visibility analyst. Your goal is to help {brand} improve its VISIBILITY in AI/LLM responses (ChatGPT, Gemini, etc.), NOT to improve the product itself.

IMPORTANT CONTEXT:
- This is a VISIBILITY audit, not a product improvement audit
- We want to know: "How can {brand} be more visible/cited in LLM responses?"
- We do NOT want product recommendations like "improve pricing" or "add features"
- Instead, we want content/SEO/GEO strategies: "create content about X" or "improve visibility on domain Y"

BRAND: {brand}

QUESTIONS AND LLM RESPONSES:
{formatted_responses}

TOP DOMAINS/SOURCES CITED:
{domains_text if domains_text else "No domain data available"}

ANALYSIS REQUIREMENTS:

1. **Focus on Negative Responses (Transform to Content Opportunities)**:
   - Identify the question(s) about negative aspects, weaknesses, or criticisms
   - Extract all negative points mentioned
   - TRANSFORM these into CONTENT OPPORTUNITIES, not product fixes
   - Example: If "pricing is high" → Recommend "Create content explaining value proposition to be cited when users ask about pricing"
   - Example: If "limited integrations" → Recommend "Create blog posts about integrations to improve visibility on tech blogs"

2. **Competitor Analysis (Content Strategy)**:
   - If competitors are preferred over {brand}, identify which ones and why
   - Analyze the reasons (price, quality, innovation, etc.)
   - Recommend CONTENT STRATEGIES to compete, not product changes
   - Example: If competitor is preferred for "better features" → Recommend "Create comparison content highlighting {brand}'s unique features"

3. **Source/Domain Analysis (SEO/GEO Opportunities)**:
   - Identify which domains/sources are most frequently cited by the LLM
   - Identify which domains appear in search results but are NOT cited (opportunities)
   - Recommend improving visibility on these domains through content creation
   - Suggest specific types of content that would help (blog posts, reviews, guides, etc.)

4. **Reputation Score (0.0 to 1.0)**:
   - Calculate based on: visibility in LLM responses, number of sources cited, position in responses, competitor comparisons
   - 0.0 = Very poor visibility in LLM responses
   - 0.5 = Average/mixed visibility
   - 1.0 = Excellent visibility in LLM responses
   - NOTE: This is about VISIBILITY in AI responses, not product quality

5. **Recommendations (GEO/SEO Focus ONLY)**:
   - Generate 3-5 actionable recommendations to improve VISIBILITY in LLM responses
   - Focus ONLY on content, SEO, and GEO strategies - NOT product improvements
   - Each recommendation should have: title, description, priority (high/medium/low)
   - Examples of GOOD recommendations:
     * "Improve visibility on [domain] by creating blog content about [topic]" (if domain is frequently cited)
     * "Create content addressing [negative point] to be cited when users ask about [topic]" (transform negative into content opportunity)
     * "Optimize content on [domain] for LLM citations" (if domain appears but isn't cited)
     * "Create comparison content vs [competitor] to improve visibility" (if competitor is preferred)
   - Examples of BAD recommendations (DO NOT GENERATE):
     * "Improve product pricing" (product change, not visibility)
     * "Enhance product features" (product change, not visibility)
     * "Fix product issues" (product change, not visibility)
   - IMPORTANT: Transform negative points into CONTENT OPPORTUNITIES, not product fixes
     * Instead of "Fix pricing" → "Create content explaining pricing strategy to be cited in LLM responses"
     * Instead of "Improve integrations" → "Create blog posts about integrations to improve visibility on tech blogs"

Provide a comprehensive analysis with a justified score and actionable recommendations."""

        response = structured_llm.invoke(prompt)

        logger.info(f"Analysis completed for brand: {brand}")
        logger.info(f"Reputation score: {response.reputation_score}")
        logger.info(f"Generated {len(response.recommendations)} recommendations")

        return response.reputation_score, response.recommendations

    except Exception as e:
        logger.error(f"Failed to analyze brand visibility for '{brand}': {str(e)}")
        raise
