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
