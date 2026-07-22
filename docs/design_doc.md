# 📚 DocuMind-AI: System Design Document

**Author:** Saptaparni Saha  
**Degree:** B.Tech CSE – Artificial Intelligence & Data Engineering (Lovely Professional University)  
**Program:** Foundations of Applied Machine Learning (Summer Internship 2026)  
**Problem Statement:** I2 – Document Q&A (RAG over a Focused Corpus)  
**Date:** July 2026  

---

## 1. Project Context & Objectives

DocuMind-AI is an enterprise-grade Retrieval-Augmented Generation (RAG) system designed to solve the inefficiency of manual search across unstructured PDF corpora (textbooks, research papers, legal documents, technical manuals). Standard keyword search fails when user queries use conceptual or domain-specific terminology that differs from literal source phrasing. Raw LLM ingestion suffers from strict context-window constraints, excessive API costs, and factual hallucinations.

DocuMind-AI overcomes these limitations by combining PyMuPDF document parsing, recursive character chunking, 384d/768d vector embeddings, ChromaDB vector storage, BM25 keyword matching, Reciprocal Rank Fusion (RRF $k=60$) candidate reranking, and Google Gemini LLM generation with exact page-level citations.

---

## 2. High-Level Architecture & Component Decomposition

The system is structured across 5 decoupled tiers:

```
[ Tier 1: Presentation Layer ]
  └── Streamlit Web Application (frontend/app.py) with Dark/Light Glassmorphism Theme

[ Tier 2: API Gateway Layer ]
  └── FastAPI Async REST Server (app/main.py) servicing /upload, /query, /chats endpoints

[ Tier 3: Ingestion & Hybrid RAG Engine Layer ]
  ├── PyMuPDF (fitz) Extractor & Table Parser (app/ingest.py)
  ├── Recursive Character Splitter (500 chars / 50 overlap)
  ├── Sentence Transformers (all-MiniLM-L6-v2) & Gemini Embeddings (app/embed.py)
  ├── ChromaDB Vector Database (HNSW Index) + BM25 Sparse Index
  └── Reciprocal Rank Fusion (RRF k=60) Hybrid Candidate Reranker (app/retrieve.py)

[ Tier 4: LLM Generation & Citation Engine Layer ]
  ├── Primary LLM: Google Gemini 2.5 Flash / 1.5 Flash (app/chatbot.py)
  ├── Resilient Rate-Limit Fallback Cascade (HTTP 429 Handling)
  └── Inline Page & Chunk Citation Badges

[ Tier 5: Database & File Storage Layer ]
  ├── SQLite3 Chat Session Database (app/database.py)
  └── Local PDF Document Storage (data/pdfs/ & uploads/)
```

---

## 3. Detailed Technical Choices & Trade-offs

| Component Layer | Technology Selected | Alternatives Considered | Trade-off Rationale |
|---|---|---|---|
| **PDF Parsing** | PyMuPDF (`fitz`) | PyPDF2, pdfplumber, Unstructured.io | PyMuPDF offers 10x faster C-extension parsing speed, low RAM footprint, and accurate table detection. |
| **Text Chunking** | Recursive Character Splitter (500/50) | Fixed-size chunking, Paragraph splitting | 500-char chunks with 50-char overlap preserve semantic boundaries while staying within optimal embedding context. |
| **Vector DB** | ChromaDB (HNSW) | Qdrant, Pinecone, FAISS | ChromaDB provides zero-config local persistence, fast ANN vector queries, and built-in metadata filtering. |
| **Sparse Retrieval** | Rank-BM25 | TF-IDF, Elasticsearch | BM25 provides exact keyword and acronym matching (MLR, SLR, OLS) without high Java infrastructure overhead. |
| **Rank Fusion** | Reciprocal Rank Fusion ($k=60$) | Linear Score Summing | RRF normalizes scale discrepancies between cosine distance (-1 to +1) and BM25 scores (0 to +inf). |
| **Primary LLM** | Google Gemini API | OpenAI GPT-4o, Claude Haiku | Gemini delivers high reasoning accuracy, generous rate limits, fast response latency, and multi-tier model availability. |

---

## 4. Data Flow Pipeline

1. **PDF Ingestion**: User uploads PDF via Streamlit or REST API. PyMuPDF extracts text page by page.
2. **Chunking**: Text is split into 500-character semantic chunks with 50-character overlap.
3. **Indexing**: Embeddings are computed (`all-MiniLM-L6-v2` / `gemini-embedding-001`) and stored in ChromaDB alongside document metadata (`document_name`, `page`, `chunk_id`). An in-memory BM25 index is built for sparse keyword lookup.
4. **Hybrid Retrieval**: When a query is received, ChromaDB computes top-k dense vector matches, while BM25 calculates top-k keyword matches. RRF ($k=60$) merges both candidate lists into a unified ranked list.
5. **Grounded Generation**: Top-ranked passages are formatted into a strict system prompt and sent to Google Gemini, which generates a factual answer accompanied by explicit page numbers and text citations.

---

## 5. Security, Reliability & Failure Modes

- **Input Sanitization**: Query inputs are validated to prevent prompt injection and oversized payload attacks.
- **Resilient Fallback**: If Google Gemini returns HTTP 429 (rate limit), the system automatically cascades across model tiers (`gemini-2.5-flash` → `gemini-1.5-flash` → mock standalone extractor).
- **Standalone Fallback**: If the FastAPI server is unreachable, the Streamlit frontend gracefully switches to local in-memory execution mode.
