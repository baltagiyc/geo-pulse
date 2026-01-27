"""Detailed results rendering."""

import streamlit as st


def render_details(result: dict) -> None:
    """Render detailed results in expanders."""
    st.subheader("Details")

    questions = result.get("questions") or []
    search_results = result.get("search_results") or {}
    llm_responses = result.get("llm_responses") or {}
    brand_context = result.get("brand_context") or ""
    errors = result.get("errors") or []
    search_errors = result.get("search_errors") or []
    llm_errors = result.get("llm_errors") or []

    with st.expander("Questions", expanded=False):
        st.info(
            "These questions were generated based on the brand context to represent what real users might ask about your brand."
        )
        if not questions:
            st.info("No questions available.")
        else:
            for q in questions:
                st.write(f"- {q}")

    with st.expander("Brand Context", expanded=False):
        if not brand_context:
            st.info("No brand context available.")
        else:
            st.write(brand_context)

    with st.expander("Search Results", expanded=False):
        st.info(
            "These are live web search results. We scan these sources to understand what the LLM 'sees' when it looks for your brand."
        )
        if not search_results:
            st.info("No search results available.")
        else:
            for question, results in search_results.items():
                st.markdown(f"**Question:** {question}")
                if not results:
                    st.write("No results.")
                    continue
                for item in results:
                    title = item.get("title", "Untitled")
                    url = item.get("url", "")
                    snippet = item.get("snippet", "")
                    domain = item.get("domain", "")
                    if url:
                        st.markdown(f"- [{title}]({url}) — `{domain}`")
                    else:
                        st.write(f"- {title} — `{domain}`")
                    if snippet:
                        st.write(snippet)

    with st.expander("LLM Responses", expanded=False):
        st.info(
            "These are the simulated responses you would get if you asked these questions directly on ChatGPT, Gemini, or Claude."
        )
        if not llm_responses:
            st.info("No LLM responses available.")
        else:
            for question, response in llm_responses.items():
                st.markdown(f"**Question:** {question}")
                st.write(response.get("response", ""))
                sources = response.get("sources", [])
                if sources:
                    st.write("Sources:")
                    for source in sources:
                        st.write(f"- {source}")

    with st.expander("Errors", expanded=False):
        if not (errors or search_errors or llm_errors):
            st.info("No errors reported.")
        if errors:
            st.write("General errors:")
            for err in errors:
                st.write(f"- {err}")
        if search_errors:
            st.write("Search errors:")
            for err in search_errors:
                st.write(f"- {err}")
        if llm_errors:
            st.write("LLM errors:")
            for err in llm_errors:
                st.write(f"- {err}")
