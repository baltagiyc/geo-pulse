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
