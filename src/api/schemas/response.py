"""Pydantic models for API responses."""

from pydantic import BaseModel, Field

from src.core.graph.state import LLMResponse, Recommendation

# ============================================================================
# HEALTH ENDPOINT - Response Schema
# ============================================================================


# Endpoint: GET /api/health
class HealthResponse(BaseModel):
    """Response schema for the health check endpoint."""

    status: str = Field(default="healthy", description="API status")
    timestamp: str = Field(description="Current timestamp in ISO format")


# ============================================================================
# DEBUG ENDPOINTS - Response Schemas
# ============================================================================


# Endpoint: POST /api/questions/generate
class QuestionGenerateResponse(BaseModel):
    """Response schema for question generation endpoint (debug)."""

    questions: list[str] = Field(description="Generated questions about the brand")
    brand: str = Field(description="Brand name used for generation")
    num_questions_generated: int = Field(description="Number of questions actually generated")


# Endpoint: POST /api/search/execute
class SearchResultResponse(BaseModel):
    """Response schema for a single search result."""

    title: str = Field(description="Title of the search result")
    url: str = Field(description="URL of the search result")
    snippet: str = Field(description="Text snippet from the page")
    domain: str = Field(description="Domain of the link")


# Endpoint: POST /api/search/execute
class SearchExecuteResponse(BaseModel):
    """Response schema for search execution endpoint (debug)."""

    search_results: list[SearchResultResponse] = Field(
        description="List of search results. This field can be copied directly to `/api/llm/simulate` endpoint."
    )
    query: str = Field(description="Search query that was executed")
    search_tool: str = Field(description="Search tool that was used")
    num_results: int = Field(description="Number of results returned")


# Endpoint: POST /api/llm/simulate
class LLMSimulateResponse(BaseModel):
    """Response schema for LLM simulation endpoint (debug)."""

    llm_response: LLMResponse = Field(description="The simulated LLM response with sources")
    question: str = Field(description="The question that was simulated")
    llm_spec: str = Field(description="The LLM specification that was used for simulation")
    brand: str = Field(description="The brand name used for context (if provided)")


# Endpoint: POST /api/analysis/analyze
class AnalysisAnalyzeResponse(BaseModel):
    """Response schema for analysis endpoint (debug, node 4)."""

    reputation_score: float = Field(description="Overall reputation score from 0.0 to 1.0", ge=0.0, le=1.0)
    recommendations: list[Recommendation] = Field(
        description="List of recommendations to improve brand visibility (GEO-focused)."
    )
    brand: str = Field(description="Brand name that was analyzed")
    num_questions_analyzed: int = Field(description="Number of questions that were included in the analysis")
