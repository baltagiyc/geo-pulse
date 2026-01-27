"""Audit page for GEO Pulse."""

import os

import streamlit as st

from src.frontend.components.audit_form import render_audit_form
from src.frontend.components.details import render_details
from src.frontend.components.results import render_summary
from src.frontend.utils.api_client import APIError, run_audit
from src.frontend.utils.config import is_hf_space


def _init_state() -> None:
    """Initialize Streamlit session state."""
    if "audit_result" not in st.session_state:
        st.session_state.audit_result = None
    if "audit_error" not in st.session_state:
        st.session_state.audit_error = None
    if "audit_running" not in st.session_state:
        st.session_state.audit_running = False
    if "audits_remaining" not in st.session_state:
        st.session_state.audits_remaining = None
    if "access_code" not in st.session_state:
        st.session_state.access_code = ""


def _get_access_codes() -> set[str]:
    """Return access codes from environment (comma-separated)."""
    raw_codes = os.getenv("ACCESS_CODES", "")
    return {code.strip() for code in raw_codes.split(",") if code.strip()}


def _render_access_sidebar() -> dict:
    """Render access code / API key inputs in the sidebar."""
    st.sidebar.header("Access & API Keys")
    st.sidebar.caption("Enter an access code to use the demo keys, or provide your own API keys for unlimited usage.")

    access_code = st.sidebar.text_input("Access code", type="password").strip()
    openai_api_key = st.sidebar.text_input("OpenAI API key (optional)", type="password").strip()
    google_api_key = st.sidebar.text_input("Google API key (optional)", type="password").strip()

    access_codes = _get_access_codes()
    valid_access_code = bool(access_code and access_code in access_codes)
    has_user_keys = bool(openai_api_key or google_api_key)

    free_audits_limit = int(os.getenv("FREE_AUDITS_PER_CODE", "3"))

    if valid_access_code and not has_user_keys:
        if st.session_state.access_code != access_code:
            st.session_state.access_code = access_code
            st.session_state.audits_remaining = free_audits_limit
        st.sidebar.success(f"Access granted — {st.session_state.audits_remaining} audits left")
    elif has_user_keys:
        st.sidebar.info("Using your own API keys (unlimited usage)")
    else:
        st.sidebar.warning("Enter an access code or your own API keys to run an audit.")

    return {
        "access_code": access_code,
        "openai_api_key": openai_api_key,
        "google_api_key": google_api_key,
        "valid_access_code": valid_access_code,
        "has_user_keys": has_user_keys,
    }


def render_audit_page() -> None:
    """Render the main audit page."""
    _init_state()

    st.title("GEO Pulse - Brand Audit")
    st.write(
        "Run a full GEO audit using the LangGraph workflow. "
        "The API generates questions, searches the web, simulates LLM responses, "
        "and produces a visibility score with recommendations."
    )

    access_info = None
    if is_hf_space():
        access_info = _render_access_sidebar()

    with st.form("audit_form"):
        brand, llm_provider, include_details = render_audit_form()
        submitted = st.form_submit_button("Run audit")

    if submitted:
        st.session_state.audit_running = True
        st.session_state.audit_result = None
        st.session_state.audit_error = None

        with st.spinner("Running audit... This may take a few minutes."):
            try:
                access_code = None
                openai_api_key = None
                google_api_key = None

                if is_hf_space() and access_info:
                    access_code = access_info["access_code"] if access_info["valid_access_code"] else None
                    openai_api_key = access_info["openai_api_key"] or None
                    google_api_key = access_info["google_api_key"] or None

                    if not access_info["valid_access_code"] and not access_info["has_user_keys"]:
                        raise APIError(
                            status_code=400,
                            detail="Access required: enter a valid access code or your own API keys.",
                        )

                    if access_info["valid_access_code"] and not access_info["has_user_keys"]:
                        remaining = st.session_state.audits_remaining or 0
                        if remaining <= 0:
                            raise APIError(
                                status_code=400,
                                detail="Free quota reached. Please enter your own API keys to continue.",
                            )
                        st.session_state.audits_remaining = max(remaining - 1, 0)

                result = run_audit(
                    brand=brand,
                    llm_provider=llm_provider,
                    include_details=include_details,
                    access_code=access_code,
                    openai_api_key=openai_api_key,
                    google_api_key=google_api_key,
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


if __name__ == "__main__":
    render_audit_page()
