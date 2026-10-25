"""Debugging service orchestrator for SlothFix."""

from typing import Dict, Iterator, Tuple, Any, Optional, Callable
from utils.prompts import build_debug_prompt
from utils.response_parser import parse_slothfix_response
from services.ollama_client import query_gemma_streaming


def stream_debug_analysis(
    ollama_url: str,
    model: str,
    language: str,
    code: str,
    error: str,
    temperature: float = 0.2,
    max_tokens: int = 1500,
    timeout: int = 180
) -> Iterator[Tuple[str, Any]]:
    """Stream inference from Ollama for a debugging request.
    
    Yields:
        ("thinking", chunk_text)
        ("content", chunk_text)
        ("done", {"content": str, "thinking": str, "parsed": Dict[str, str]})
    """
    prompt = build_debug_prompt(language=language, code=code, error=error)
    
    full_thinking = ""
    full_content = ""
    
    for kind, payload in query_gemma_streaming(
        base_url=ollama_url,
        model=model,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout
    ):
        if kind == "thinking":
            full_thinking += payload
            yield ("thinking", payload)
        elif kind == "content":
            full_content += payload
            yield ("content", payload)
        elif kind == "done":
            parsed = parse_slothfix_response(full_content)
            yield ("done", {
                "content": full_content,
                "thinking": full_thinking,
                "parsed": parsed
            })


def run_debug_analysis(
    ollama_url: str,
    model: str,
    language: str,
    code: str,
    error: str,
    temperature: float = 0.2,
    max_tokens: int = 1500,
    timeout: int = 180,
    on_thinking: Optional[Callable[[str], None]] = None,
    on_content: Optional[Callable[[str], None]] = None
) -> Dict[str, str]:
    """Execute complete debugging analysis synchronously and return parsed diagnostic dictionary.
    
    Args:
        ollama_url: Ollama base endpoint.
        model: Selected model tag.
        language: Programming language.
        code: Source code text.
        error: Runtime traceback or error log.
        temperature: Inference temperature.
        max_tokens: Maximum tokens budget.
        timeout: Socket timeout in seconds.
        on_thinking: Optional callback invoked with cumulative thinking text.
        on_content: Optional callback invoked with each content chunk.
        
    Returns:
        Structured dictionary with root_cause, patch_code, patch_explanation,
        butterfly_effect, regression_test, and confidence_safety.
    """
    cumulative_thinking = ""
    last_parsed: Dict[str, str] = {}
    
    for kind, payload in stream_debug_analysis(
        ollama_url=ollama_url,
        model=model,
        language=language,
        code=code,
        error=error,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout
    ):
        if kind == "thinking":
            cumulative_thinking += payload
            if on_thinking:
                on_thinking(cumulative_thinking)
        elif kind == "content":
            if on_content:
                on_content(payload)
        elif kind == "done":
            last_parsed = payload.get("parsed", {})
            
    return last_parsed
