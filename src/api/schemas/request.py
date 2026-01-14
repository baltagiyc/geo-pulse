"""Pydantic models for API requests."""

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from src.core.graph.state import LLMResponse

if TYPE_CHECKING:
    from src.api.schemas.response import SearchResultResponse

# ============================================================================
# DEBUG ENDPOINTS - Request Schemas
# ============================================================================


# Endpoint: POST /api/questions/generate
class QuestionGenerateRequest(BaseModel):
    """Request schema for question generation endpoint (debug)."""

    brand: str = Field(description="Name of the brand to generate questions for")
    num_questions: int = Field(default=2, ge=1, le=10, description="Number of questions to generate (1-10)")
    question_llm: str = Field(
        default="openai:gpt-4o-mini",
        description=(
            'LLM to use for generating questions. Format: "provider:model" '
            '(e.g., "openai:gpt-4o-mini", "openai:gpt-4"). This is the LLM used internally to '
            "generate questions, separate from the LLM being audited."
        ),
    )


# Endpoint: POST /api/search/execute
class SearchExecuteRequest(BaseModel):
    """Request schema for search execution endpoint (debug)."""

    query: str = Field(
        min_length=1,
        description=(
            "Search query string. You can either type your own query manually, "
            "or copy-paste one of the questions returned by `/api/questions/generate`."
        ),
    )
    max_results: int = Field(default=5, ge=1, le=20, description="Maximum number of results to return (1-20)")
    search_tool: str = Field(
        default="tavily",
        description=(
            'Search tool to use. Options: "tavily" (default), "bing" (to be implemented), '
            '"google" (to be implemented). For testing individual search tools in isolation.'
        ),
    )


# Endpoint: POST /api/llm/simulate
class LLMSimulateRequest(BaseModel):
    """Request schema for LLM simulation endpoint (debug)."""

    question: str = Field(
        min_length=1,
        description=(
            "The question to simulate an LLM response for. "
            "You can either type your own question, or copy-paste a question from "
            "`/api/questions/generate` (questions field) or from the `query` used in "
            "`/api/search/execute`."
        ),
    )
    search_results: list["SearchResultResponse"] = Field(
        description=(
            "List of search results to use for the LLM response. "
            "You can copy-paste the `search_results` field directly from `/api/search/execute` response."
        ),
    )
    llm_spec: str = Field(
        default="openai:gpt-4",
        description=(
            'LLM specification for simulation. Format: "provider:model" '
            '(e.g., "openai:gpt-4", "openai:gpt-4o-mini") or simple format "gpt-4". '
            "This is the LLM being audited (simulated)."
        ),
    )
    brand: str = Field(
        default="",
        description="Optional brand name for context in the prompt. Helps the LLM provide more relevant responses.",
    )


# Endpoint: POST /api/analysis/analyze
class AnalysisAnalyzeRequest(BaseModel):
    """Request schema for analysis endpoint (debug, node 4)."""

    brand: str = Field(description="Name of the brand being analyzed")
    question: str = Field(
        description=(
            "The question that was analyzed. "
            "You can copy-paste this from the `question` field of `/api/llm/simulate` response, "
            "or from the `query` field of `/api/search/execute` response."
        )
    )
    llm_response: LLMResponse = Field(
        description=(
            "The LLM response for this question. "
            "You can copy-paste the `llm_response` field directly from `/api/llm/simulate` response."
        )
    )
    search_results: list["SearchResultResponse"] = Field(
        description=(
            "List of search results for this question. "
            "You can copy-paste the `search_results` field directly from `/api/search/execute` response."
        )
    )


# Resolve forward references after all models are defined
def _resolve_forward_refs() -> None:
    """Resolve forward references in request schemas."""
    from src.api.schemas.response import SearchResultResponse  # noqa: F401

    LLMSimulateRequest.model_rebuild()
    AnalysisAnalyzeRequest.model_rebuild()


_resolve_forward_refs()
