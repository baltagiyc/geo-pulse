"""Result rendering components."""

import re
from collections import defaultdict

import streamlit as st


def _priority_rank(priority: str) -> int:
    priority_map = {"high": 0, "medium": 1, "low": 2}
    return priority_map.get(priority.lower(), 3)


def render_summary(result: dict) -> None:
    """Render the main summary: score + recommendations."""
    st.subheader("Audit Results")

    reputation_score = float(result.get("reputation_score", 0.0))
    display_score = reputation_score if reputation_score > 0 else 0.10
    brand = result.get("brand", "Unknown")
    execution_time_seconds = result.get("execution_time_seconds")

    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.metric("Reputation Score", f"{display_score:.2f}")

        # Determine color based on score
        if display_score < 0.40:
            color = "#FF4B4B"  # Red
        elif display_score < 0.70:
            color = "#FFAA00"  # Yellow/Orange
        else:
            color = "#28A745"  # Green

        # Custom HTML Progress Bar
        st.markdown(
            f"""
            <div style="background-color: #f0f2f6; border-radius: 5px; height: 10px; width: 100%;">
                <div style="background-color: {color}; border-radius: 5px; height: 10px; width: {display_score * 100}%;"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        st.write(f"**Brand:** {brand}")
        if execution_time_seconds is not None:
            st.write(f"**Execution time:** {execution_time_seconds:.1f}s")

    recommendations = result.get("recommendations", [])
    questions = result.get("questions", [])
    llm_provider = result.get("llm_provider")

    if llm_provider:
        st.markdown("")
        st.caption(
            f"The audit and recommendations below focus on improving **visibility** of **{brand}** on **{llm_provider}**."
        )

    if questions:
        st.markdown("---")
        st.markdown("### Simulated User Journeys on IA")
        st.write(f"Typical questions users might ask about **{brand}**:")
        for i, q in enumerate(questions, start=1):
            st.write(f"{i}. *{q}*")

    def _detect_related_questions(text: str) -> list[tuple[int, str]]:
        """Detect all Q1/Q2/Q3 references and return list of (number, text)."""
        if not text or not questions:
            return []

        detected = []
        for idx, question in enumerate(questions, start=1):
            if not question:
                continue
            # Detect references like "Q2", "Q2's", "Question 2"
            reference_patterns = [
                rf"\bQ{idx}\b",
                rf"\bQ{idx}'s\b",
                rf"\bQuestion\s+{idx}\b",
                rf"\bQuestion\s+{idx}'s\b",
            ]
            if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in reference_patterns):
                detected.append((idx, question))

        return detected

    st.markdown("---")
    st.subheader("Strategic Recommendations")
    if not recommendations:
        st.info("No recommendations available.")
        return

    grouped = defaultdict(list)
    for rec in recommendations:
        priority = rec.get("priority", "medium")
        grouped[priority].append(rec)

    ordered = sorted(recommendations, key=lambda r: _priority_rank(r.get("priority", "medium")))
    for idx, rec in enumerate(ordered, start=1):
        priority_raw = rec.get("priority", "medium")
        priority = priority_raw.capitalize()
        description = rec.get("description", "")

        badge_class = "gp-badge-medium"
        if priority_raw.lower() == "high":
            badge_class = "gp-badge-high"
        elif priority_raw.lower() == "low":
            badge_class = "gp-badge-low"

        st.markdown(
            f'<span class="gp-badge {badge_class}">{priority}</span> ' f"**Recommendation {idx}**",
            unsafe_allow_html=True,
        )
        if description:
            detected_qs = _detect_related_questions(description)
            if detected_qs:
                st.caption("**Based on potential user queries about your brand:**")
                for q_num, q_text in detected_qs:
                    st.caption(f"*{q_text}*")
            st.write(description)
        if idx < len(ordered):
            st.markdown("---")
