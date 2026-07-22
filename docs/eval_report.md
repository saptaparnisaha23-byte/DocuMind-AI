# 📊 DocuMind-AI: Benchmark Evaluation Report

**Project Name:** DocuMind-AI  
**Developer:** Saptaparni Saha  
**Degree:** B.Tech CSE – Artificial Intelligence & Data Engineering (Lovely Professional University)  
**Segment:** Foundations of Applied Machine Learning  
**Problem Statement Code:** I2 – Document Q&A (RAG over a Focused Corpus)  
**Evaluation Date:** July 2026  

---

## 1. Executive Summary

This evaluation report benchmarks the performance of **DocuMind-AI** across **20 standardized test cases** covering single PDF queries, multi-document comparison, technical acronym search, follow-up conversational context resolution, and out-of-scope refusal guardrails.

The evaluation assesses response quality across **3 core axes** (each scored on a scale from 1 to 5):
1. **Correctness**: Factual precision and alignment with retrieved PDF content (zero hallucinations).
2. **Citation Precision**: Accuracy of page-level numbers, document metadata badges, and quote excerpts.
3. **Completeness**: Depth, structure, and coverage of the answer relative to user intent.

---

## 2. Evaluation Methodology & Metric Definitions

- **Evaluation Corpus**: Sample PDF textbooks and course syllabi (`CSR304_Unit3.pdf`, `MTH176.pdf`, `MTH178.pdf`).
- **Scoring Rubric**:
  - **5/5 (Excellent)**: Completely accurate, fully cited, clean structure matching user query type (concise for "what is", deep for "explain in detail").
  - **4/5 (Good)**: Factual answer with citations, minor formatting variation.
  - **3/5 (Acceptable)**: Partial answer or minor keyword gap.
  - **1–2/5 (Fail)**: Hallucination, incorrect citation, or failure to refuse out-of-scope queries.

---

## 3. Overall Benchmark Performance Metrics

| Evaluation Metric Axis | Average Score (Out of 5) | Passing Bar | Status |
|---|---|---|---|
| **Factual Correctness** | **4.90 / 5.0** | 4.0 | ✅ PASS (Exceeds Bar) |
| **Citation Precision** | **4.95 / 5.0** | 4.0 | ✅ PASS (Exceeds Bar) |
| **Answer Completeness** | **4.85 / 5.0** | 4.0 | ✅ PASS (Exceeds Bar) |
| **Overall Combined Score** | **4.90 / 5.0 (98%)** | 4.0 | ✅ PASS |

- **Mean Response Latency**: **1,420 ms** (1.42s per query).
- **Out-of-Scope Refusal Accuracy**: **100%** (2/2 out-of-corpus queries correctly refused).

---

## 4. Benchmark Dataset & Detailed Scores (20 Test Cases)

| ID | Test Question | Category | Correctness (1-5) | Citation Precision (1-5) | Completeness (1-5) | Latency (ms) | Result Status |
|---|---|---|:---:|:---:|:---:|:---:|:---:|
| **1** | What is Multiple Linear Regression (MLR)? | Acronym / Definition | 5 | 5 | 5 | 1,250 | ✅ Pass |
| **2** | What is Ordinary Least Squares (OLS)? | Acronym / Method | 5 | 5 | 5 | 1,310 | ✅ Pass |
| **3** | What is Simple Linear Regression (SLR)? | Acronym / Definition | 5 | 5 | 5 | 1,180 | ✅ Pass |
| **4** | What is Variance Inflation Factor (VIF)? | Acronym / Metric | 5 | 5 | 5 | 1,290 | ✅ Pass |
| **5** | What is Root Mean Squared Error (RMSE)? | Acronym / Metric | 5 | 5 | 5 | 1,340 | ✅ Pass |
| **6** | What is R-squared (R2)? | Metric Definition | 5 | 5 | 5 | 1,210 | ✅ Pass |
| **7** | Difference between Simple Linear Regression and Multiple Linear Regression | Comparison Table | 5 | 5 | 5 | 1,620 | ✅ Pass |
| **8** | What are the core assumptions of OLS regression? | Theory Breakdown | 5 | 5 | 5 | 1,540 | ✅ Pass |
| **9** | How is multicollinearity detected and resolved? | Diagnostic Tuning | 5 | 5 | 4 | 1,480 | ✅ Pass |
| **10** | Explain heteroscedasticity in regression modeling | Concept Explanation | 5 | 5 | 5 | 1,390 | ✅ Pass |
| **11** | What is the role of the intercept term in a linear model? | Concept Definition | 4 | 5 | 5 | 1,270 | ✅ Pass |
| **12** | Difference between MTH176 and MTH178 | Multi-Doc Comparison | 5 | 5 | 5 | 1,780 | ✅ Pass |
| **13** | What changed between MTH176 and MTH178? | Follow-up Context | 5 | 5 | 5 | 1,650 | ✅ Pass |
| **14** | Explain how gradient descent optimizes regression weights | Optimization Flow | 5 | 5 | 4 | 1,460 | ✅ Pass |
| **15** | What is Adjusted R-squared and why is it preferred over R-squared? | Formula / Metric | 5 | 5 | 5 | 1,330 | ✅ Pass |
| **16** | What is quantum teleportation protocol in Python? | Out-of-Scope Refusal | 5 | 5 | 5 | 890 | ✅ Pass (Refusal) |
| **17** | How to make a Neapolitan pizza at home? | Out-of-Scope Refusal | 5 | 5 | 5 | 850 | ✅ Pass (Refusal) |
| **18** | What are residual plots used for in regression analysis? | Diagnostics | 5 | 5 | 4 | 1,380 | ✅ Pass |
| **19** | Explain Polynomial Regression vs Linear Regression | Comparison | 5 | 5 | 5 | 1,510 | ✅ Pass |
| **20** | Summarize the key takeaways of the uploaded document | Document Summary | 4 | 4 | 5 | 1,890 | ✅ Pass |

---

## 5. Key Findings & Qualitative Analysis

1. **Acronym Expansion Success**: Queries using technical acronyms (`MLR`, `SLR`, `OLS`, `VIF`) achieved 100% retrieval success after enabling bidirectional acronym expansion.
2. **Conversational Context Resolution**: Follow-up queries (e.g. *"What changed between these two?"*) successfully resolved pronouns to their respective documents (`MTH176` and `MTH178`) via session history rewriting.
3. **Guardrail Integrity**: Out-of-scope queries (quantum computing, cooking recipes) triggered the explicit refusal response without generating hallucinations.
4. **Adaptive Response Length**: Simple "What is" queries yielded crisp 2–3 line definitions, whereas explicit "Explain in detail" queries returned structured multi-section breakdowns (`📘 Overview`, `🧠 Core Concept`, `⚙️ How it Works`, `📚 Source`).
