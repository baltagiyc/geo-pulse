"""Audit page for GEO Pulse."""

import streamlit as st

from src.frontend.components.audit_form import render_audit_form
from src.frontend.components.details import render_details
from src.frontend.components.results import render_summary
from src.frontend.utils.api_client import APIError, run_audit


def _init_state() -> None:
    """Initialize Streamlit session state."""
    if "audit_result" not in st.session_state:
        st.session_state.audit_result = None
    if "audit_error" not in st.session_state:
        st.session_state.audit_error = None
    if "audit_running" not in st.session_state:
        st.session_state.audit_running = False


def render_audit_page() -> None:
    """Render the main audit page."""
    _init_state()

    st.title("GEO Pulse - Brand Audit")
    st.write(
        "Run a full GEO audit using the LangGraph workflow. "
        "The API generates questions, searches the web, simulates LLM responses, "
        "and produces a visibility score with recommendations."
    )

    with st.form("audit_form"):
        brand, llm_provider, include_details = render_audit_form()
        submitted = st.form_submit_button("Run audit")

    if submitted:
        st.session_state.audit_running = True
        st.session_state.audit_result = None
        st.session_state.audit_error = None

        with st.spinner("Running audit... This may take a few minutes."):
            try:
                result = run_audit(
                    brand=brand,
                    llm_provider=llm_provider,
                    include_details=include_details,
                )
                st.session_state.audit_result = result
            except APIError as exc:
                st.session_state.audit_error = exc.detail
            except Exception as exc:  # noqa: BLE001 - fallback for unexpected errors
                st.session_state.audit_error = str(exc)

        st.session_state.audit_running = False

    if st.session_state.audit_error:
        st.error(st.session_state.audit_error)

    if st.session_state.audit_result:
        result = st.session_state.audit_result
        render_summary(result)

        if result.get("questions"):
            render_details(result)
