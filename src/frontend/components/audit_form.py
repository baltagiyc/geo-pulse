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
            "gpt-5.2",  # Latest (2025)
            "gpt-5",
            "gpt-4.1",  # API-optimized
            "gpt-4",
            "gemini",  # Gemini Pro (default)
            "gemini-pro",  # Gemini Pro (explicit)
            "gemini-flash",  # Gemini Flash (fast)
            "gemini-reasoning",  # Gemini Reasoning (advanced thinking)
        ],
        index=0,  # Default to gpt-5.2 (latest)
        help="Select the LLM provider to simulate. Supports ChatGPT (GPT-5.2, GPT-5) and Gemini (Pro, Flash, Reasoning) models.",
    )

    include_details = st.checkbox(
        "Include details (see the full process)",
        value=True,
        help="If enabled, detailed intermediate results will be shown below.",
    )

    return brand.strip(), llm_provider, include_details
