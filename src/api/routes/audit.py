"""Main audit endpoint for GEO Pulse API."""

import logging

from fastapi import APIRouter, HTTPException, status

from src.api.exceptions import format_error_message
from src.api.schemas.request import AuditRequest
from src.api.schemas.response import AuditResponse, SearchResultResponse
from src.api.services.access_code_quota import consume_access_code_quota
from src.core.config import get_access_code_max_audits, get_access_codes, is_hf_space
from src.core.graph.graph import create_audit_graph, create_initial_state
from src.core.graph.state import LLMResponse
from src.core.services.llm.request_context import reset_request_api_keys, set_request_api_keys

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/audit", response_model=AuditResponse, tags=["audit"])
async def audit_endpoint(request: AuditRequest) -> AuditResponse:
    """
    Main audit endpoint: Complete GEO audit workflow.

    This endpoint orchestrates the full LangGraph workflow:
    1. Generates realistic questions about the brand
    2. Executes web searches for each question
    3. Simulates LLM responses based on search results
    4. Analyzes responses to calculate reputation score and generate recommendations

    Args:
        request: Audit request with brand, llm_provider, and include_details flag.

    Returns:
        AuditResponse: Reputation score, recommendations, and optionally detailed results.

    Raises:
        HTTPException: 400 if request is invalid, 500 if audit fails.
    """
    try:
        logger.info(f"Starting GEO audit for brand: {request.brand} (LLM: {request.llm_provider})")

        graph = create_audit_graph()

        provider_lower = request.llm_provider.lower().strip()
        is_gemini = provider_lower.startswith("gemini")
        access_codes = get_access_codes()
        has_valid_access_code = bool(request.access_code and request.access_code in access_codes)

        if is_hf_space() and not has_valid_access_code:
            if is_gemini and not request.google_api_key:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Access required: enter a valid access code.",
                )
            if not is_gemini and not request.openai_api_key:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Access required: enter a valid access code.",
                )
        if (
            request.access_code
            and not has_valid_access_code
            and not request.openai_api_key
            and not request.google_api_key
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid access code.",
            )
        if has_valid_access_code and not request.openai_api_key and not request.google_api_key:
            allowed, _remaining = consume_access_code_quota(
                request.access_code,
                get_access_code_max_audits(),
            )
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Free quota reached for this access code. Contact Yacin-Christian-Baltagi on LinkedIn for more.",
                )

        tokens = set_request_api_keys(request.openai_api_key, request.google_api_key)
        try:
            initial_state = create_initial_state(
                brand=request.brand,
                llm_provider=request.llm_provider,
            )
            invoke_config = None
            if is_hf_space():
                invoke_config = {
                    "metadata": {
                        "source": "hf_space",
                        "brand": request.brand,
                        "llm_provider": request.llm_provider,
                        "using_access_code": bool(has_valid_access_code),
                        "using_user_keys": bool(request.openai_api_key or request.google_api_key),
                        "access_code": request.access_code if has_valid_access_code else None,
                    }
                }

            final_state = graph.invoke(initial_state, config=invoke_config)
        finally:
            reset_request_api_keys(tokens)

        reputation_score = final_state.get("reputation_score", 0.0)
        recommendations = final_state.get("recommendations", [])
        questions = final_state.get("questions", [])
        num_questions = len(questions)

        response_data = {
            "reputation_score": reputation_score,
            "recommendations": recommendations,
            "brand": request.brand,
            "num_questions": num_questions,
            "llm_provider": request.llm_provider,
        }

        if request.include_details:
            search_results_dict = final_state.get("search_results", {})
            search_results_response = {}
            for question, results_dicts in search_results_dict.items():
                search_results_response[question] = [
                    SearchResultResponse.model_validate(result_dict) for result_dict in results_dicts
                ]

            llm_responses_dict = final_state.get("llm_responses", {})
            llm_responses_response = {}
            for question, response_dict in llm_responses_dict.items():
                if not response_dict:
                    continue
                llm_responses_response[question] = LLMResponse.model_validate(response_dict)

            response_data.update(
                {
                    "questions": questions,
                    "search_results": search_results_response if search_results_response else None,
                    "llm_responses": llm_responses_response if llm_responses_response else None,
                    "brand_context": final_state.get("brand_context") or None,
                    "errors": final_state.get("errors") or None,
                    "search_errors": final_state.get("search_errors") or None,
                    "llm_errors": final_state.get("llm_errors") or None,
                }
            )

        logger.info(
            f"Audit complete for {request.brand}. Score: {reputation_score}, "
            f"Recommendations: {len(recommendations)}, Questions: {num_questions}"
        )

        return AuditResponse(**response_data)

    except HTTPException:
        raise
    except ValueError as e:
        error_msg = format_error_message(e, "audit")
        logger.error(f"Invalid request for audit: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        ) from e
    except Exception as e:
        error_msg = format_error_message(e, "audit")
        logger.error(f"Failed to complete audit for '{request.brand}': {error_msg}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg,
        ) from e
