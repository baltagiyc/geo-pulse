"""Result rendering components."""

from collections import defaultdict

import streamlit as st


def _priority_rank(priority: str) -> int:
    priority_map = {"high": 0, "medium": 1, "low": 2}
    return priority_map.get(priority.lower(), 3)


def render_summary(result: dict) -> None:
    """Render the main summary: score + recommendations."""
    st.subheader("Audit Results")

    reputation_score = float(result.get("reputation_score", 0.0))
    brand = result.get("brand", "Unknown")
    num_questions = result.get("num_questions", 0)

    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.metric("Reputation Score", f"{reputation_score:.2f}")
        st.progress(min(max(reputation_score, 0.0), 1.0))

    with col_right:
        st.write(f"**Brand:** {brand}")
        st.write(f"**Questions analyzed:** {num_questions}")

    recommendations = result.get("recommendations", [])

    st.subheader("Recommendations")
    if not recommendations:
        st.info("No recommendations available.")
        return

    grouped = defaultdict(list)
    for rec in recommendations:
        priority = rec.get("priority", "medium")
        grouped[priority].append(rec)

    ordered = sorted(recommendations, key=lambda r: _priority_rank(r.get("priority", "medium")))
    for idx, rec in enumerate(ordered, start=1):
        priority = rec.get("priority", "medium").capitalize()
        rec_type = rec.get("type", "recommendation")
        description = rec.get("description", "")

        st.write(f"{idx}. **{priority}** — `{rec_type}`")
        if description:
            st.write(description)
