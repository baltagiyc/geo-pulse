import logging

from src.core.config import DEFAULT_MAX_SEARCH_RESULTS, DEFAULT_NUM_QUESTIONS
from src.core.graph.state import GEOState
from src.core.graph.utils import (
    llm_response_model_to_dict,
    recommendations_models_to_dicts,
    search_results_dicts_to_models,
    search_results_models_to_dicts,
)
from src.core.services.analysis.analyst_service import analyze_brand_visibility
from src.core.services.llm.brand_context_service import generate_brand_context
from src.core.services.llm.llm_factory import get_simulation_llm_for_provider
from src.core.services.llm.llm_simulator import simulate_llm_response
from src.core.services.llm.question_generator import generate_questions
from src.core.services.search.search_factory import create_search_tool, get_search_tool_for_llm

logger = logging.getLogger(__name__)


def brand_context_generator_node(state: GEOState) -> dict:
    """
    Node 0: Generate factual context about the brand.

    This node searches the web and uses an LLM to create a factual summary
    of what the brand does. This helps prevent hallucinations when generating
    questions for unknown brands.
    """
    try:
        brand = state["brand"]
        logger.info(f"Generating brand context for: {brand}")

        context = generate_brand_context(brand)
        state["brand_context"] = context or None

        if state["brand_context"]:
            logger.info(f"Generated brand context: {state['brand_context'][:100]}...")
        else:
            logger.info("No brand context generated (empty result)")

    except Exception as e:
        error_msg = f"Failed to generate brand context: {str(e)}"
        logger.error(error_msg)
        state["errors"].append(error_msg)
        state["llm_errors"].append(error_msg)
        state["brand_context"] = None

    return state


def question_generator_node(state: GEOState) -> dict:
    """
    Node 1: Generate relevant questions to audit the brand.

    This node generates questions that typical users would ask about the brand,
    which will be used to search and analyze brand visibility.

    Uses the question_generator service to generate realistic questions via LLM.
    """
    try:
        brand = state["brand"]
        logger.info(f"Generating questions for brand: {brand}")

        brand_context = state.get("brand_context")
        questions = generate_questions(brand, num_questions=DEFAULT_NUM_QUESTIONS, brand_context=brand_context)

        state["questions"] = questions
        logger.info(f"Generated {len(questions)} questions")

    except Exception as e:
        error_msg = f"Failed to generate questions: {str(e)}"
        logger.error(error_msg)
        state["errors"].append(error_msg)
        state["llm_errors"].append(error_msg)
        state["questions"] = []

    return state


def search_executor_node(state: GEOState) -> dict:
    """
    Node 2: Execute web searches for each question.

    This node uses the search factory to execute searches.
    Currently uses Tavily as default for all LLMs.
    Future: will automatically select the correct search tool based on llm_provider
    (e.g., chatgpt -> bing, gemini -> google, perplexity -> perplexity).

    Structures the results with SearchResult Pydantic model,
    and handles errors with retry logic.
    """
    if "search_results" not in state:
        state["search_results"] = {}

    if "search_errors" not in state:
        state["search_errors"] = []

    llm_provider = state.get("llm_provider", "gpt-4")
    search_tool_spec = get_search_tool_for_llm(llm_provider)
    search_function = create_search_tool(search_tool_spec)

    for question in state.get("questions", []):
        try:
            logger.info(f"Searching for question: {question} using {search_tool_spec}")

            results = search_function(question, max_results=DEFAULT_MAX_SEARCH_RESULTS)

            state["search_results"][question] = search_results_models_to_dicts(results)

            logger.info(f"Found {len(results)} results for question: {question}")

        except Exception as e:
            error_msg = f"Failed to search '{question}': {str(e)}"
            logger.error(error_msg)
            state["search_errors"].append(error_msg)
            state["search_results"][question] = []

    return state


def llm_simulator_node(state: GEOState) -> dict:
    """
    Node 3: Simulate LLM responses based on search results.

    This node simulates the chosen LLM (ChatGPT, Gemini, etc.) by generating
    responses based on the search results, using with_structured_output for LLMResponse.

    For each question:
    1. Retrieves search_results from state (as dicts)
    2. Converts dicts to SearchResult objects
    3. Calls simulate_llm_response() to generate LLM response
    4. Stores LLMResponse as dict in state
    """
    if "llm_responses" not in state:
        state["llm_responses"] = {}

    if "llm_errors" not in state:
        state["llm_errors"] = []

    llm_provider = state.get("llm_provider", "gpt-4")
    brand = state.get("brand", "")

    for question in state.get("questions", []):
        try:
            logger.info(f"Simulating LLM response for question: {question}")

            search_results_dicts = state.get("search_results", {}).get(question, [])

            if not search_results_dicts:
                logger.warning(f"No search results for question: {question}")
                state["llm_responses"][question] = {}
                continue

            search_results = search_results_dicts_to_models(search_results_dicts)

            llm_spec = get_simulation_llm_for_provider(llm_provider)
            llm_response = simulate_llm_response(
                question=question,
                search_results=search_results,
                llm_spec=llm_spec,
                brand=brand,
            )

            state["llm_responses"][question] = llm_response_model_to_dict(llm_response)

            logger.info(f"Generated LLM response for question: {question[:50]}...")
            logger.info(f"Response cites {len(llm_response.sources)} sources")

        except Exception as e:
            error_msg = f"Failed to simulate LLM response for '{question}': {str(e)}"
            logger.error(error_msg)
            state["llm_errors"].append(error_msg)
            state["llm_responses"][question] = {}

    return state


def response_analyst_node(state: GEOState) -> dict:
    """
    Node 4: Analyze LLM responses and generate score + recommendations.

    This node analyzes the LLM responses to calculate the reputation score
    and generate recommendations to improve brand visibility.

    Uses the analyst_service to:
    1. Analyze negative responses (weaknesses, criticisms)
    2. Identify preferred competitors and reasons
    3. Analyze sources/domains most cited (SEO/GEO opportunities)
    4. Calculate overall reputation score (0.0 to 1.0)
    5. Generate actionable recommendations
    """
    try:
        brand = state.get("brand", "")
        questions = state.get("questions", [])
        llm_responses = state.get("llm_responses", {})
        search_results = state.get("search_results", {})

        logger.info(f"Analyzing brand visibility for: {brand}")

        if not questions or not llm_responses:
            logger.warning("Insufficient data for analysis. Using default values.")
            state["reputation_score"] = 0.0
            state["recommendations"] = []
            return state

        reputation_score, recommendations = analyze_brand_visibility(
            brand=brand,
            questions=questions,
            llm_responses=llm_responses,
            search_results=search_results,
        )

        state["reputation_score"] = reputation_score
        state["recommendations"] = recommendations_models_to_dicts(recommendations)

        logger.info(f"Analysis complete. Score: {reputation_score}, Recommendations: {len(recommendations)}")

    except Exception as e:
        error_msg = f"Failed to analyze brand visibility: {str(e)}"
        logger.error(error_msg)
        state["errors"].append(error_msg)
        # Set default values on error
        state["reputation_score"] = 0.0
        state["recommendations"] = []

    return state
