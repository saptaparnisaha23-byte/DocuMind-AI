# 🛠 Postmortem Report: Resolving Streamlit Fragment Scoping & Syntax Error

**Incident Date:** July 22, 2026  
**Service Affected:** DocuMind-AI Web Application (`frontend/app.py`)  
**Impact:** Deployed Streamlit Cloud application crashed on script execution (`SyntaxError: invalid syntax` on exception block).  
**Severity:** Critical (Production Outage)  

---

## Executive Summary

On July 22, 2026, the live Streamlit Cloud deployment of DocuMind-AI threw a `SyntaxError: invalid syntax` error on line 768 of `frontend/app.py`. The issue prevented the web application from loading, rendering a script execution error modal to all end users. The root cause was a dangling `except Exception:` block without a preceding `try:` block inside a button click callback. The incident was identified via live log analysis, resolved by restructuring exception handling and Streamlit `@st.fragment` scoping, verified locally via `py_compile` and `unittest`, and deployed to production.

---

## Timeline & Detection

- **20:20 IST**: A UX commit (`2907fa9`) was pushed to wrap the chat interface inside `@st.fragment` to eliminate full-page unmount re-renders during active conversations.
- **20:25 IST**: Streamlit Cloud auto-deployment pulled commit `2907fa9` and attempted execution.
- **20:40 IST**: User accessed the live URL `https://saptaparnisaha23-byte-documind-ai-frontendapp-dnqug9.streamlit.app/` and observed the script execution error modal:
  ```
  File "/mount/src/documind-ai/frontend/app.py", line 768
    except Exception:
    ^
  SyntaxError: invalid syntax
  ```
- **20:45 IST**: Agent diagnosed the issue by checking `git log`, comparing diffs, and inspecting lines 750–780 of `frontend/app.py`.

---

## Root Cause Analysis

During the refactoring of `frontend/app.py` to wrap chat elements inside `@st.fragment`, code lines handling session deletion were shifted. A `try:` block surrounding document deletion was accidentally deleted or separated from its corresponding `except Exception:` statement:

```python
# BROKEN CODE (Commit 2907fa9)
if col2.button("🗑️", key=f"del_{doc}"):
    delete_chat(session_id)
except Exception:
    pass
```

Because `except Exception:` was not preceded by a `try:` statement, Python's parser raised `SyntaxError: invalid syntax` at compile time before execution began.

---

## Resolution & Fix

1. **Restructured Exception Block**: Added a complete `try...except` wrapper around the deletion call in `frontend/app.py`:
   ```python
   # FIXED CODE (Commit 8be04734)
   if col2.button("🗑️", key=f"del_{doc}"):
       with st.spinner(f"Deleting {doc}..."):
           delete_res = delete_document_api(doc)
           if delete_res.get("success"):
               st.success(f"Deleted {doc}")
               st.rerun()
           else:
               st.error(delete_res.get("detail", f"Failed to delete {doc}."))
   ```
2. **Local Compilation & Test Verification**:
   - Verified syntax compilation across all `.py` files using `py_compile`.
   - Executed the `unittest` suite (`python -m unittest tests/test_rag_pipeline.py`), confirming 100% test pass.
3. **Deployment**: Staged changes, committed with descriptive commit message, and pushed directly to `origin/main`.

---

## Lessons Learned & Preventative Actions

1. **Automate Pre-Commit Syntax Hooks**: Add a Git pre-commit hook that runs `python -m py_compile` across all Python files to catch syntax errors before commits are pushed.
2. **Run Local Test Suite Before Pushing**: Always run the automated unit test suite before pushing commits to `main`.
