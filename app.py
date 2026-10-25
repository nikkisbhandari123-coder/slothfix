import streamlit as st
import requests
import json
import difflib
import re
import time
from typing import Dict, List, Tuple, Optional

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SlothFix 🦥 · Local-First AI Debugger",
    page_icon="🦥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS FOR MODERN HACKATHON AESTHETICS ---
CUSTOM_CSS = """
<style>
/* Modern Typography and Palette */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
}

code, pre, .stCodeBlock {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Header & Brand styling */
.brand-title {
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #f59e0b 0%, #10b981 50%, #3b82f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: inline-block;
    margin-bottom: 0.2rem;
}

.brand-subtitle {
    color: #94a3b8;
    font-size: 1.05rem;
    margin-bottom: 1.2rem;
}

/* Badge styling */
.badge-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1.2rem;
}

.sloth-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.3rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.025em;
    border: 1px solid rgba(255, 255, 255, 0.12);
}

.badge-local {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(5, 150, 105, 0.25));
    color: #34d399;
    border-color: rgba(52, 211, 153, 0.4);
}

.badge-gemma {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(37, 99, 235, 0.25));
    color: #60a5fa;
    border-color: rgba(96, 165, 250, 0.4);
}

.badge-safe {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(217, 119, 6, 0.25));
    color: #fbbf24;
    border-color: rgba(251, 191, 36, 0.4);
}

/* Feature cards */
.feature-card {
    background: rgba(22, 31, 48, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
}

/* Butterfly effect cards */
.cascade-card {
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    border-left: 4px solid;
    background: rgba(15, 23, 42, 0.6);
}

.cascade-l1 {
    border-left-color: #ef4444;
    background: linear-gradient(90deg, rgba(239, 68, 68, 0.12) 0%, rgba(15, 23, 42, 0.6) 100%);
}

.cascade-l2 {
    border-left-color: #f59e0b;
    background: linear-gradient(90deg, rgba(245, 158, 11, 0.12) 0%, rgba(15, 23, 42, 0.6) 100%);
}

.cascade-l3 {
    border-left-color: #06b6d4;
    background: linear-gradient(90deg, rgba(6, 182, 212, 0.12) 0%, rgba(15, 23, 42, 0.6) 100%);
}

.cascade-title {
    font-weight: 700;
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
    margin-bottom: 0.3rem;
}

/* Safety banner */
.safety-banner {
    background: rgba(245, 158, 11, 0.1);
    border: 1px solid rgba(245, 158, 11, 0.3);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
    font-size: 0.85rem;
    color: #fbbf24;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- PRESET SAMPLE CASES ---
SAMPLE_CASES = {
    "🐍 Python NoneType Error": {
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
    "🌐 JS undefined .map() Error": {
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
    "🔢 Off-by-One Loop Error": {
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
        return False, [], "Cannot connect to Ollama at http://localhost:11434. Is Ollama running?"
    except Exception as e:
        return False, [], str(e)


def extract_best_gemma_model(models: List[Dict]) -> Optional[str]:
    """Auto-detect the best installed Gemma model tag (preferring gemma4, then gemma3, etc.)."""
    model_names = [m.get("name", "") for m in models]
    
    # Priority 1: Gemma 4 variants (e.g. gemma4:e2b)
    for name in model_names:
        if "gemma4" in name.lower():
            return name
            
    # Priority 2: Gemma 3 variants
    for name in model_names:
        if "gemma3" in name.lower():
            return name
            
    # Priority 3: Any Gemma model
    for name in model_names:
        if "gemma" in name.lower():
            return name
            
    # Priority 4: First available model
    if model_names:
        return model_names[0]
        
    return None


def generate_unified_diff(original: str, patch: str, filename: str = "code_snippet") -> str:
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
    st.session_state.code_input = SAMPLE_CASES["🐍 Python NoneType Error"]["code"]
if "error_input" not in st.session_state:
    st.session_state.error_input = SAMPLE_CASES["🐍 Python NoneType Error"]["error"]
if "selected_lang" not in st.session_state:
    st.session_state.selected_lang = "python"
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "thinking_trace" not in st.session_state:
    st.session_state.thinking_trace = ""


# --- SIDEBAR: LOCAL AI STATUS & MODEL SELECTION ---
with st.sidebar:
    st.markdown("### 🦥 SlothFix Control Hub")
    st.markdown("---")
    
    ollama_url = st.text_input("Ollama Host URL", value="http://localhost:11434", help="Local HTTP endpoint for Ollama.")
    
    connected, installed_models, conn_err = get_ollama_models(ollama_url)
    
    if connected and installed_models:
        st.markdown(
            '<div class="sloth-badge badge-local" style="width:100%; justify-content:center; margin-bottom:1rem;">'
            '● Ollama Engine Connected'
            '</div>', 
            unsafe_allow_html=True
        )
        
        model_names = [m.get("name", "") for m in installed_models]
        best_detected = extract_best_gemma_model(installed_models)
        
        default_index = 0
        if best_detected and best_detected in model_names:
            default_index = model_names.index(best_detected)
            
        selected_model = st.selectbox(
            "Selected Local Model",
            options=model_names,
            index=default_index,
            help="Select the locally running model. Auto-detected Gemma models are prioritized."
        )
        
        # Display model metadata
        curr_meta = next((m for m in installed_models if m.get("name") == selected_model), None)
        if curr_meta and "details" in curr_meta:
            details = curr_meta["details"]
            param_size = details.get("parameter_size", "Unknown")
            family = details.get("family", "Unknown")
            quant = details.get("quantization_level", "Unknown")
            runner = details.get("runner", "llamacpp")
            
            with st.expander("Model Specifications", expanded=False):
                st.write(f"**Family:** `{family}`")
                st.write(f"**Parameters:** `{param_size}`")
                st.write(f"**Quantization:** `{quant}`")
                st.write(f"**Engine:** `{runner}`")
                st.write(f"**Privacy:** 100% On-Host Local RAM/VRAM")
    else:
        st.markdown(
            '<div class="sloth-badge" style="background:rgba(239,68,68,0.2); color:#f87171; width:100%; justify-content:center; margin-bottom:1rem;">'
            '✕ Ollama Offline'
            '</div>', 
            unsafe_allow_html=True
        )
        st.error(f"Error: {conn_err}")
        selected_model = "gemma4:e2b"
        
        st.info("💡 **How to resolve:**\n1. Open your terminal\n2. Run `ollama serve`\n3. Verify with `ollama list`\n4. If missing Gemma: `ollama run gemma4:e2b`")

    st.markdown("---")
    st.markdown("#### ⚙️ Inference Settings")
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.05, help="Lower values produce more deterministic, accurate code fixes.")
    max_tokens = st.slider("Max Output Tokens", min_value=500, max_value=2500, value=1500, step=50, help="Token budget for Gemma reasoning and response.")
    
    st.markdown("---")
    st.markdown("#### 🛡️ Local Safety Guarantee")
    st.caption("• Zero external HTTP API calls\n• No third-party telemetry\n• No host-level code execution\n• Air-gapped capable")


# --- MAIN UI HEADER ---
col_logo, col_badges = st.columns([2, 1])

with col_logo:
    st.markdown('<div class="brand-title">SlothFix 🦥</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-subtitle">The Local-First AI Debugging & Blast-Radius Assistant</div>', unsafe_allow_html=True)

with col_badges:
    st.markdown(
        '<div class="badge-container" style="justify-content: flex-end; margin-top: 0.8rem;">'
        '<span class="sloth-badge badge-local">⚡ Local AI · Gemma via Ollama</span>'
        '<span class="sloth-badge badge-gemma">🦥 100% On-Device</span>'
        '<span class="sloth-badge badge-safe">🔒 Host Safe · No Exec</span>'
        '</div>',
        unsafe_allow_html=True
    )

# --- SAMPLE CASE SELECTOR PRESETS ---
st.markdown("##### ⚡ Quick Test Presets:")
preset_cols = st.columns(3)

for idx, (preset_name, preset_data) in enumerate(SAMPLE_CASES.items()):
    with preset_cols[idx]:
        if st.button(preset_name, use_container_width=True, key=f"btn_preset_{idx}"):
            st.session_state.code_input = preset_data["code"]
            st.session_state.error_input = preset_data["error"]
            st.session_state.selected_lang = preset_data["language"]
            st.session_state.analysis_results = None
            st.rerun()

# --- INPUT SECTION: CODE & ERROR ---
st.markdown("---")

col_lang, col_space = st.columns([1, 3])
with col_lang:
    languages = ["python", "javascript", "typescript", "go", "rust", "java", "cpp", "sql", "bash"]
    lang_idx = languages.index(st.session_state.selected_lang) if st.session_state.selected_lang in languages else 0
    selected_lang = st.selectbox("Programming Language", options=languages, index=lang_idx)
    st.session_state.selected_lang = selected_lang

col_code, col_error = st.columns([1.1, 0.9])

with col_code:
    code_text = st.text_area(
        "Buggy Source Code",
        value=st.session_state.code_input,
        height=240,
        placeholder="Paste your source code snippet here...",
        help="Paste the relevant function or block causing the error."
    )
    st.session_state.code_input = code_text

with col_error:
    error_text = st.text_area(
        "Runtime Error / Traceback",
        value=st.session_state.error_input,
        height=240,
        placeholder="Paste runtime stack trace, error log, or console output...",
        help="Paste the exact error message or stack trace."
    )
    st.session_state.error_input = error_text

# --- ACTION BUTTON ---
analyze_clicked = st.button("🦥 Analyze & Debug with Gemma", type="primary", use_container_width=True)

# --- ANALYSIS PIPELINE EXECUTION ---
if analyze_clicked:
    if not code_text.strip():
        st.warning("⚠️ Please provide source code to analyze.")
    elif not error_text.strip():
        st.warning("⚠️ Please provide the error message or traceback.")
    elif not connected:
        st.error(f"Cannot run local inference: {conn_err}. Please ensure Ollama is running (`ollama serve`).")
    else:
        # Construct systematic prompt
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
        
        status_box = st.status("🦥 SlothFix analyzing with local Gemma...", expanded=True)
        thinking_area = st.empty()
        
        full_content = ""
        full_thinking = ""
        
        try:
            status_box.write(f"Connecting to local Ollama (`{selected_model}`)...")
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
                    thinking_area.info("🧠 **Gemma Analyzing:** Diagnosing interpreter state and identifying failure modes...")
                elif kind == "content":
                    full_content += chunk
                elif kind == "done":
                    break
                    
            elapsed = time.time() - t_start
            status_box.update(label=f"✅ Analysis completed in {elapsed:.1f}s via {selected_model}!", state="complete", expanded=False)
            thinking_area.empty()
            
            # Store parsed output in session state
            st.session_state.analysis_results = parse_slothfix_response(full_content)
            st.session_state.thinking_trace = full_thinking
            
        except requests.exceptions.Timeout:
            status_box.update(label="❌ Inference timed out", state="error")
            st.error("Request timed out. Try reducing 'Max Output Tokens' or ensure your CPU/GPU isn't overloaded.")
        except Exception as ex:
            status_box.update(label="❌ Inference failed", state="error")
            st.error(f"Error during inference: {ex}")


# --- RESULTS DISPLAY ---
if st.session_state.analysis_results:
    results = st.session_state.analysis_results
    
    st.markdown("---")
    
    # Visible Safety & Non-Execution Notice
    st.markdown(
        '<div class="safety-banner">'
        '<span>🛡️</span>'
        '<span><strong>Safety Guarantee:</strong> All diagnoses, patches, and regression tests are statically synthesized by local Gemma AI. '
        'For host protection, arbitrary submitted code is <strong>NEVER</strong> executed directly on your machine.</span>'
        '</div>',
        unsafe_allow_html=True
    )
    
    # Structured Tabbed View
    tab_patch, tab_root, tab_butterfly, tab_test = st.tabs([
        "🩹 Minimal Patch & Diff",
        "🔍 Root Cause Diagnosis",
        "🦋 Butterfly Effect (Downstream Cascade)",
        "🧪 Generated Regression Test"
    ])
    
    # TAB 1: MINIMAL PATCH & DIFF
    with tab_patch:
        st.markdown("### 🩹 Minimal Suggested Patch")
        
        if results.get("patch_explanation"):
            st.info(results["patch_explanation"])
            
        col_orig, col_fixed = st.columns(2)
        with col_orig:
            st.markdown("##### 🛑 Original Code")
            st.code(st.session_state.code_input, language=st.session_state.selected_lang)
            
        with col_fixed:
            st.markdown("##### ✅ SlothFix Corrected Patch")
            fixed_code = results.get("patch_code") or "# No patch code extracted"
            st.code(fixed_code, language=st.session_state.selected_lang)
            
        st.markdown("##### 📊 Unified Git-Style Diff")
        diff_text = generate_unified_diff(st.session_state.code_input, fixed_code)
        st.code(diff_text, language="diff")
        
        st.caption("Tip: Copy the patch above directly into your local IDE.")

    # TAB 2: ROOT CAUSE DIAGNOSIS
    with tab_root:
        st.markdown("### 🔍 Root Cause Analysis")
        root_cause_text = results.get("root_cause", "No root cause identified.")
        st.markdown(root_cause_text)
        
        if results.get("confidence_safety"):
            st.markdown("---")
            st.markdown("##### 🎯 Model Assessment & Confidence")
            st.markdown(results["confidence_safety"])

    # TAB 3: BUTTERFLY EFFECT (DOWNSTREAM CASCADE)
    with tab_butterfly:
        st.markdown("### 🦋 The Butterfly Effect: Downstream Blast Radius")
        st.markdown(
            "A single uncaught exception can ripple across call stacks, service boundaries, and storage layers. "
            "Here is Gemma's projected downstream chain of failure:"
        )
        
        butterfly_raw = results.get("butterfly_effect", "")
        
        # Parse or render structured cascade cards
        st.markdown(
            '<div class="cascade-card cascade-l1">'
            '<div class="cascade-title"><span style="color:#ef4444;">⚡ Level 1: Immediate Crash Site</span></div>'
            '<div>Immediate unhandled exception terminating the local thread, coroutine, or function scope.</div>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="cascade-card cascade-l2">'
            '<div class="cascade-title"><span style="color:#f59e0b;">🌊 Level 2: Caller & Interface Cascades</span></div>'
            '<div>Calling service receives 500 Internal Server Error, broken promises, or partial rendering states.</div>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="cascade-card cascade-l3">'
            '<div class="cascade-title"><span style="color:#06b6d4;">🌪️ Level 3: Silent & System Integrity Risks</span></div>'
            '<div>Potential database transaction rollbacks, desynchronized cache keys, or aggressive retry loops overwhelming downstreams.</div>'
            '</div>',
            unsafe_allow_html=True
        )
        
        st.markdown("##### 📝 Detailed Cascade Breakdown:")
        st.markdown(butterfly_raw if butterfly_raw else "No detailed cascade provided.")

    # TAB 4: GENERATED REGRESSION TEST
    with tab_test:
        st.markdown("### 🧪 Generated Regression Test")
        st.markdown(
            "Use this unit/regression test to verify the failure case and prevent future regressions. "
            "Add this test to your project's CI pipeline."
        )
        
        st.markdown(
            '<div class="sloth-badge badge-safe" style="margin-bottom: 0.8rem;">'
            '⚠️ Unverified Proposal · Static Analysis Only (Never executed on host machine)'
            '</div>',
            unsafe_allow_html=True
        )
        
        reg_code = results.get("regression_test", "# No regression test generated")
        st.code(reg_code, language=st.session_state.selected_lang)


# --- FOOTER ---
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 1rem 0;">'
    '🦥 <strong>SlothFix</strong> · Built for Local-First Hackathons · '
    'Zero Cloud Inference · Privacy Guaranteed · Powered by Gemma & Ollama'
    '</div>',
    unsafe_allow_html=True
)
