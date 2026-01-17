"""Audit form component."""

import streamlit as st


def render_audit_form() -> tuple[str, str, bool]:
    """Render the audit form and return user inputs."""
    st.subheader("Audit Configuration")

    brand = st.text_input(
        "Brand name",
        value="Nike",
        help="Enter the brand to audit (e.g., Nike, Brevo, Amazon).",
    )

    llm_provider = st.selectbox(
        "LLM provider",
        options=[
            "gpt-4",
            "gpt-4o",
            "gpt-4o-mini",
        ],
        index=0,
        help="Select the LLM provider to simulate. Some providers may fall back to OpenAI for now.",
    )

    include_details = st.checkbox(
        "Include details (questions, search results, LLM responses)",
        value=False,
        help="If enabled, detailed intermediate results will be shown below.",
    )

    return brand.strip(), llm_provider, include_details
