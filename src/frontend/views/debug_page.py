"""Debug page for GEO Pulse."""

import streamlit as st

from src.frontend.utils.config import get_api_base_url


def render_debug_page() -> None:
    """Render the debug page with helpful links."""
    st.title("GEO Pulse - Debug Tools")
    st.write(
        "Use the debug endpoints to test each node independently. "
        "These endpoints support a copy-paste workflow to chain results between nodes."
    )

    api_base_url = get_api_base_url()

    st.subheader("API Links")
    st.markdown(f"- API Base URL: `{api_base_url}`")
    st.markdown(f"- Swagger UI: {api_base_url}/docs")
    st.markdown(f"- OpenAPI JSON: {api_base_url}/openapi.json")

    st.subheader("Debug Endpoints")
    st.markdown("- `/api/brand/context` — Generate brand context (node 0)")
    st.markdown("- `/api/questions/generate` — Generate questions (node 1)")
    st.markdown("- `/api/search/execute` — Run web search (node 2)")
    st.markdown("- `/api/llm/simulate` — Simulate LLM response (node 3)")
    st.markdown("- `/api/analysis/analyze` — Analyze response (node 4)")

    st.info(
        "Tip: Use the Swagger UI to copy outputs directly into the next endpoint. "
        "This mirrors the LangGraph workflow step by step."
    )


if __name__ == "__main__":
    render_debug_page()
