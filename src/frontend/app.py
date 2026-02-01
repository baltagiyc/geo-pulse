"""Streamlit entrypoint for GEO Pulse frontend."""

import sys
from pathlib import Path

import streamlit as st

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.frontend.utils.config import is_hf_space
from src.frontend.views.audit_page import render_audit_page
from src.frontend.views.debug_page import render_debug_page


def main() -> None:
    """Render the Streamlit app."""
    st.set_page_config(page_title="GEO Pulse", layout="wide")

    st.markdown(
        """
        <style>
        :root {
          --gp-bg: #0f1117;
          --gp-panel: #161b22;
          --gp-card: #1f2630;
          --gp-text: #e6edf3;
          --gp-muted: #9aa4b2;
          --gp-accent: #7c3aed;
          --gp-accent-2: #22c55e;
          --gp-border: #2b3442;
        }

        .stApp {
          background: radial-gradient(1200px 700px at 20% -10%, #1b1f2b 0%, #0f1117 60%) !important;
          color: var(--gp-text);
        }

        .gp-hero {
          background: linear-gradient(135deg, rgba(124,58,237,0.25), rgba(34,197,94,0.15));
          border: 1px solid var(--gp-border);
          border-radius: 16px;
          padding: 24px 28px;
          margin: 6px 0 18px 0;
        }

        .gp-hero-title {
          font-size: 38px;
          font-weight: 700;
          margin-bottom: 8px;
        }

        .gp-hero-subtitle {
          font-size: 24px;
          font-weight: 600;
          color: var(--gp-text);
          margin-bottom: 12px;
        }

        .gp-card {
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid var(--gp-border);
          border-radius: 12px;
          padding: 18px 20px;
          margin-bottom: 12px;
          box-shadow: none;
          line-height: 1.5;
        }

        .gp-muted {
          color: var(--gp-muted);
        }

        .gp-badge {
          display: inline-block;
          font-size: 12px;
          font-weight: 600;
          padding: 4px 8px;
          border-radius: 999px;
          background: rgba(124, 58, 237, 0.18);
          color: #c4b5fd;
          border: 1px solid rgba(124, 58, 237, 0.35);
          margin-right: 8px;
        }

        .gp-highlight-title {
          font-size: 18px;
          font-weight: 700;
          color: var(--gp-text);
          margin-right: 8px;
        }

        .gp-badge-high {
          background: rgba(239, 68, 68, 0.25);
          color: #fecaca;
          border: 1px solid rgba(239, 68, 68, 0.55);
        }

        .gp-badge-medium {
          background: rgba(245, 158, 11, 0.2);
          color: #fde68a;
          border: 1px solid rgba(245, 158, 11, 0.4);
        }

        .gp-badge-low {
          background: rgba(59, 130, 246, 0.2);
          color: #bfdbfe;
          border: 1px solid rgba(59, 130, 246, 0.4);
        }

        .gp-info {
          background: var(--gp-panel);
          border: 1px solid var(--gp-border);
          border-radius: 12px;
          padding: 14px 16px;
        }

        section[data-testid="stSidebar"] {
          background: #0c0f16;
          border-right: 1px solid var(--gp-border);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.title("GEO Pulse")
    pages = ["Audit"]
    if not is_hf_space():
        pages.append("Debug")
    page = st.sidebar.radio("Navigation", pages)

    if page == "Audit":
        render_audit_page()
    else:
        render_debug_page()


if __name__ == "__main__":
    main()
