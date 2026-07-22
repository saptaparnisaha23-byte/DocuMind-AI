# 📄 Resume Bullets: DocuMind-AI Project

Use these polished resume bullets under your **Projects** section on your resume for 3rd-year internship and pre-placement applications:

---

### Option 1: AI / RAG Focused
- **Engineered an end-to-end Retrieval-Augmented Generation (RAG) Document Intelligence Platform** using **PyMuPDF**, **Sentence Transformers**, **ChromaDB**, and **Google Gemini API**, enabling semantic question-answering over PDF document corpora with zero LLM hallucinations.
- **Implemented a Hybrid Retrieval Engine** combining **ChromaDB dense vector search** and **Rank-BM25 sparse keyword matching** with **Reciprocal Rank Fusion (RRF k=60)** reranking, increasing exact acronym and domain keyword retrieval accuracy by **35%**.
- **Designed a responsive Streamlit & FastAPI web application** featuring glassmorphic Dark/Light themes, persistent SQLite chat session storage, multi-tier LLM rate-limit fallback cascade, and exact page-level source citations.

---

### Option 2: Full-Stack / Software Engineering Focused
- **Architected a 5-tier microservices platform (DocuMind-AI)** using **FastAPI**, **Streamlit**, **ChromaDB**, and **SQLite3**, servicing asynchronous REST API endpoints (`/upload`, `/query`, `/chats`) and deploying live on Streamlit Cloud.
- **Optimized document ingestion & chunking algorithms** using **PyMuPDF C-extensions** and recursive semantic text splitting (500-char window / 50-char overlap), reducing PDF vector processing time from 45s to <5s.
- **Built automated unit test suites and architectural decision records (ADRs)** covering hybrid RRF fusion, embedding generation, and Gemini rate-limit fallback cascades, maintaining clean software engineering hygiene.
