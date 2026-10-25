import streamlit as st
import requests
import json
import difflib
import re
import time
from typing import Dict, List, Tuple, Optional

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SlothFix · Developer Debugging Assistant",
    page_icon="🪲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS FOR REFINED DEVELOPER TOOL AESTHETIC ---
CUSTOM_CSS = """
<style>
/* Modern Typography and Neutral Developer-Tool Palette */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #f1f5f9;
}

code, pre, .stCodeBlock, textarea {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Base background & container spacing */
.stApp {
    background-color: #0b0f19;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* Header & Navbar styling */
.navbar-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.9rem 1.25rem;
    background: #111827;
    border: 1px solid rgba(148, 163, 184, 0.12);
    border-radius: 10px;
    margin-bottom: 1.25rem;
}

.navbar-brand {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.brand-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 34px;
    height: 34px;
    border-radius: 8px;
    background: rgba(16, 185, 129, 0.12);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.brand-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #f8fafc;
    letter-spacing: -0.02em;
    margin: 0;
    line-height: 1.2;
}

.brand-tagline {
    font-size: 0.82rem;
    color: #94a3b8;
    margin-left: 0.25rem;
    font-weight: 400;
}

.navbar-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
}

/* Compact status pills */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.25rem 0.65rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.01em;
    border: 1px solid transparent;
}

.pill-connected {
    background: rgba(16, 185, 129, 0.1);
    color: #34d399;
    border-color: rgba(16, 185, 129, 0.25);
}

.pill-offline {
    background: rgba(239, 68, 68, 0.1);
    color: #f87171;
    border-color: rgba(239, 68, 68, 0.25);
}

.pill-meta {
    background: #1e293b;
    color: #cbd5e1;
    border-color: rgba(148, 163, 184, 0.15);
}

.dot-green {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: #10b981;
}

.dot-red {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: #ef4444;
}

/* Workbench Cards */
.workbench-card {
    background: #111827;
    border: 1px solid rgba(148, 163, 184, 0.12);
    border-radius: 10px;
    padding: 1.2rem;
    margin-bottom: 1rem;
}

.card-header-label {
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #94a3b8;
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

/* Section dividers & labels */
.section-label {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #64748b;
    margin-bottom: 0.4rem;
}

/* Butterfly effect cascade cards */
.cascade-card {
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.75rem;
    border-left: 3px solid;
    background: #0f172a;
    border-top: 1px solid rgba(148, 163, 184, 0.08);
    border-right: 1px solid rgba(148, 163, 184, 0.08);
    border-bottom: 1px solid rgba(148, 163, 184, 0.08);
}

.cascade-l1 {
    border-left-color: #f87171;
    background: linear-gradient(90deg, rgba(239, 68, 68, 0.06) 0%, #0f172a 100%);
}

.cascade-l2 {
    border-left-color: #fbbf24;
    background: linear-gradient(90deg, rgba(245, 158, 11, 0.06) 0%, #0f172a 100%);
}

.cascade-l3 {
    border-left-color: #38bdf8;
    background: linear-gradient(90deg, rgba(56, 189, 248, 0.06) 0%, #0f172a 100%);
}

.cascade-header {
    font-weight: 600;
    font-size: 0.88rem;
    margin-bottom: 0.25rem;
}

.cascade-desc {
    font-size: 0.82rem;
    color: #94a3b8;
    line-height: 1.4;
}

/* Safety guarantee banner */
.safety-banner {
    background: rgba(16, 185, 129, 0.06);
    border: 1px solid rgba(16, 185, 129, 0.2);
    border-radius: 8px;
    padding: 0.65rem 0.9rem;
    margin-bottom: 1rem;
    font-size: 0.82rem;
    color: #6ee7b7;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.unverified-banner {
    background: rgba(245, 158, 11, 0.08);
    border: 1px solid rgba(245, 158, 11, 0.25);
    border-radius: 8px;
    padding: 0.6rem 0.85rem;
    margin-bottom: 0.75rem;
    font-size: 0.8rem;
    color: #fcd34d;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

/* Empty state styling */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 2.8rem 1.5rem;
    background: #111827;
    border: 1px dashed rgba(148, 163, 184, 0.2);
    border-radius: 10px;
    color: #94a3b8;
}

.empty-state-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #e2e8f0;
    margin-top: 0.75rem;
    margin-bottom: 0.35rem;
}

.empty-state-text {
    font-size: 0.85rem;
    color: #64748b;
    max-width: 420px;
    line-height: 1.5;
    margin-bottom: 1.25rem;
}

.feature-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
    width: 100%;
    max-width: 480px;
    text-align: left;
}

.feature-pill {
    background: #1e293b;
    border: 1px solid rgba(148, 163, 184, 0.1);
    border-radius: 6px;
    padding: 0.55rem 0.75rem;
    font-size: 0.78rem;
    color: #cbd5e1;
}

.feature-pill strong {
    color: #f1f5f9;
    display: block;
    margin-bottom: 0.15rem;
}

/* Native buttons styling refinements */
button[kind="primary"] {
    background-color: #10b981 !important;
    border-color: #10b981 !important;
    color: #042f2e !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
}

button[kind="primary"]:hover {
    background-color: #059669 !important;
    border-color: #059669 !important;
}

/* Sidebar polish */
[data-testid="stSidebar"] {
    background-color: #0d1322;
    border-right: 1px solid rgba(148, 163, 184, 0.1);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- SUPPORTED LANGUAGES & FILE EXTENSIONS ---
LANG_EXTENSIONS = {
    "python": "py",
    "javascript": "js",
    "typescript": "ts",
    "go": "go",
    "rust": "rs",
    "java": "java",
    "cpp": "cpp",
    "sql": "sql",
    "bash": "sh"
}

# --- PRESET SAMPLE CASES ---
SAMPLE_CASES = {
    "Python NoneType": {
        "language": "python",
        "code": """def fetch_and_format_user(user_id):
    # Simulates querying a database record
    user = get_database_user(user_id)  # Returns None if not found
    
    # Bug: Directly calling .get() or indexing on None
    full_name = user.get("first_name", "") + " " + user.get("last_name", "")
    return full_name.strip()
""",
        "error": """AttributeError: 'NoneType' object has no attribute 'get'
Traceback (most recent call last):
  File "services/user_service.py", line 14, in fetch_and_format_user
    full_name = user.get("first_name", "") + " " + user.get("last_name", "")
"""
    },
    "JavaScript .map()": {
        "language": "javascript",
        "code": """function renderUserProfile(apiResponse) {
    // When apiResponse.data is missing or teamMembers is undefined
    const userList = apiResponse.data.teamMembers;
    
    // Bug: Calling .map() on undefined
    const badgeElements = userList.map(member => {
        return `<span class="badge">${member.role}: ${member.name}</span>`;
    });
    
    return badgeElements.join('\\n');
}
""",
        "error": """TypeError: Cannot read properties of undefined (reading 'map')
    at renderUserProfile (components/team.js:3:25)
    at renderDashboard (pages/dashboard.js:18:12)
"""
    },
    "Off-by-One Loop": {
        "language": "python",
        "code": """def get_last_n_transactions(history, count):
    latest = []
    # Bug: Off-by-one boundary: len(history) + 1 causes IndexError
    start_index = len(history) - count
    end_index = len(history) + 1
    
    for i in range(start_index, end_index):
        latest.append(history[i])
    return latest
""",
        "error": """IndexError: list index out of range
Traceback (most recent call last):
  File "finance/analytics.py", line 8, in get_last_n_transactions
    latest.append(history[i])
"""
    }
}

# --- OLLAMA CLIENT UTILITIES ---
def get_ollama_models(base_url: str = "http://localhost:11434") -> Tuple[bool, List[Dict], str]:
    """Query Ollama /api/tags to discover locally installed models."""
    try:
        response = requests.get(f"{base_url.rstrip('/')}/api/tags", timeout=5)
        if response.status_code == 200:
            models_data = response.json().get("models", [])
            return True, models_data, ""
        return False, [], f"Ollama returned HTTP status {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, [], "Cannot connect to Ollama at http://localhost:11434. Is the local daemon running?"
    except Exception as e:
        return False, [], str(e)


def extract_best_gemma_model(models: List[Dict]) -> Optional[str]:
    """Auto-detect the best installed Gemma model tag (preferring gemma4, then gemma3, etc.)."""
    model_names = [m.get("name", "") for m in models]
    
    for name in model_names:
        if "gemma4" in name.lower():
            return name
            
    for name in model_names:
        if "gemma3" in name.lower():
            return name
            
    for name in model_names:
        if "gemma" in name.lower():
            return name
            
    if model_names:
        return model_names[0]
        
    return None


def generate_unified_diff(original: str, patch: str, filename: str = "snippet") -> str:
    """Produce a standard git-style unified diff between original and patched code."""
    orig_lines = original.splitlines(keepends=True)
    patch_lines = patch.splitlines(keepends=True)
    diff = list(difflib.unified_diff(
        orig_lines, patch_lines,
        fromfile=f"a/{filename} (original)",
        tofile=f"b/{filename} (SlothFix patch)",
        lineterm=""
    ))
    return "".join(diff) if diff else "No textual differences detected."


def parse_slothfix_response(text: str) -> Dict[str, str]:
    """Parse the structured sections from Gemma's response."""
    sections = {
        "root_cause": "",
        "patch_code": "",
        "patch_explanation": "",
        "butterfly_effect": "",
        "regression_test": "",
        "confidence_safety": ""
    }
    
    patterns = [
        ("root_cause", r"(?:###?\s*(?:1\.?\s*)?ROOT\s*CAUSE[^\n]*\n)(.*?)(?=(?:###?\s*(?:2\.?\s*)?MINIMAL\s*PATCH|###?\s*\d|\Z))"),
        ("patch_section", r"(?:###?\s*(?:2\.?\s*)?MINIMAL\s*PATCH[^\n]*\n)(.*?)(?=(?:###?\s*(?:3\.?\s*)?BUTTERFLY|###?\s*\d|\Z))"),
        ("butterfly_effect", r"(?:###?\s*(?:3\.?\s*)?BUTTERFLY\s*(?:EFFECT)?[^\n]*\n)(.*?)(?=(?:###?\s*(?:4\.?\s*)?REGRESSION\s*TEST|###?\s*\d|\Z))"),
        ("regression_test", r"(?:###?\s*(?:4\.?\s*)?REGRESSION\s*TEST[^\n]*\n)(.*?)(?=(?:###?\s*(?:5\.?\s*)?CONFIDENCE|###?\s*\d|\Z))"),
        ("confidence_safety", r"(?:###?\s*(?:5\.?\s*)?CONFIDENCE[^\n]*\n)(.*?)(?=\Z)")
    ]
    
    for key, pattern in patterns:
        m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            if key == "patch_section":
                code_match = re.search(r"```(?:\w+)?\n(.*?)```", val, re.DOTALL)
                if code_match:
                    sections["patch_code"] = code_match.group(1).strip()
                    sections["patch_explanation"] = re.sub(r"```(?:\w+)?\n.*?```", "", val, flags=re.DOTALL).strip()
                else:
                    sections["patch_code"] = val
            elif key == "regression_test":
                code_match = re.search(r"```(?:\w+)?\n(.*?)```", val, re.DOTALL)
                if code_match:
                    sections["regression_test"] = code_match.group(1).strip()
                else:
                    sections["regression_test"] = val
            else:
                sections[key] = val
                
    # Fallback if headings were slightly different
    if not sections["root_cause"] and not sections["patch_code"]:
        sections["root_cause"] = text
        
    return sections


def query_gemma_streaming(base_url: str, model: str, prompt: str, temperature: float = 0.2, max_tokens: int = 1500, timeout: int = 180):
    """Stream response from Ollama /api/chat to handle thinking models and avoid socket timeouts."""
    endpoint = f"{base_url.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }
    
    response = requests.post(endpoint, json=payload, stream=True, timeout=timeout)
    if response.status_code != 200:
        raise RuntimeError(f"Ollama error ({response.status_code}): {response.text}")
        
    thinking_chunks = []
    content_chunks = []
    
    for line in response.iter_lines():
        if not line:
            continue
        try:
            chunk = json.loads(line.decode("utf-8"))
        except Exception:
            continue
            
        msg = chunk.get("message", {})
        t = msg.get("thinking", "")
        c = msg.get("content", "")
        
        if t:
            thinking_chunks.append(t)
            yield ("thinking", t)
        if c:
            content_chunks.append(c)
            yield ("content", c)
            
        if chunk.get("done", False):
            break
            
    full_thinking = "".join(thinking_chunks)
    full_content = "".join(content_chunks)
    yield ("done", {"thinking": full_thinking, "content": full_content})


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
status_badge_html = (
    f'<span class="status-pill pill-connected"><span class="dot-green"></span> Connected &middot; {selected_model}</span>'
    if connected else
    '<span class="status-pill pill-offline"><span class="dot-red"></span> Ollama Offline</span>'
)

navbar_html = f"""
<div class="navbar-container">
    <div class="navbar-brand">
        <div class="brand-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect width="8" height="14" x="8" y="6" rx="4"></rect>
                <path d="m19 7-3 2"></path>
                <path d="m5 7 3 2"></path>
                <path d="m19 19-3-2"></path>
                <path d="m5 19 3-2"></path>
                <path d="M20 13h-4"></path>
                <path d="M4 13h4"></path>
                <path d="m10 4 1 2"></path>
                <path d="m14 4-1 2"></path>
            </svg>
        </div>
        <div>
            <div class="brand-title">SlothFix</div>
            <div class="brand-tagline">Debug smarter. Ship safer.</div>
        </div>
    </div>
    <div class="navbar-status">
        {status_badge_html}
        <span class="status-pill pill-meta">100% On-Device</span>
        <span class="status-pill pill-meta">Host Safe</span>
    </div>
</div>
"""
st.markdown(navbar_html, unsafe_allow_html=True)


# --- MAIN WORKSPACE: TWO-COLUMN WORKBENCH ON WIDE SCREENS ---
col_input, col_output = st.columns([5, 6], gap="large")

# === LEFT COLUMN: INPUT WORKSPACE ===
with col_input:
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
    
    # Language selector & Code input
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

    code_text = st.text_area(
        "Source Code",
        value=st.session_state.code_input,
        height=220,
        placeholder="Paste your source code block here...",
        help="Relevant function or module containing the bug."
    )
    st.session_state.code_input = code_text

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

    # --- INFERENCE EXECUTION PIPELINE ---
    if analyze_clicked:
        if not code_text.strip():
            st.warning("Please provide source code to analyze.")
        elif not error_text.strip():
            st.warning("Please provide the runtime error message or stack trace.")
        elif not connected:
            st.error(f"Cannot perform local inference: {conn_err}. Verify that Ollama is running (`ollama serve`).")
        else:
            prompt = f"""You are SlothFix, an expert debugging AI powered by Gemma.
Analyze the following code and error thoroughly:

Programming Language: {selected_lang}

Buggy Code:
```{selected_lang}
{code_text}
```

Error Message / Traceback:
```
{error_text}
```

Format your response strictly using these markdown sections:

### 1. ROOT CAUSE
[Explain exactly why this error occurred at runtime, citing the specific line and variable conditions.]

### 2. MINIMAL PATCH
```{selected_lang}
[The corrected code snippet fixing the bug with minimal, clean changes]
```
[Brief 1-2 sentence explanation of why this patch resolves the bug cleanly]

### 3. BUTTERFLY EFFECT & DOWNSTREAM IMPACT
- **Immediate Failure**: [What immediately crashes at this call site]
- **Caller Cascades**: [How parent functions, API endpoints, or user requests fail]
- **Silent / System Risks**: [Potential database inconsistency, uncommitted state, or cascading retry storms]

### 4. REGRESSION TEST
```{selected_lang}
[Complete standalone regression test code (e.g. pytest for Python, Jest for JavaScript, etc.) that reproduces the failure on buggy code and verifies the fix. Ready to copy.]
```

### 5. CONFIDENCE & SAFETY NOTICE
- Confidence Score: [e.g. 98%]
- Verification Status: Model-generated proposal (unexecuted on host machine)
- Rationale: [Brief justification]
"""
            
            status_box = st.status("Diagnosing runtime mechanics with local Gemma...", expanded=True)
            thinking_placeholder = st.empty()
            
            full_content = ""
            full_thinking = ""
            
            try:
                status_box.write(f"Connecting to `{selected_model}` on localhost:11434...")
                t_start = time.time()
                
                for kind, chunk in query_gemma_streaming(
                    base_url=ollama_url,
                    model=selected_model,
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=180
                ):
                    if kind == "thinking":
                        full_thinking += chunk
                        thinking_placeholder.info("🧠 **Gemma Analyzing:** Diagnosing interpreter state and identifying failure modes...")
                    elif kind == "content":
                        full_content += chunk
                    elif kind == "done":
                        break
                        
                elapsed = time.time() - t_start
                status_box.update(
                    label=f"Analysis completed in {elapsed:.1f}s via {selected_model}",
                    state="complete",
                    expanded=False
                )
                thinking_placeholder.empty()
                
                # Parse structured diagnosis
                st.session_state.analysis_results = parse_slothfix_response(full_content)
                st.session_state.thinking_trace = full_thinking
                st.rerun()
                
            except requests.exceptions.Timeout:
                status_box.update(label="Inference request timed out", state="error")
                st.error("Model generation timed out. Try reducing 'Max Output Tokens' or verify GPU/CPU load.")
            except Exception as ex:
                status_box.update(label="Inference failed", state="error")
                st.error(f"Inference error: {ex}")


# === RIGHT COLUMN: RESULTS WORKSPACE ===
with col_output:
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
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
                st.code(st.session_state.code_input, language=st.session_state.selected_lang)
                
            with col_fixed:
                st.markdown('<div class="section-label">CORRECTED PATCH</div>', unsafe_allow_html=True)
                fixed_code = results.get("patch_code") or "# No patch code extracted"
                st.code(fixed_code, language=st.session_state.selected_lang)
                
            st.markdown('<div class="section-label">UNIFIED GIT DIFF</div>', unsafe_allow_html=True)
            diff_text = generate_unified_diff(st.session_state.code_input, fixed_code)
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
            st.code(reg_code, language=st.session_state.selected_lang)
            
            ext = LANG_EXTENSIONS.get(st.session_state.selected_lang, "txt")
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


# --- FOOTER ---
st.markdown("---")
footer_html = """
<div style="display: flex; justify-content: space-between; align-items: center; color: #64748b; font-size: 0.8rem; padding: 0.5rem 0;">
    <div><strong>SlothFix</strong> &middot; Debug smarter. Ship safer.</div>
    <div>100% Local Inference &middot; Google Gemma via Ollama &middot; Zero Cloud Telemetry</div>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
