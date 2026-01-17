from dotenv import load_dotenv
from langgraph.graph import END, StateGraph

from src.core.graph.nodes import (
    brand_context_generator_node,
    llm_simulator_node,
    question_generator_node,
    response_analyst_node,
    search_executor_node,
)
from src.core.graph.state import GEOState

load_dotenv()


def create_initial_state(brand: str, llm_provider: str = "gpt-4") -> GEOState:
    """
    Create an initial state for the GEO audit graph.

    The user only needs to provide brand and llm_provider.
    The search tool is automatically determined from llm_provider (future feature).
    For now, we use Tavily as default for all LLMs.

    Args:
        brand: Name of the brand to audit (e.g., "Nike", "Brevo", "Amazon")
        llm_provider: LLM provider to simulate (e.g., "gpt-4", "gemini", "perplexity")
                     Future: will automatically map to correct search tool:
                     - chatgpt/gpt-4 -> bing
                     - gemini -> google
                     - perplexity -> perplexity (special case)

    Returns:
        Initialized GEOState with all required fields
    """
    return {
        "messages": [],
        "brand": brand,
        "llm_provider": llm_provider,
        "brand_context": None,
        "questions": [],
        "search_results": {},
        "llm_responses": {},
        "reputation_score": 0.0,
        "recommendations": [],
        "errors": [],
        "search_errors": [],
        "llm_errors": [],
    }


def create_audit_graph() -> StateGraph:
    """
    Create and compile the GEO audit graph.

    The graph follows a linear flow:
    0. brand_context_generator_node: Generate factual context about the brand
    1. question_generator_node: Generate questions about the brand
    2. search_executor_node: Execute web searches for each question
    3. llm_simulator_node: Simulate LLM responses based on search results
    4. response_analyst_node: Analyze responses and generate score + recommendations

    Returns:
        Compiled LangGraph ready to be invoked
    """
    # Create the graph with our custom state
    graph = StateGraph(GEOState)

    # Add all nodes
    graph.add_node("brand_context_generator", brand_context_generator_node)
    graph.add_node("question_generator", question_generator_node)
    graph.add_node("search_executor", search_executor_node)
    graph.add_node("llm_simulator", llm_simulator_node)
    graph.add_node("response_analyst", response_analyst_node)

    # Define the linear flow
    graph.set_entry_point("brand_context_generator")
    graph.add_edge("brand_context_generator", "question_generator")
    graph.add_edge("question_generator", "search_executor")
    graph.add_edge("search_executor", "llm_simulator")
    graph.add_edge("llm_simulator", "response_analyst")
    graph.add_edge("response_analyst", END)

    # Compile and return the graph
    return graph.compile()
