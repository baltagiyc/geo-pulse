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
    """Render access code input in the sidebar."""
    st.sidebar.header("Access Control")
    st.sidebar.caption("This tool is in private access. Enter an access code to run the audit.")

    access_code = st.sidebar.text_input("Access code", type="password").strip()

    # API key inputs are removed on HF Spaces to prioritize lead generation
    openai_api_key = ""
    google_api_key = ""

    access_codes = _get_access_codes()
    valid_access_code = bool(access_code and access_code in access_codes)
    has_user_keys = False  # Always False on HF Spaces now

    free_audits_limit = int(os.getenv("ACCESS_CODE_MAX_AUDITS", os.getenv("FREE_AUDITS_PER_CODE", "3")))

    if valid_access_code:
        if st.session_state.access_code != access_code:
            st.session_state.access_code = access_code
            st.session_state.audits_remaining = free_audits_limit
        st.sidebar.success(f"Access granted — {st.session_state.audits_remaining} audits left")
    elif access_code:
        st.sidebar.warning("Access code will be validated by the server when you run an audit.")
    else:
        st.sidebar.warning("Enter an access code to run an audit.")

    st.sidebar.info("Want a free access code? Contact Yacin-Christian-Baltagi on LinkedIn.")

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

    st.title("GEO Pulse — Brand Audit")
    st.markdown("### Stop being invisible to AI.")

    st.write(
        "GEO (Generative Engine Optimization) is the new SEO. "
        "When users ask ChatGPT, Gemini, or Perplexity for recommendations, **does your brand show up?**"
    )
    st.write("We help you track and improve your AI visibility.")

    # How it works section
    st.subheader("How it works")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Audit**")
        st.caption("We scan how your brand is perceived across the LLMs of your choice.")
    with col2:
        st.markdown("**Score**")
        st.caption("You get a 'Visibility Score' comparing you to your competitors.")
    with col3:
        st.markdown("**Action**")
        st.caption("We provide concrete content recommendations to improve your AI ranking.")

    # Why it matters
    st.info(
        "**Why it matters:** Traditional search (SEO) is dying as users shift from Google to AI for answers. "
        "AI-driven discovery is how your next customers will find you. "
        "If you aren't in the AI's training data or context, you don't exist."
    )

    # Engineering Excellence
    with st.expander("🛠 Engineering Excellence (Production-Grade Specs)"):
        st.write("Built for reliability and scale.")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Orchestration:** LangGraph, LangChain")
            st.markdown("**Backend:** FastAPI, Pydantic, uv")
        with c2:
            st.markdown("**Deployment & Quality:** Docker, Pytest, Hugging Face, Ruff")
            st.markdown("**Models & UI:** OpenAI, Gemini, Streamlit")
    st.caption("Want free access? Request an access code by contacting yacin-christian-baltagi on LinkedIn.")

    access_info = None
    if is_hf_space():
        access_info = _render_access_sidebar()

    with st.form("audit_form"):
        brand, llm_provider, include_details = render_audit_form()
        submitted = st.form_submit_button("Run audit")

    if submitted:
        if not brand:
            st.error("Please enter a brand name.")
            st.stop()

        st.session_state.audit_running = True
        st.session_state.audit_result = None
        st.session_state.audit_error = None

        with st.spinner("Running audit... This will take between 2 and 3 minutes."):
            try:
                access_code = None
                openai_api_key = None
                google_api_key = None

                if is_hf_space() and access_info:
                    access_code = access_info["access_code"] or None
                    openai_api_key = access_info["openai_api_key"] or None
                    google_api_key = access_info["google_api_key"] or None

                    if not access_code:
                        raise APIError(
                            status_code=400,
                            detail="Access required: enter a valid access code.",
                        )

                    if access_info["valid_access_code"]:
                        remaining = st.session_state.audits_remaining or 0
                        if remaining <= 0:
                            raise APIError(
                                status_code=400,
                                detail="Free quota reached for this access code. Contact Yacin for more.",
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
