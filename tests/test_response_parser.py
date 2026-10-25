"""Unit tests for response parsing and diff generation."""

import unittest
from utils.response_parser import parse_slothfix_response, generate_unified_diff


class TestResponseParser(unittest.TestCase):
    """Test suite for diagnostic response parser."""

    def test_parse_complete_response(self):
        sample = """
### 1. ROOT CAUSE
The error occurred because variable `user` was None.

### 2. MINIMAL PATCH
```python
if user is not None:
    return user.get("name")
```
This check guarantees user is defined.

### 3. BUTTERFLY EFFECT & DOWNSTREAM IMPACT
- **Immediate Failure**: Crashes with AttributeError
- **Caller Cascades**: Returns 500 error
- **Silent / System Risks**: Desynchronized cache

### 4. REGRESSION TEST
```python
def test_user_none():
    assert fetch_user(999) is None
```

### 5. CONFIDENCE & SAFETY NOTICE
- Confidence Score: 98%
- Verification Status: Model-generated proposal
- Rationale: High confidence fix
"""
        parsed = parse_slothfix_response(sample)
        
        self.assertIn("because variable `user` was None", parsed["root_cause"])
        self.assertIn('if user is not None:', parsed["patch_code"])
        self.assertIn("guarantees user is defined", parsed["patch_explanation"])
        self.assertIn("Immediate Failure", parsed["butterfly_effect"])
        self.assertIn("def test_user_none", parsed["regression_test"])
        self.assertIn("Confidence Score: 98%", parsed["confidence_safety"])

    def test_parse_fallback_for_unstructured_response(self):
        sample = "Just a raw unformatted text from model without sections."
        parsed = parse_slothfix_response(sample)
        
        self.assertEqual(parsed["root_cause"], sample)
        self.assertEqual(parsed["patch_code"], "")

    def test_parse_partial_response(self):
        sample = """
### 1. ROOT CAUSE
Index out of bounds on loop.

### 2. MINIMAL PATCH
```python
range(len(items))
```
Use exact length.
"""
        parsed = parse_slothfix_response(sample)
        
        self.assertIn("Index out of bounds", parsed["root_cause"])
        self.assertIn("range(len(items))", parsed["patch_code"])
        self.assertEqual(parsed["regression_test"], "")


class TestUnifiedDiff(unittest.TestCase):
    """Test suite for unified diff generator."""

    def test_diff_detected(self):
        orig = "def foo():\n    return False\n"
        patch = "def foo():\n    return True\n"
        diff = generate_unified_diff(orig, patch, filename="test.py")
        
        self.assertIn("--- a/test.py (original)", diff)
        self.assertIn("+++ b/test.py (SlothFix patch)", diff)
        self.assertIn("-    return False", diff)
        self.assertIn("+    return True", diff)

    def test_identical_diff(self):
        code = "def foo():\n    return True\n"
        diff = generate_unified_diff(code, code)
        
        self.assertEqual(diff, "No textual differences detected.")


if __name__ == "__main__":
    unittest.main()
