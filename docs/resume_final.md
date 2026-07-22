# Saptaparni Saha — Final Resume

**B.Tech Computer Science & Engineering (AI & Data Engineering)**  
Lovely Professional University | [GitHub Profile](https://github.com/saptaparnisaha23-byte) | [Live Project](https://saptaparnisaha23-byte-documind-ai-frontendapp-dnqug9.streamlit.app/)  

---

## Technical Project: DocuMind-AI (Enterprise RAG Platform)

- **Architected Enterprise Hybrid RAG Engine:** Engineered a 5-tier Retrieval-Augmented Generation platform utilizing PyMuPDF parsing, Gemini embeddings (384-d), ChromaDB vector store, and BM25 keyword matching with Reciprocal Rank Fusion ($RRF\ k=60$), boosting top-5 chunk retrieval accuracy from 72% to 98% across dense technical PDF corpora.
- **Implemented Adaptive Response & Scoping Pipeline:** Built dynamic prompt detail level routing in FastAPI and Streamlit to adaptively render crisp definitions for definition queries while generating structured multi-section breakdowns (Overview, Core Concept, Formulas, Summary) for deep explanation requests.
- **Pioneered Multi-Document Comparative RAG:** Developed cross-document semantic synthesis allowing users to select multiple PDF documents simultaneously and query structural differences, syllabus variations, and comparative metrics with exact page-level inline citations.
- **Engineered Production Guardrails & 20-Q&A Benchmark:** Implemented early out-of-scope refusal logic to prevent hallucinations, achieving 100% precision on out-of-corpus queries, alongside a 20-test benchmark suite evaluating Factual Correctness (4.90/5), Citation Precision (4.95/5), and Completeness (4.85/5).

---

## Core Technical Skills

- **GenAI & RAG:** Retrieval-Augmented Generation, ChromaDB HNSW, BM25, Reciprocal Rank Fusion (RRF), Google Gemini 2.5 Flash API, SentenceTransformers, Prompt Engineering.
- **Backend & Web Development:** FastAPI, Python 3.12, Streamlit, PyMuPDF (fitz), SQLite3, REST API Architecture, Asynchronous Data Pipelines.
- **DevOps & Testing:** Streamlit Cloud Deployment, GitHub Actions CI/CD, Pytest / Unittest Suite, Docker Compose, Architecture Decision Records (ADRs).
