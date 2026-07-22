# DocuMind-AI — 3rd Year Extension Roadmap

## What this project is today
DocuMind-AI is an end-to-end Retrieval-Augmented Generation (RAG) system running on Streamlit and FastAPI. It processes PDF documents into 500-character semantic chunks, indexes 384d/768d embeddings into ChromaDB alongside a BM25 sparse index, reranks candidate passages via Reciprocal Rank Fusion (RRF $k=60$), and synthesizes grounded answers with page-level citations using Google Gemini.

## The arc: where this could be by 3rd year internship (May 2027)
By May 2027, DocuMind-AI will evolve into **Enterprise Knowledge Graph & Agentic Multi-Modal RAG (E3)**. It will handle 4+ heterogeneous file formats (PDFs, Word documents, Excel sheets, SQL databases), support scanned image PDFs via OCR, execute multi-agent query decomposition via LangGraph, and operate within a containerized Kubernetes production environment with automated Ragas evaluation CI/CD pipelines.

---

## 3rd Year Semester Plan (Aug 2026 – Dec 2026)

### Milestone 1 (Aug–Sep 2026): Production Vector DB & Multi-Format Ingestion
- **What I'll add**: Migrate vector storage to self-hosted Qdrant & pgvector; add DOCX, PPTX, and HTML document parsers; add OCR support via Tesseract/Surya for scanned PDFs.
- **Tools I'll learn**: Qdrant, PostgreSQL + pgvector, Unstructured.io, Tesseract OCR.
- **Time commitment**: 10 hours/week
- **Done looks like**: System ingests multi-format documents and scanned PDFs into Qdrant with zero text loss.

### Milestone 2 (Oct–Nov 2026): Agentic RAG Workflows & Self-Correction
- **What I'll add**: Multi-step query decomposition, web-search fallback (Tavily API), and self-reflection validation loops to detect hallucinations before answering.
- **Tools I'll learn**: LangGraph, LangChain Expression Language (LCEL), Tavily Search API.
- **Time commitment**: 12 hours/week
- **Done looks like**: Complex user queries are broken down into sub-queries, retrieved across graph nodes, and self-evaluated.

### Milestone 3 (Nov–Dec 2026): Automated Evaluation & Observability Pipeline
- **What I'll add**: Automated RAG evaluation benchmark harness (Ragas & DeepEval) measuring Faithfulness, Answer Relevance, and Context Recall on a 100+ Q&A test set; add Prometheus + Grafana metrics.
- **Tools I'll learn**: Ragas, DeepEval, Prometheus, Grafana, OpenTelemetry.
- **Time commitment**: 10 hours/week
- **Done looks like**: Every GitHub pull request triggers an automated evaluation benchmark report with quantitative precision scores.

---

## 3rd Year Internship Plan (Jun–Jul 2027)
This project becomes **E3: Enterprise Multi-Modal Knowledge Engine**, positioning me for AI/ML Engineering and LLMOps Specialist roles at companies like Amazon, Google, Razorpay, Adobe, and Flipkart.

---

## What I'll need from the placement / mentor ecosystem
- Access to GPU instances (NVIDIA T4 / A10G) for local LLM inference testing (Ollama / vLLM).
- Guidance on advanced RAG evaluation benchmarks and production latency tuning.
- Code reviews on multi-agent orchestrations.

---

## Risks & open questions
- **VRAM / Hardware Latency**: Running open-source embeddings and re-ranker models locally on CPU can introduce latency; cloud inference endpoints may be required.
- **Context Window Drift**: Managing long multi-turn agentic conversational state without exceeding token budgets.
