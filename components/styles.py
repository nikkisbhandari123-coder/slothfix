"""Custom CSS for SlothFix developer-tool aesthetic."""

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
