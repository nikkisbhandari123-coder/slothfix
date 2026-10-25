"""UI components module for SlothFix."""

from components.styles import CUSTOM_CSS
from components.header import render_header
from components.input_panel import render_input_panel
from components.results_panel import render_results_panel

__all__ = [
    "CUSTOM_CSS",
    "render_header",
    "render_input_panel",
    "render_results_panel"
]
