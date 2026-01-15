"""Pydantic models for API requests."""

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from src.core.graph.state import LLMResponse

if TYPE_CHECKING:
    from src.api.schemas.response import SearchResultResponse

# ============================================================================
# MAIN AUDIT ENDPOINT - Request Schema
# ============================================================================


# Endpoint: POST /api/audit
class AuditRequest(BaseModel):
    """Request schema for the main audit endpoint."""

    brand: str = Field(
        description="Name of the brand to audit (e.g., 'Nike', 'Brevo', 'Amazon')",
        examples=["Nike", "Brevo", "Amazon"],
    )
    llm_provider: str = Field(
        default="gpt-4",
        description=(
            "LLM provider to simulate/audit. Options: 'gpt-4', 'gpt-4o', 'gpt-4o-mini', "
            "'gemini', 'claude', 'perplexity' (default: 'gpt-4'). "
            "The search tool is automatically determined from the LLM provider."
        ),
        examples=["gpt-4", "gpt-4o", "gemini"],
    )
    include_details: bool = Field(
        default=False,
        description=(
            "If True, includes detailed intermediate results (questions, search_results, "
            "llm_responses, errors) in the response. If False, returns only the final "
            "reputation_score and recommendations."
        ),
        examples=[False, True],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "brand": "Nike",
                    "llm_provider": "gpt-4",
                    "include_details": False,
                },
                {
                    "brand": "Brevo",
                    "llm_provider": "gpt-4o",
                    "include_details": True,
                },
            ]
        }
    }


# ============================================================================
# DEBUG ENDPOINTS - Request Schemas
# ============================================================================


# Endpoint: POST /api/questions/generate
class QuestionGenerateRequest(BaseModel):
    """Request schema for question generation endpoint (debug)."""

    brand: str = Field(
        description="Name of the brand to generate questions for",
        examples=["Nike", "Brevo", "Amazon"],
    )
    num_questions: int = Field(
        default=2, ge=1, le=10, description="Number of questions to generate (1-10)", examples=[2, 5, 10]
    )
    question_llm: str = Field(
        default="openai:gpt-4o-mini",
        description=(
            'LLM to use for generating questions. Format: "provider:model" '
            '(e.g., "openai:gpt-4o-mini", "openai:gpt-4"). This is the LLM used internally to '
            "generate questions, separate from the LLM being audited."
        ),
        examples=["openai:gpt-4o-mini", "openai:gpt-4"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "brand": "Nike",
                    "num_questions": 2,
                    "question_llm": "openai:gpt-4o-mini",
                },
                {
                    "brand": "Nike",
                    "num_questions": 5,
                    "question_llm": "openai:gpt-4",
                },
            ]
        }
    }


# Endpoint: POST /api/search/execute
class SearchExecuteRequest(BaseModel):
    """Request schema for search execution endpoint (debug)."""

    query: str = Field(
        min_length=1,
        description=(
            "Search query string. You can either type your own query manually, "
            "or copy-paste one of the questions returned by `/api/questions/generate`."
        ),
        examples=[
            "What are the best Nike running shoes?",
            "Nike vs Adidas: which brand is better?",
            "What are the main complaints and criticisms about Nike?",
        ],
    )
    max_results: int = Field(
        default=5, ge=1, le=20, description="Maximum number of results to return (1-20)", examples=[5, 10, 20]
    )
    search_tool: str = Field(
        default="tavily",
        description=(
            'Search tool to use. Options: "tavily" (default), "bing" (to be implemented), '
            '"google" (to be implemented). For testing individual search tools in isolation.'
        ),
        examples=["tavily"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "What are the best Nike running shoes?",
                    "max_results": 5,
                    "search_tool": "tavily",
                },
                {
                    "query": "Nike vs Adidas: which brand is better?",
                    "max_results": 10,
                    "search_tool": "tavily",
                },
            ]
        }
    }


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
        examples=["What are the best Nike running shoes?"],
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
        examples=["openai:gpt-4", "gpt-4", "openai:gpt-4o-mini"],
    )
    brand: str = Field(
        default="",
        description="Optional brand name for context in the prompt. Helps the LLM provide more relevant responses.",
        examples=["Nike", ""],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "question": "What are the best Nike running shoes?",
                    "search_results": [
                        {
                            "title": "Best Nike Running Shoes 2024",
                            "url": "https://www.nike.com/running-shoes",
                            "snippet": "Discover our top-rated running shoes for every type of runner, from daily training to race day.",
                            "domain": "nike.com",
                        },
                        {
                            "title": "Nike Air Zoom Pegasus 40 Review",
                            "url": "https://www.runnersworld.com/nike-pegasus-40",
                            "snippet": "The Nike Air Zoom Pegasus 40 is one of the most popular running shoes for daily training.",
                            "domain": "runnersworld.com",
                        },
                        {
                            "title": "Nike vs Adidas Running Shoes Comparison",
                            "url": "https://www.gearpatrol.com/nike-vs-adidas",
                            "snippet": "Both brands offer excellent options, but Nike excels in cushioning technology.",
                            "domain": "gearpatrol.com",
                        },
                    ],
                    "llm_spec": "openai:gpt-4",
                    "brand": "Nike",
                }
            ]
        }
    }


# Endpoint: POST /api/analysis/analyze
class AnalysisAnalyzeRequest(BaseModel):
    """Request schema for analysis endpoint (debug, node 4)."""

    brand: str = Field(description="Name of the brand being analyzed", examples=["Nike", "Brevo", "Amazon"])
    question: str = Field(
        description=(
            "The question that was analyzed. "
            "You can copy-paste this from the `question` field of `/api/llm/simulate` response, "
            "or from the `query` field of `/api/search/execute` response."
        ),
        examples=["What are the best Nike running shoes?"],
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

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "brand": "Nike",
                    "question": "What are the best Nike running shoes?",
                    "llm_response": {
                        "llm_name": "gpt-4",
                        "response": "Nike offers several excellent running shoes, with the Air Zoom Pegasus 40 being one of the most popular for daily training. The shoe provides excellent cushioning and durability. For race day, the Vaporfly series is highly regarded. Nike's strength lies in their innovative cushioning technology, particularly their Air Zoom and React foam systems.",
                        "sources": [
                            "https://www.nike.com/running-shoes",
                            "https://www.runnersworld.com/nike-pegasus-40",
                        ],
                    },
                    "search_results": [
                        {
                            "title": "Best Nike Running Shoes 2024",
                            "url": "https://www.nike.com/running-shoes",
                            "snippet": "Discover our top-rated running shoes for every type of runner, from daily training to race day.",
                            "domain": "nike.com",
                        },
                        {
                            "title": "Nike Air Zoom Pegasus 40 Review",
                            "url": "https://www.runnersworld.com/nike-pegasus-40",
                            "snippet": "The Nike Air Zoom Pegasus 40 is one of the most popular running shoes for daily training.",
                            "domain": "runnersworld.com",
                        },
                        {
                            "title": "Nike vs Adidas Running Shoes Comparison",
                            "url": "https://www.gearpatrol.com/nike-vs-adidas",
                            "snippet": "Both brands offer excellent options, but Nike excels in cushioning technology.",
                            "domain": "gearpatrol.com",
                        },
                    ],
                }
            ]
        }
    }


# Resolve forward references after all models are defined
def _resolve_forward_refs() -> None:
    """Resolve forward references in request schemas."""
    from src.api.schemas.response import SearchResultResponse  # noqa: F401

    LLMSimulateRequest.model_rebuild()
    AnalysisAnalyzeRequest.model_rebuild()


_resolve_forward_refs()
