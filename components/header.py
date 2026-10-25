"""Header and top navbar component for SlothFix."""

import streamlit as st


def render_header(connected: bool, selected_model: str) -> None:
    """Render the branded SlothFix top navbar with dynamic status pills.
    
    Args:
        connected: Boolean indicating if Ollama local daemon is reachable.
        selected_model: Tag name of the active local model (e.g. 'gemma4:e2b').
    """
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
