"""Debug endpoints - test individual nodes."""

import logging

from fastapi import APIRouter, HTTPException, status

from src.api.schemas.request import QuestionGenerateRequest, SearchExecuteRequest
from src.api.schemas.response import QuestionGenerateResponse, SearchExecuteResponse, SearchResultResponse
from src.core.services.llm.question_generator import generate_questions
from src.core.services.search.search_factory import create_search_tool

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/questions/generate", response_model=QuestionGenerateResponse, tags=["debug"])
async def generate_questions_endpoint(request: QuestionGenerateRequest) -> QuestionGenerateResponse:
    """
    Generate realistic questions about a brand (debug endpoint).

    This endpoint allows testing the question generation node in isolation.
    It uses the LLM factory to support multiple providers.

    Args:
        request: Question generation request with brand, num_questions, and question_llm

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
        )

        return QuestionGenerateResponse(
            questions=questions,
            brand=request.brand,
            num_questions_generated=len(questions),
        )

    except ValueError as e:
        logger.error(f"Invalid request for question generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}",
        ) from e
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to generate questions for brand '{request.brand}': {error_msg}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate questions: {error_msg}",
        ) from e


@router.post("/search/execute", response_model=SearchExecuteResponse, tags=["debug"])
async def execute_search_endpoint(request: SearchExecuteRequest) -> SearchExecuteResponse:
    """
    Execute a web search (debug endpoint).

    This endpoint allows testing the search executor node in isolation.
    It uses the search factory to support multiple search tools (Tavily, Bing, Google, etc.).

    Args:
        request: Search request with query, max_results, and search_tool

    Returns:
        SearchExecuteResponse: Search results with metadata

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
            results=result_responses,
            query=request.query,
            search_tool=request.search_tool,
            num_results=len(result_responses),
        )

    except ValueError as e:
        logger.error(f"Invalid request for search execution: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}",
        ) from e
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to execute search for query '{request.query}': {error_msg}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute search: {error_msg}",
        ) from e
