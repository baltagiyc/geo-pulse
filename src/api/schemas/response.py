"""Pydantic models for API responses."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""

    status: str = Field(default="healthy", description="API status")
    timestamp: str = Field(description="Current timestamp in ISO format")


class QuestionGenerateResponse(BaseModel):
    """Response schema for question generation endpoint."""

    questions: list[str] = Field(description="Generated questions about the brand")
    brand: str = Field(description="Brand name used for generation")
    num_questions_generated: int = Field(description="Number of questions actually generated")


class SearchResultResponse(BaseModel):
    """Response schema for a single search result."""

    title: str = Field(description="Title of the search result")
    url: str = Field(description="URL of the search result")
    snippet: str = Field(description="Text snippet from the page")
    domain: str = Field(description="Domain of the link")


class SearchExecuteResponse(BaseModel):
    """Response schema for search execution endpoint."""

    results: list[SearchResultResponse] = Field(description="List of search results")
    query: str = Field(description="Search query that was executed")
    search_tool: str = Field(description="Search tool that was used")
    num_results: int = Field(description="Number of results returned")
