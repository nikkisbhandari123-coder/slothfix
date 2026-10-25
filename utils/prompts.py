"""Prompt templates and language definitions for SlothFix."""

from typing import Dict

LANG_EXTENSIONS: Dict[str, str] = {
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

SAMPLE_CASES: Dict[str, Dict[str, str]] = {
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


def build_debug_prompt(language: str, code: str, error: str) -> str:
    """Construct a systematic, structured prompt for Gemma to diagnose the bug.
    
    Args:
        language: Programming language name (e.g. 'python', 'javascript').
        code: Buggy source code snippet.
        error: Runtime stack trace or error log.
        
    Returns:
        Formatted prompt requesting structured markdown sections.
    """
    return f"""You are SlothFix, an expert debugging AI powered by Gemma.
Analyze the following code and error thoroughly:

Programming Language: {language}

Buggy Code:
```{language}
{code}
```

Error Message / Traceback:
```
{error}
```

Format your response strictly using these markdown sections:

### 1. ROOT CAUSE
[Explain exactly why this error occurred at runtime, citing the specific line and variable conditions.]

### 2. MINIMAL PATCH
```{language}
[The corrected code snippet fixing the bug with minimal, clean changes]
```
[Brief 1-2 sentence explanation of why this patch resolves the bug cleanly]

### 3. BUTTERFLY EFFECT & DOWNSTREAM IMPACT
- **Immediate Failure**: [What immediately crashes at this call site]
- **Caller Cascades**: [How parent functions, API endpoints, or user requests fail]
- **Silent / System Risks**: [Potential database inconsistency, uncommitted state, or cascading retry storms]

### 4. REGRESSION TEST
```{language}
[Complete standalone regression test code (e.g. pytest for Python, Jest for JavaScript, etc.) that reproduces the failure on buggy code and verifies the fix. Ready to copy.]
```

### 5. CONFIDENCE & SAFETY NOTICE
- Confidence Score: [e.g. 98%]
- Verification Status: Model-generated proposal (unexecuted on host machine)
- Rationale: [Brief justification]
"""
