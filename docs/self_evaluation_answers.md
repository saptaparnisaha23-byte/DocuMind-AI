# 📝 DocuMind-AI: Self-Evaluation Form Answers

**Student Name:** Saptaparni Saha  
**Registration Number / Degree:** B.Tech CSE – Artificial Intelligence & Data Engineering  
**Segment Chosen:** Segment 3 — Foundations of Applied Machine Learning  
**Problem Statement Code:** I2 – Document Q&A (RAG over a Focused Corpus)  
**Live Project URL:** [https://saptaparnisaha23-byte-documind-ai-frontendapp-dnqug9.streamlit.app/](https://saptaparnisaha23-byte-documind-ai-frontendapp-dnqug9.streamlit.app/)  

---

### 1. Segment Chosen, Problem Chosen, and Why?
- **Segment:** Foundations of Applied Machine Learning.
- **Problem:** I2 — Document Q&A (RAG over a Focused Corpus).
- **Rationale:** RAG is the single most in-demand GenAI engineering pattern in 2026 placements. Building an end-to-end RAG system with hybrid retrieval, citations, and evaluation provided the foundational depth required for 3rd-year LLMOps and enterprise AI roles.

### 2. What tool/concept felt like a breakthrough this month?
- **Breakthrough Concept:** **Reciprocal Rank Fusion (RRF $k=60$) & Bidirectional Acronym Expansion**. Fusing dense vector search with BM25 sparse keyword retrieval resolved keyword-sensitive queries (e.g. "What is MLR?") that dense embeddings alone failed to retrieve.

### 3. What was the hardest week and why?
- **Hardest Week:** **Week 4 (Deployment & Performance Tuning)**. Resolving cloud container rate limits and eliminating full browser page reloads on Streamlit Community Cloud required deep inspection of `@st.fragment` scoping, caching resource clients with `@st.cache_resource`, and removing hard JS redirects.

### 4. Self-Rating of Core Skills (1 to 5 Scale)
- **Python / FastAPI Development:** 5 / 5
- **RAG & Vector Search (ChromaDB / BM25):** 5 / 5
- **Git & Version Control:** 5 / 5
- **Streamlit Web UI & State Management:** 4.8 / 5
- **Technical Writing & ADR Documentation:** 5 / 5

### 5. What would you build next if you had 2 more weeks?
- Integrate Qdrant as an enterprise vector database backend with payload metadata filtering, and add GraphRAG (knowledge graph extraction using NetworkX) for complex multi-hop reasoning.

### 6. Which 3rd-year internship segment are you best positioned for?
- **Segment E3 / E4 (Enterprise GenAI & LLMOps Systems)** — specifically building multi-source data ingestion, model fine-tuning, and agentic RAG workflows.

### 7. Top 3 target companies to apply for:
1. **Google / DeepMind** (AI Systems & Applied GenAI)
2. **Razorpay / PhonePe** (AI Platform & Engineering)
3. **Tiger Analytics / Genpact AI** (Applied Machine Learning)

### 8. 30-Day Post-Internship Momentum Plan
- **Days 1–10:** Package DocuMind-AI into Docker containers and deploy FastAPI backend on Render.
- **Days 11–20:** Implement agentic RAG query decomposition using LangGraph.
- **Days 21–30:** Publish a technical blog post explaining RRF hybrid search and present at student developer meetups.

### 9. Message for Internship Lead / Evaluator
- "Thank you for the rigorous curriculum. Building DocuMind-AI taught me how to go beyond basic tutorials to deliver production-grade GenAI with proper evaluation, guardrails, and clean architecture."
