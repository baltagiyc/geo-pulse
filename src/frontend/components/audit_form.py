"""Audit form component."""

import streamlit as st


def render_audit_form() -> tuple[str, str, bool]:
    """Render the audit form and return user inputs."""
    st.subheader("Audit Configuration")

    brand = st.text_input(
        "Brand name",
        placeholder="e.g., Nike, Brevo, Amazon",
        help="Enter the brand to audit.",
    )

    llm_provider = st.selectbox(
        "LLM provider",
        options=[
            "gpt-5.2-pro",  # ChatGPT Pro (Highest Reasoning)
            "gpt-5.2",  # ChatGPT Plus/Free (Flagship)
            "o3",  # Advanced Reasoning
            "gpt-4.5",  # API Optimized
            "gemini-3-pro",  # Gemini Pro (Intelligence)
            "gemini-3-flash",  # Gemini Flash (Speed)
            "gemini-2.5-pro",  # Stable reasoning mode
        ],
        index=1,  # Default to gpt-5.2 (Flagship)
        help="Select the LLM provider to simulate. Supports ChatGPT (GPT-5.2 Pro/Plus) and Gemini (Pro, Flash, Reasoning) models.",
    )

    include_details = st.checkbox(
        "Include details (see the full process)",
        value=True,
        help="If enabled, detailed intermediate results will be shown below.",
    )

    return brand.strip(), llm_provider, include_details
