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

    llm_display_labels = {
        "gpt-5.2-pro": "ChatGPT Pro — highest quality (GPT-5.2 Pro)",
        "gpt-5.2": "ChatGPT Free/Plus — flagship (GPT-5.2)",
        "o3": "ChatGPT Reasoning — advanced (o3)",
        "gemini-pro": "Gemini Pro — highest quality (gemini-3-pro)",
        "gemini-flash": "Gemini Flash — fastest (gemini-3-flash)",
        "gemini-reasoning": "Gemini Reasoning — stable (gemini-2.5-pro)",
    }

    llm_provider_options = list(llm_display_labels.keys())
    default_index = llm_provider_options.index("gemini-pro")

    llm_provider = st.selectbox(
        "LLM provider",
        options=llm_provider_options,
        index=default_index,  # Default to Gemini Pro
        format_func=lambda key: llm_display_labels.get(key, key),
        help=(
            "Pick the LLM to simulate. ChatGPT options include flagship and reasoning modes; "
            "Gemini options include Pro and Flash."
        ),
    )

    st.caption(
        "Note on speed: 'Highest quality' models (Pro) provide deeper analysis but "
        "can take 2–5 minutes. 'Fastest' models (Flash, Reasoning, Free/Plus) usually complete in about 1 minute."
    )

    include_details = st.checkbox(
        "Include details (see the full process)",
        value=True,
        help="If enabled, detailed intermediate results will be shown below.",
    )

    return brand.strip(), llm_provider, include_details
