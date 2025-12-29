from typing import TypedDict, Annotated, List, Dict
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


# We use Pydantic models below for parts of our state
# (mainly configs and what flows between nodes)

class SearchResult(BaseModel):
    """
    Represents a single search result from web search engines.
    """
    title: str = Field(description="Title of the search result")
    url: str = Field(description="URL of the search result")
    snippet: str = Field(description="Text snippet from the page")
    domain: str = Field(description="Domain of the link")


class LLMResponse(BaseModel):
    """
    Represents a response from an LLM with its sources.
    """
    llm_name: str = Field(description="Name of the LLM that gave the answer (e.g., 'chatgpt', 'gemini')")
    response: str = Field(description="The response text from the LLM")
    sources: List[str] = Field(default=[], description="URLs cited by the LLM in its response")


class Recommendation(BaseModel):
    """
    Represents a recommendation to improve brand visibility.
    """
    title: str = Field(description="Title of the recommendation")
    description: str = Field(description="Description of the recommendation")
    priority: str = Field(default="medium", description="Priority level: 'high', 'medium', or 'low'")


# We define our own custom state for the graph, as we have specific requirements for what needs to be tracked at each stage of the workflow

class GEOState(TypedDict):
    """
    State for the GEO Agent Workflow.
    
    This state tracks:
    - Input: brand and llm_provider
    - Flow: questions, search_results, llm_responses (between nodes)
    - Output: reputation_score and recommendations
    - Errors: errors, search_errors, llm_errors for tracking failures
    """
    
    # LangGraph conversation history
    messages: Annotated[List[BaseMessage], add_messages]
    
    # input
    brand: str  # we take only the name of the brand we wanna audit (eg: Nike, Brevo, Amazon etc)
    llm_provider: str  # LLM where we wanna checke the visibility: "chatgpt", "gemini", "perplexity", etc. (default: "gpt-4")
    
    # to be changed by the nodes
    questions: List[str]  # first agent will generated tyicals questions that any user can ask about the brand
    search_results: Dict[str, List[Dict]]  # {question: [SearchResult as dict]}
    llm_responses: Dict[str, Dict]  # {question: LLMResponse as dict}
    
    # output
    reputation_score: float  # from 0.0 to 1.0 of the brand
    recommendations: List[Dict]  # [Recommendation as dict]
    
    # error tracking
    errors: List[str]  # general errors
    search_errors: List[str]  # errors from search operations
    llm_errors: List[str]  # errors from LLM operations
