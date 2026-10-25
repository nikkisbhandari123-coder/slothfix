"""Unit tests for debugging service, prompt construction, and Ollama integration with mocks."""

import unittest
from unittest.mock import patch, MagicMock
from utils.prompts import build_debug_prompt, SAMPLE_CASES
from services.ollama_client import extract_best_gemma_model, get_ollama_models
from services.debugger import run_debug_analysis


class TestPrompts(unittest.TestCase):
    """Test suite for prompt synthesis."""

    def test_build_debug_prompt(self):
        prompt = build_debug_prompt(
            language="python",
            code="x = None\nx.get()",
            error="AttributeError"
        )
        self.assertIn("Programming Language: python", prompt)
        self.assertIn("x = None\nx.get()", prompt)
        self.assertIn("AttributeError", prompt)
        self.assertIn("### 1. ROOT CAUSE", prompt)
        self.assertIn("### 2. MINIMAL PATCH", prompt)
        self.assertIn("### 3. BUTTERFLY EFFECT", prompt)
        self.assertIn("### 4. REGRESSION TEST", prompt)

    def test_sample_cases_present(self):
        self.assertIn("Python NoneType", SAMPLE_CASES)
        self.assertIn("JavaScript .map()", SAMPLE_CASES)
        self.assertIn("Off-by-One Loop", SAMPLE_CASES)


class TestOllamaClient(unittest.TestCase):
    """Test suite for Ollama client utilities."""

    def test_extract_best_gemma_model_priority(self):
        models = [
            {"name": "llama3:8b"},
            {"name": "gemma3:4b"},
            {"name": "gemma4:e2b"}
        ]
        best = extract_best_gemma_model(models)
        self.assertEqual(best, "gemma4:e2b")

    def test_extract_best_gemma3_when_no_gemma4(self):
        models = [
            {"name": "mistral:7b"},
            {"name": "gemma3:4b"}
        ]
        best = extract_best_gemma_model(models)
        self.assertEqual(best, "gemma3:4b")

    def test_extract_best_fallback(self):
        models = [{"name": "qwen3.5:4b"}]
        best = extract_best_gemma_model(models)
        self.assertEqual(best, "qwen3.5:4b")

    def test_extract_best_empty(self):
        best = extract_best_gemma_model([])
        self.assertIsNone(best)

    @patch("requests.get")
    def test_get_ollama_models_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": [{"name": "gemma4:e2b"}]}
        mock_get.return_value = mock_response

        ok, models, err = get_ollama_models("http://localhost:11434")
        self.assertTrue(ok)
        self.assertEqual(len(models), 1)
        self.assertEqual(models[0]["name"], "gemma4:e2b")
        self.assertEqual(err, "")


class TestDebuggerOrchestration(unittest.TestCase):
    """Test suite for debugger service orchestration with mocked streaming."""

    @patch("services.debugger.query_gemma_streaming")
    def test_run_debug_analysis(self, mock_stream):
        mock_stream.return_value = iter([
            ("thinking", "Thinking step 1..."),
            ("content", "### 1. ROOT CAUSE\nRoot cause text.\n\n### 2. MINIMAL PATCH\n```python\nfixed_code()\n```\nExplanation.\n\n### 3. BUTTERFLY EFFECT\nImmediate crash.\n\n### 4. REGRESSION TEST\n```python\ntest_code()\n```\n\n### 5. CONFIDENCE\nScore: 99%"),
            ("done", {"done": True})
        ])

        thinking_calls = []
        result = run_debug_analysis(
            ollama_url="http://localhost:11434",
            model="gemma4:e2b",
            language="python",
            code="bug()",
            error="Crash",
            on_thinking=lambda t: thinking_calls.append(t)
        )

        self.assertIn("Root cause text", result["root_cause"])
        self.assertIn("fixed_code()", result["patch_code"])
        self.assertIn("Immediate crash", result["butterfly_effect"])
        self.assertIn("test_code()", result["regression_test"])
        self.assertEqual(len(thinking_calls), 1)


if __name__ == "__main__":
    unittest.main()
