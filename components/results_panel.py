"""Results panel component rendering diagnostic tabs or empty workbench."""

import streamlit as st
from typing import Dict, Optional
from utils.prompts import LANG_EXTENSIONS
from utils.response_parser import generate_unified_diff


def render_results_panel(
    results: Optional[Dict[str, str]],
    selected_lang: str,
    code_input: str
) -> None:
    """Render the right-column results workspace for SlothFix.
    
    Args:
        results: Dictionary containing parsed diagnostic sections, or None.
        selected_lang: Currently active programming language.
        code_input: Original source code snippet for diff generation.
    """
    if results:
        # Safety & Non-execution notice
        st.markdown(
            '<div class="safety-banner">'
            '<span>🛡️</span>'
            '<span><strong>Host Safe:</strong> All diagnoses, patches, and tests are statically synthesized by local Gemma AI and <strong>never executed</strong> on your machine.</span>'
            '</div>',
            unsafe_allow_html=True
        )
        
        # 4 Clean Developer Tabs
        tab_patch, tab_root, tab_butterfly, tab_test = st.tabs([
            "Minimal Patch & Diff",
            "Root Cause Diagnosis",
            "Butterfly Effect",
            "Regression Test"
        ])
        
        # TAB 1: MINIMAL PATCH & UNIFIED DIFF
        with tab_patch:
            if results.get("patch_explanation"):
                st.info(results["patch_explanation"])
                
            col_orig, col_fixed = st.columns(2)
            with col_orig:
                st.markdown('<div class="section-label">ORIGINAL CODE</div>', unsafe_allow_html=True)
                st.code(code_input, language=selected_lang)
                
            with col_fixed:
                st.markdown('<div class="section-label">CORRECTED PATCH</div>', unsafe_allow_html=True)
                fixed_code = results.get("patch_code") or "# No patch code extracted"
                st.code(fixed_code, language=selected_lang)
                
            st.markdown('<div class="section-label">UNIFIED GIT DIFF</div>', unsafe_allow_html=True)
            diff_text = generate_unified_diff(code_input, fixed_code)
            st.code(diff_text, language="diff")
            
            # Action button: Download patch file
            st.download_button(
                label="📥 Download Patch (.diff)",
                data=diff_text,
                file_name="slothfix.diff",
                mime="text/x-diff",
                use_container_width=True
            )

        # TAB 2: ROOT CAUSE DIAGNOSIS
        with tab_root:
            st.markdown('<div class="section-label">INTERPRETER & RUNTIME MECHANICS</div>', unsafe_allow_html=True)
            root_cause_text = results.get("root_cause", "No root cause identified.")
            st.markdown(root_cause_text)
            
            if results.get("confidence_safety"):
                st.markdown("---")
                st.markdown('<div class="section-label">MODEL ASSESSMENT & CONFIDENCE</div>', unsafe_allow_html=True)
                st.markdown(results["confidence_safety"])

        # TAB 3: BUTTERFLY EFFECT (DOWNSTREAM CASCADE)
        with tab_butterfly:
            st.markdown(
                '<div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 0.85rem;">'
                'Projected cascading blast radius across function scopes, service boundaries, and storage layers:'
                '</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(
                '<div class="cascade-card cascade-l1">'
                '<div class="cascade-header" style="color: #f87171;">Level 1 &middot; Immediate Crash Site</div>'
                '<div class="cascade-desc">Unhandled exception aborts the local thread, coroutine, or function execution context.</div>'
                '</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<div class="cascade-card cascade-l2">'
                '<div class="cascade-header" style="color: #fbbf24;">Level 2 &middot; Caller & Interface Cascades</div>'
                '<div class="cascade-desc">Calling services receive HTTP 500 status codes, rejected promises, or broken render states.</div>'
                '</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<div class="cascade-card cascade-l3">'
                '<div class="cascade-header" style="color: #38bdf8;">Level 3 &middot; Silent System Integrity Risks</div>'
                '<div class="cascade-desc">Partial transaction rollbacks, desynchronized caches, or cascading client retry storms.</div>'
                '</div>',
                unsafe_allow_html=True
            )
            
            butterfly_raw = results.get("butterfly_effect", "")
            if butterfly_raw:
                st.markdown("---")
                st.markdown('<div class="section-label">DETAILED IMPACT BREAKDOWN</div>', unsafe_allow_html=True)
                st.markdown(butterfly_raw)

        # TAB 4: GENERATED REGRESSION TEST
        with tab_test:
            st.markdown(
                '<div class="unverified-banner">'
                '<span>⚠️</span>'
                '<span><strong>Unexecuted Suggestion:</strong> This test case is a statically synthesized proposal. It has <strong>NOT</strong> been executed or verified on your host machine.</span>'
                '</div>',
                unsafe_allow_html=True
            )
            
            reg_code = results.get("regression_test", "# No regression test generated")
            st.code(reg_code, language=selected_lang)
            
            ext = LANG_EXTENSIONS.get(selected_lang, "txt")
            st.download_button(
                label=f"📥 Download Regression Test (test_bug.{ext})",
                data=reg_code,
                file_name=f"test_bug.{ext}",
                mime="text/plain",
                use_container_width=True
            )

    else:
        # === EMPTY WORKBENCH INITIAL STATE ===
        empty_html = """
        <div class="empty-state">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <div class="empty-state-title">SlothFix Diagnostic Engine</div>
            <div class="empty-state-text">
                Select a sample bug preset on the left or paste your code snippet and runtime traceback, then click <strong>Analyze Bug</strong> to run on-device inference.
            </div>
            <div class="feature-grid">
                <div class="feature-pill">
                    <strong>Root Cause Diagnosis</strong>
                    Pinpoints exact interpreter mechanics
                </div>
                <div class="feature-pill">
                    <strong>Minimal Patch & Diff</strong>
                    Clean surgical fix with unified git diff
                </div>
                <div class="feature-pill">
                    <strong>The Butterfly Effect</strong>
                    3-level downstream blast radius projection
                </div>
                <div class="feature-pill">
                    <strong>Regression Test</strong>
                    Pre-synthesized test case for CI pipelines
                </div>
            </div>
        </div>
        """
        st.markdown(empty_html, unsafe_allow_html=True)
