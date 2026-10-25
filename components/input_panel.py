"""Input panel component for presets, code editor, and error logs."""

import streamlit as st
from typing import Tuple
from utils.prompts import SAMPLE_CASES, LANG_EXTENSIONS


def render_input_panel() -> Tuple[bool, str, str, str]:
    """Render the left-column input workbench for SlothFix.
    
    Returns:
        Tuple of (analyze_clicked, code_text, error_text, selected_lang).
    """
    st.markdown('<div class="section-label">SAMPLE BUG PRESETS</div>', unsafe_allow_html=True)
    preset_cols = st.columns(3)
    
    preset_keys = list(SAMPLE_CASES.keys())
    for idx, preset_name in enumerate(preset_keys):
        with preset_cols[idx]:
            if st.button(preset_name, use_container_width=True, key=f"btn_preset_{idx}"):
                st.session_state.code_input = SAMPLE_CASES[preset_name]["code"]
                st.session_state.error_input = SAMPLE_CASES[preset_name]["error"]
                st.session_state.selected_lang = SAMPLE_CASES[preset_name]["language"]
                st.session_state.analysis_results = None
                st.rerun()

    st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)
    
    # Language selector
    languages = list(LANG_EXTENSIONS.keys())
    current_lang = st.session_state.selected_lang
    lang_idx = languages.index(current_lang) if current_lang in languages else 0
    selected_lang = st.selectbox(
        "Programming Language",
        options=languages,
        index=lang_idx,
        help="Select language syntax for highlighting and test generation."
    )
    st.session_state.selected_lang = selected_lang

    # Source code text area
    code_text = st.text_area(
        "Source Code",
        value=st.session_state.code_input,
        height=220,
        placeholder="Paste your source code block here...",
        help="Relevant function or module containing the bug."
    )
    st.session_state.code_input = code_text

    # Runtime error text area
    error_text = st.text_area(
        "Runtime Error / Stack Trace",
        value=st.session_state.error_input,
        height=160,
        placeholder="Paste runtime stack trace, error log, or console output...",
        help="Exact exception message or traceback from the terminal."
    )
    st.session_state.error_input = error_text

    st.markdown('<div style="height: 0.35rem;"></div>', unsafe_allow_html=True)
    analyze_clicked = st.button("Analyze Bug", type="primary", use_container_width=True)

    return analyze_clicked, code_text, error_text, selected_lang
