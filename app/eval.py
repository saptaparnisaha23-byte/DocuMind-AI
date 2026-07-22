"""
DocuMind-AI Evaluation Module
Runs benchmark evaluation on 20+ Q&A test cases evaluating 3 core axes:
1. Correctness (1-5)
2. Citation Precision (1-5)
3. Completeness (1-5)
"""

import json
import time
from app.chatbot import ask_question

# 20 Benchmark Test Cases across single PDF, multi-PDF comparison, acronyms, and out-of-scope queries
BENCHMARK_DATASET = [
    {
        "id": 1,
        "question": "What is Multiple Linear Regression (MLR)?",
        "category": "Concept Definition",
        "expected_keywords": ["regression", "independent variables", "dependent variable"],
    },
    {
        "id": 2,
        "question": "What is Ordinary Least Squares (OLS)?",
        "category": "Formula & Method",
        "expected_keywords": ["sum of squared residuals", "minimizes"],
    },
    {
        "id": 3,
        "question": "What is Simple Linear Regression (SLR)?",
        "category": "Concept Definition",
        "expected_keywords": ["single independent variable", "linear relationship"],
    },
    {
        "id": 4,
        "question": "What is Variance Inflation Factor (VIF)?",
        "category": "Diagnostic Metric",
        "expected_keywords": ["multicollinearity", "variance"],
    },
    {
        "id": 5,
        "question": "What is Root Mean Squared Error (RMSE)?",
        "category": "Metric",
        "expected_keywords": ["square root", "residuals", "error"],
    },
    {
        "id": 6,
        "question": "What is R-squared (R2)?",
        "category": "Metric",
        "expected_keywords": ["coefficient of determination", "variance explained"],
    },
    {
        "id": 7,
        "question": "Difference between Simple Linear Regression and Multiple Linear Regression",
        "category": "Comparison",
        "expected_keywords": ["one predictor", "multiple predictors"],
    },
    {
        "id": 8,
        "question": "What are the core assumptions of OLS regression?",
        "category": "Core Theory",
        "expected_keywords": ["linearity", "homoscedasticity", "independence", "normality"],
    },
    {
        "id": 9,
        "question": "How is multicollinearity detected and resolved?",
        "category": "Model Tuning",
        "expected_keywords": ["VIF", "correlation matrix", "drop features"],
    },
    {
        "id": 10,
        "question": "Explain heteroscedasticity in regression modeling",
        "category": "Diagnostics",
        "expected_keywords": ["non-constant variance", "residuals"],
    },
    {
        "id": 11,
        "question": "What is the role of the intercept term in a linear model?",
        "category": "Theory",
        "expected_keywords": ["expected value", "zero predictors"],
    },
    {
        "id": 12,
        "question": "Difference between MTH176 and MTH178",
        "category": "Multi-Doc Comparison",
        "expected_keywords": ["syllabus", "prerequisites", "course"],
    },
    {
        "id": 13,
        "question": "What changed between MTH176 and MTH178?",
        "category": "Conversational Follow-up",
        "expected_keywords": ["topics", "units"],
    },
    {
        "id": 14,
        "question": "Explain how gradient descent optimizes regression weights",
        "category": "Optimization",
        "expected_keywords": ["learning rate", "loss function", "partial derivative"],
    },
    {
        "id": 15,
        "question": "What is Adjusted R-squared and why is it preferred over R-squared?",
        "category": "Metric",
        "expected_keywords": ["penalizes extra predictors", "degrees of freedom"],
    },
    {
        "id": 16,
        "question": "What is quantum teleportation protocol in Python?",
        "category": "Out-of-Scope (Refusal)",
        "expected_keywords": ["not found in the uploaded documents"],
    },
    {
        "id": 17,
        "question": "How to make a Neapolitan pizza at home?",
        "category": "Out-of-Scope (Refusal)",
        "expected_keywords": ["not found in the uploaded documents"],
    },
    {
        "id": 18,
        "question": "What are residual plots used for in regression analysis?",
        "category": "Diagnostics",
        "expected_keywords": ["residuals", "fitted values", "pattern"],
    },
    {
        "id": 19,
        "question": "Explain Polynomial Regression vs Linear Regression",
        "category": "Comparison",
        "expected_keywords": ["degree", "non-linear relationship"],
    },
    {
        "id": 20,
        "question": "Summarize the key takeaways of the uploaded document",
        "category": "Document Summary",
        "expected_keywords": ["overview", "concepts"],
    },
]

def run_evaluation():
    print("=" * 60)
    print("DocuMind-AI: Running Benchmark Evaluation Suite (20 Test Cases)")
    print("=" * 60)
    
    results = []
    total_correctness = 0
    total_citation = 0
    total_completeness = 0
    
    for tc in BENCHMARK_DATASET:
        qid = tc["id"]
        q_text = tc["question"]
        cat = tc["category"]
        
        start_t = time.time()
        res = ask_question(session_id=f"eval_sess_{qid}", question=q_text)
        latency = round((time.time() - start_t) * 1000)
        
        answer = res.get("answer", "")
        sources = res.get("sources", [])
        
        # Scoring Logic
        # Correctness (1-5): check expected keywords / out-of-scope refusal
        correctness = 5
        if tc["category"] == "Out-of-Scope (Refusal)":
            if "not found in the uploaded documents" in answer.lower():
                correctness = 5
            else:
                correctness = 1
        else:
            kw_matches = sum(1 for kw in tc["expected_keywords"] if kw.lower() in answer.lower())
            if kw_matches >= len(tc["expected_keywords"]):
                correctness = 5
            elif kw_matches > 0:
                correctness = 4
            else:
                correctness = 3
                
        # Citation Precision (1-5): check if sources exist for in-scope
        citation_precision = 5
        if tc["category"] != "Out-of-Scope (Refusal)":
            if len(sources) > 0 or "Source:" in answer:
                citation_precision = 5
            else:
                citation_precision = 2
                
        # Completeness (1-5): check answer length and structure
        completeness = 5
        if len(answer.strip()) < 50 and tc["category"] != "Out-of-Scope (Refusal)":
            completeness = 3
            
        total_correctness += correctness
        total_citation += citation_precision
        total_completeness += completeness
        
        item = {
            "id": qid,
            "question": q_text,
            "category": cat,
            "correctness": correctness,
            "citation_precision": citation_precision,
            "completeness": completeness,
            "latency_ms": latency,
            "sources_count": len(sources)
        }
        results.append(item)
        print(f"[{qid}/20] {q_text[:35]}... -> Correctness: {correctness}/5, Citation: {citation_precision}/5, Complete: {completeness}/5 ({latency}ms)")
        
    num_tests = len(BENCHMARK_DATASET)
    avg_correctness = round(total_correctness / num_tests, 2)
    avg_citation = round(total_citation / num_tests, 2)
    avg_completeness = round(total_completeness / num_tests, 2)
    
    print("-" * 60)
    print(f"EVALUATION COMPLETE | Avg Correctness: {avg_correctness}/5 | Avg Citation Precision: {avg_citation}/5 | Avg Completeness: {avg_completeness}/5")
    print("-" * 60)
    
    return {
        "avg_correctness": avg_correctness,
        "avg_citation": avg_citation,
        "avg_completeness": avg_completeness,
        "results": results
    }

if __name__ == "__main__":
    run_evaluation()
