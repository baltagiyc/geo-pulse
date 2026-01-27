"""Debug endpoints - test individual nodes."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.exceptions import format_error_message
from src.api.schemas.request import (
    AnalysisAnalyzeRequest,
    BrandContextRequest,
    LLMSimulateRequest,
    QuestionGenerateRequest,
    SearchExecuteRequest,
)
from src.api.schemas.response import (
    AnalysisAnalyzeResponse,
    BrandContextResponse,
    LLMSimulateResponse,
    QuestionGenerateResponse,
    SearchExecuteResponse,
    SearchResultResponse,
)
from src.core.config import is_hf_space
from src.core.graph.state import SearchResult
from src.core.services.analysis.analyst_service import analyze_brand_visibility
from src.core.services.llm.brand_context_service import generate_brand_context
from src.core.services.llm.llm_simulator import simulate_llm_response
from src.core.services.llm.question_generator import generate_questions
from src.core.services.search.search_factory import create_search_tool

logger = logging.getLogger(__name__)


def _block_debug_on_hf() -> None:
    if is_hf_space():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debug endpoints are disabled on Hugging Face Spaces, only available in local dev",
        )


router = APIRouter(dependencies=[Depends(_block_debug_on_hf)])


@router.post("/questions/generate", response_model=QuestionGenerateResponse, tags=["debug"])
async def generate_questions_endpoint(request: QuestionGenerateRequest) -> QuestionGenerateResponse:
    """
    Generate realistic questions about a brand (debug endpoint).

    This endpoint allows testing the question generation node in isolation.
    It uses the LLM factory to support multiple providers.

    **Note on `brand_context` parameter:**
    - This parameter is **optional** and especially useful for less-known brands or startups
      to prevent hallucinations when generating questions.
    - For well-known brands (e.g., Nike, Amazon, Google), you can **omit this parameter**
      as the LLM already has sufficient knowledge about these brands.
    - If you want to provide context, you can generate it using `/api/brand/context` endpoint
      and copy the `brand_context` field here.

    **Copy-paste workflow:**
    - For unknown brands: Generate brand context using `/api/brand/context`, then copy the
      `brand_context` field to use it here for more accurate questions.
    - For well-known brands: Simply provide `brand`, `num_questions`, and `question_llm` (no need for `brand_context`).

    Args:
        request: Question generation request with brand, num_questions, question_llm, and optional brand_context

    Returns:
        QuestionGenerateResponse: Generated questions with metadata

    Raises:
        HTTPException: 400 if request is invalid, 500 if generation fails
    """
    try:
        logger.info(
            f"Generating {request.num_questions} questions for brand: {request.brand} using {request.question_llm}"
        )

        questions = generate_questions(
            brand=request.brand,
            num_questions=request.num_questions,
            question_llm=request.question_llm,
            brand_context=request.brand_context,
        )

        return QuestionGenerateResponse(
            questions=questions,
            brand=request.brand,
            num_questions_generated=len(questions),
        )

    except ValueError as e:
        error_msg = format_error_message(e, "question generation")
        logger.error(f"Invalid request for question generation: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        ) from e
    except Exception as e:
        error_msg = format_error_message(e, "question generation")
        logger.error(f"Failed to generate questions for brand '{request.brand}': {error_msg}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg,
        ) from e


@router.post("/brand/context", response_model=BrandContextResponse, tags=["debug"])
async def generate_brand_context_endpoint(request: BrandContextRequest) -> BrandContextResponse:
    """
    Generate factual brand context (debug endpoint).

    This endpoint allows testing the brand context node in isolation.
    It uses Tavily search + LLM to build a factual summary of what the brand does.

    Args:
        request: Brand context request with brand name

    Returns:
        BrandContextResponse: Factual brand summary

    Raises:
        HTTPException: 400 if request is invalid, 500 if generation fails
    """
    try:
        logger.info(f"Generating brand context for: {request.brand}")

        brand_context = generate_brand_context(request.brand)

        return BrandContextResponse(
            brand=request.brand,
            brand_context=brand_context,
        )

    except ValueError as e:
        error_msg = format_error_message(e, "brand context generation")
        logger.error(f"Invalid request for brand context generation: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        ) from e
    except Exception as e:
        error_msg = format_error_message(e, "brand context generation")
        logger.error(f"Failed to generate brand context for '{request.brand}': {error_msg}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg,
        ) from e


@router.post("/search/execute", response_model=SearchExecuteResponse, tags=["debug"])
async def execute_search_endpoint(request: SearchExecuteRequest) -> SearchExecuteResponse:
    """
    Execute a web search (debug endpoint).

    This endpoint allows testing the search executor node in isolation.
    It uses the search factory to support multiple search tools (Tavily, Bing, Google, etc.).

    **Copy-paste workflow:**
    - You can copy a question from `/api/questions/generate` response and use it as the `query` parameter.
    - The `search_results` field in the response can be copied directly to `/api/llm/simulate` endpoint.

    Args:
        request: Search request with query, max_results, and search_tool.

    Returns:
        SearchExecuteResponse: Search results with metadata.

    Raises:
        HTTPException: 400 if request is invalid, 500 if search fails
    """
    try:
        logger.info(f"Executing search for query: '{request.query}' using {request.search_tool}")

        search_function = create_search_tool(request.search_tool)

        results = search_function(request.query, max_results=request.max_results)

        result_responses = [
            SearchResultResponse(
                title=result.title,
                url=result.url,
                snippet=result.snippet,
                domain=result.domain,
            )
            for result in results
        ]

        return SearchExecuteResponse(
            search_results=result_responses,
            query=request.query,
            search_tool=request.search_tool,
            num_results=len(result_responses),
        )

    except ValueError as e:
        error_msg = format_error_message(e, "search execution")
        logger.error(f"Invalid request for search execution: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        ) from e
    except Exception as e:
        error_msg = format_error_message(e, "search execution")
        logger.error(f"Failed to execute search for query '{request.query}': {error_msg}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg,
        ) from e


@router.post("/llm/simulate", response_model=LLMSimulateResponse, tags=["debug"])
async def simulate_llm_endpoint(request: LLMSimulateRequest) -> LLMSimulateResponse:
    """
    Simulate an LLM response based on search results (debug endpoint).

    This endpoint allows testing the LLM simulator node in isolation.
    It uses the LLM factory to support multiple providers.

    **Copy-paste workflow:**
    - You can copy a question from `/api/questions/generate` response and use it as the `question` parameter.
    - You can copy the `search_results` field from `/api/search/execute` response and use it directly as the `search_results` parameter.
    - The `llm_response` field in the response can be copied to `/api/analysis/analyze` endpoint.

    Args:
        request: LLM simulation request with question, search_results, llm_spec, and brand.


    Returns:
        LLMSimulateResponse: Simulated LLM response with metadata.

    Raises:
        HTTPException: 400 if request is invalid, 500 if simulation fails
    """
    try:
        logger.info(f"Simulating LLM response for question: '{request.question[:50]}...' using {request.llm_spec}")

        # This allows users to copy-paste results directly from /api/search/execute
        search_results_pydantic = [
            SearchResult(
                title=result.title,
                url=result.url,
                snippet=result.snippet,
                domain=result.domain,
            )
            for result in request.search_results
        ]

        llm_response = simulate_llm_response(
            question=request.question,
            search_results=search_results_pydantic,
            llm_spec=request.llm_spec,
            brand=request.brand,
        )

        return LLMSimulateResponse(
            llm_response=llm_response,
            question=request.question,
            llm_spec=request.llm_spec,
            brand=request.brand,
        )

    except ValueError as e:
        error_msg = format_error_message(e, "LLM simulation")
        logger.error(f"Invalid request for LLM simulation: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        ) from e
    except Exception as e:
        error_msg = format_error_message(e, "LLM simulation")
        logger.error(
            f"Failed to simulate LLM response for question '{request.question[:50]}...': {error_msg}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg,
        ) from e


@router.post("/analysis/analyze", response_model=AnalysisAnalyzeResponse, tags=["debug"])
async def analyze_endpoint(request: AnalysisAnalyzeRequest) -> AnalysisAnalyzeResponse:
    """
    Analyze brand visibility based on LLM responses (debug endpoint).

    This endpoint allows testing the analysis node (node 4) in isolation.
    It uses the same service as the graph (`analyze_brand_visibility`).

    **Important:** This endpoint processes ONE question at a time (consistent with other debug endpoints).
    For analyzing multiple questions, use the full `/api/audit` endpoint.

    **Copy-paste workflow:**
    - `question`: Copy from `question` field of `/api/llm/simulate` response, or from `query` field of `/api/search/execute` response.
    - `llm_response`: Copy the `llm_response` field directly from `/api/llm/simulate` response.
    - `search_results`: Copy the `search_results` field directly from `/api/search/execute` response.

    Args:
        request: Analysis request with brand, question (single), llm_response, and search_results.
                 All fields can be copied directly from previous endpoints.

    Returns:
        AnalysisAnalyzeResponse: Reputation score and GEO-focused recommendations.

    Raises:
        HTTPException: 400 if request is invalid, 500 if analysis fails.
    """
    try:
        logger.info(f"Analyzing brand visibility for: {request.brand}")

        questions = [request.question]
        llm_responses_dict = {request.question: request.llm_response.model_dump()}
        search_results_dict = {request.question: [result.model_dump() for result in request.search_results]}

        reputation_score, recommendations = analyze_brand_visibility(
            brand=request.brand,
            questions=questions,
            llm_responses=llm_responses_dict,
            search_results=search_results_dict,
        )

        return AnalysisAnalyzeResponse(
            reputation_score=reputation_score,
            recommendations=recommendations,
            brand=request.brand,
            num_questions_analyzed=1,
        )

    except ValueError as e:
        error_msg = format_error_message(e, "analysis")
        logger.error(f"Invalid request for analysis: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        ) from e
    except Exception as e:
        error_msg = format_error_message(e, "analysis")
        logger.error(f"Failed to analyze brand visibility for '{request.brand}': {error_msg}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg,
        ) from e
