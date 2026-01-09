"""Pydantic models for API requests."""

from pydantic import BaseModel, Field


class QuestionGenerateRequest(BaseModel):
    """Request schema for question generation endpoint."""

    brand: str = Field(description="Name of the brand to generate questions for")
    num_questions: int = Field(default=2, ge=1, le=10, description="Number of questions to generate (1-10)")
    question_llm: str = Field(
        default="openai:gpt-4o-mini",
        description='LLM to use for generating questions. Format: "provider:model" (e.g., "openai:gpt-4o-mini", "openai:gpt-4"). This is the LLM used internally to generate questions, separate from the LLM being audited.',
    )
