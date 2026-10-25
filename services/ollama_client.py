"""Ollama HTTP client for model discovery and streaming inference."""

import json
import requests
from typing import Dict, List, Tuple, Optional, Iterator, Any


def get_ollama_models(base_url: str = "http://localhost:11434") -> Tuple[bool, List[Dict], str]:
    """Query Ollama /api/tags to discover locally installed models.
    
    Args:
        base_url: Ollama daemon HTTP base endpoint.
        
    Returns:
        Tuple of (is_connected, list_of_models_dict, error_message).
    """
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
    """Auto-detect the best installed Gemma model tag (preferring gemma4, then gemma3, etc.).
    
    Args:
        models: List of model metadata dictionaries returned by Ollama /api/tags.
        
    Returns:
        String tag name of the prioritized model, or None if no models installed.
    """
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
            
    # Priority 4: Fallback to first available model
    if model_names:
        return model_names[0]
        
    return None


def query_gemma_streaming(
    base_url: str,
    model: str,
    prompt: str,
    temperature: float = 0.2,
    max_tokens: int = 1500,
    timeout: int = 180
) -> Iterator[Tuple[str, Any]]:
    """Stream response from Ollama /api/chat to handle thinking models and avoid socket timeouts.
    
    Yields:
        Tuples of (kind, payload) where kind is "thinking", "content", or "done".
    """
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
