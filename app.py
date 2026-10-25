"""SlothFix · Developer Debugging Assistant.

Application entry point and high-level UI orchestration.
"""

import time
import requests
import streamlit as st

from components import (
    CUSTOM_CSS,
    render_header,
    render_input_panel,
    render_results_panel
)
from services import (
    get_ollama_models,
    extract_best_gemma_model,
    stream_debug_analysis
)
from utils import SAMPLE_CASES

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SlothFix · Developer Debugging Assistant",
    page_icon="🪲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- INJECT DEVELOPER-TOOL CSS ---
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "code_input" not in st.session_state:
    st.session_state.code_input = SAMPLE_CASES["Python NoneType"]["code"]
if "error_input" not in st.session_state:
    st.session_state.error_input = SAMPLE_CASES["Python NoneType"]["error"]
if "selected_lang" not in st.session_state:
    st.session_state.selected_lang = "python"
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "thinking_trace" not in st.session_state:
    st.session_state.thinking_trace = ""


# --- SIDEBAR: OLLAMA STATUS & ENGINE CONFIGURATION ---
with st.sidebar:
    st.markdown('<div class="card-header-label">LOCAL ENGINE CONFIGURATION</div>', unsafe_allow_html=True)
    
    ollama_url = st.text_input(
        "Ollama Endpoint",
        value="http://localhost:11434",
        help="Local HTTP API address for the Ollama daemon."
    )
    
    connected, installed_models, conn_err = get_ollama_models(ollama_url)
    
    if connected and installed_models:
        model_names = [m.get("name", "") for m in installed_models]
        best_detected = extract_best_gemma_model(installed_models)
        
        default_index = 0
        if best_detected and best_detected in model_names:
            default_index = model_names.index(best_detected)
            
        selected_model = st.selectbox(
            "Selected Local Model",
            options=model_names,
            index=default_index,
            help="Locally installed models discovered via /api/tags. Gemma is prioritized."
        )
        
        curr_meta = next((m for m in installed_models if m.get("name") == selected_model), None)
        if curr_meta and "details" in curr_meta:
            details = curr_meta["details"]
            param_size = details.get("parameter_size", "Unknown")
            quant = details.get("quantization_level", "Unknown")
            runner = details.get("runner", "llamacpp")
            
            st.markdown(
                f'<div class="status-pill pill-connected" style="width: 100%; justify-content: center; margin-top: 0.25rem; margin-bottom: 0.75rem;">'
                f'<span class="dot-green"></span> Engine Connected &middot; {selected_model}'
                f'</div>',
                unsafe_allow_html=True
            )
            
            with st.expander("Model Specifications", expanded=False):
                st.caption(f"**Parameters:** {param_size}")
                st.caption(f"**Quantization:** {quant}")
                st.caption(f"**Runner:** {runner}")
                st.caption("**Host RAM/VRAM:** 100% On-Device")
    else:
        st.markdown(
            '<div class="status-pill pill-offline" style="width: 100%; justify-content: center; margin-bottom: 0.75rem;">'
            '<span class="dot-red"></span> Ollama Offline'
            '</div>',
            unsafe_allow_html=True
        )
        st.error(f"Error: {conn_err}")
        selected_model = "gemma4:e2b"
        st.caption("To start Ollama, run `ollama serve` in your terminal.")

    st.markdown("---")
    st.markdown('<div class="card-header-label">INFERENCE PARAMETERS</div>', unsafe_allow_html=True)
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.05,
        help="Lower values yield deterministic and precise code fixes."
    )
    max_tokens = st.slider(
        "Max Output Tokens",
        min_value=500,
        max_value=2500,
        value=1500,
        step=50,
        help="Token budget for Gemma reasoning and response generation."
    )
    
    st.markdown("---")
    st.markdown('<div class="card-header-label">SAFETY & PRIVACY GUARANTEE</div>', unsafe_allow_html=True)
    st.caption("• 100% on-device local inference\n• Zero third-party telemetry or cloud APIs\n• Submitted code is never executed on host\n• Air-gap capable once weights are stored")


# --- BRANDED TOP NAVBAR ---
render_header(connected=connected, selected_model=selected_model)


# --- MAIN WORKSPACE: TWO-COLUMN WORKBENCH ---
col_input, col_output = st.columns([5, 6], gap="large")

with col_input:
    analyze_clicked, code_text, error_text, selected_lang = render_input_panel()

    if analyze_clicked:
        if not code_text.strip():
            st.warning("Please provide source code to analyze.")
        elif not error_text.strip():
            st.warning("Please provide the runtime error message or stack trace.")
        elif not connected:
            st.error(f"Cannot perform local inference: {conn_err}. Verify that Ollama is running (`ollama serve`).")
        else:
            status_box = st.status("Diagnosing runtime mechanics with local Gemma...", expanded=True)
            thinking_placeholder = st.empty()
            
            try:
                status_box.write(f"Connecting to `{selected_model}` on localhost:11434...")
                t_start = time.time()
                
                parsed_result = None
                cumulative_thinking = ""
                
                for kind, payload in stream_debug_analysis(
                    ollama_url=ollama_url,
                    model=selected_model,
                    language=selected_lang,
                    code=code_text,
                    error=error_text,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=180
                ):
                    if kind == "thinking":
                        cumulative_thinking += payload
                        thinking_placeholder.info("🧠 **Gemma Analyzing:** Diagnosing interpreter state and identifying failure modes...")
                    elif kind == "done":
                        parsed_result = payload.get("parsed")
                        
                elapsed = time.time() - t_start
                status_box.update(
                    label=f"Analysis completed in {elapsed:.1f}s via {selected_model}",
                    state="complete",
                    expanded=False
                )
                thinking_placeholder.empty()
                
                st.session_state.analysis_results = parsed_result
                st.session_state.thinking_trace = cumulative_thinking
                st.rerun()
                
            except requests.exceptions.Timeout:
                status_box.update(label="Inference request timed out", state="error")
                st.error("Model generation timed out. Try reducing 'Max Output Tokens' or verify GPU/CPU load.")
            except Exception as ex:
                status_box.update(label="Inference failed", state="error")
                st.error(f"Inference error: {ex}")

with col_output:
    render_results_panel(
        results=st.session_state.analysis_results,
        selected_lang=st.session_state.selected_lang,
        code_input=st.session_state.code_input
    )


# --- FOOTER ---
st.markdown("---")
footer_html = """
<div style="display: flex; justify-content: space-between; align-items: center; color: #64748b; font-size: 0.8rem; padding: 0.5rem 0;">
    <div><strong>SlothFix</strong> &middot; Debug smarter. Ship safer.</div>
    <div>100% Local Inference &middot; Google Gemma via Ollama &middot; Zero Cloud Telemetry</div>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
