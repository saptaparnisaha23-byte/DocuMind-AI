# 🎯 Mock Interview Q&A: DocuMind-AI

These 5 technical Q&A pairs prepare you for questions an interviewer or 3rd-year internship evaluator will ask about your project.

---

### Q1: Why did you choose a Hybrid Retrieval approach (BM25 + Vector Search) instead of using pure dense vector search?
**Answer:**  
"Pure dense vector embeddings excel at capturing broad semantic concepts (e.g., matching 'car' with 'automobile'), but they struggle with exact keyword matching, technical acronyms (e.g., 'MLR', 'SLR', 'OLS'), table names, or specific error codes. Sparse retrieval using Rank-BM25 evaluates term frequency and inverse document frequency (TF-IDF), guaranteeing that exact keyword matches are scored high. By combining both using Reciprocal Rank Fusion ($RRF\ k=60$), DocuMind-AI gets the best of both worlds: deep semantic understanding from ChromaDB dense vectors and exact keyword precision from BM25."

---

### Q2: How does Reciprocal Rank Fusion (RRF) work, and why not just sum the Cosine Similarity and BM25 scores?
**Answer:**  
"Cosine similarity distance scores range strictly between -1 and +1 (or 0 to 1 for normalized vectors), whereas BM25 scores range from 0 to unbounded positive infinity depending on term rarity. Directly summing these raw scores would cause BM25 to completely dominate vector similarity. Reciprocal Rank Fusion ($RRF$) solves this by converting raw scores into ordinal rank positions ($r_m(d)$) and calculating:
$$RRF\_Score(d) = \sum \frac{1}{k + r_m(d)}$$
Using constant $k=60$ ensures that top-ranked results from both retrieval models receive high fused priority regardless of score scale differences."

---

### Q3: How do you handle LLM rate limits or quota exhaustion during user traffic spikes?
**Answer:**  
"DocuMind-AI implements an automated multi-tier LLM fallback cascade in `app/chatbot.py`. When a query request is dispatched, it attempts generation using `gemini-2.5-flash`. If an HTTP 429 (Too Many Requests / Quota Exceeded) status code is returned, the engine catches the exception and immediately cascades to `gemini-1.5-flash`. If external network connectivity fails entirely, the system activates an offline fallback mode that extracts relevant context snippets directly from local SQLite and ChromaDB storage."

---

### Q4: Why did you split text into 500-character chunks with a 50-character overlap?
**Answer:**  
"Choosing chunk size is a trade-off between semantic context preservation and retrieval precision. Chunks that are too large (e.g., 4000+ characters) dilute specific facts with irrelevant noise, making vector embeddings less distinct. Chunks that are too small (e.g., 100 characters) cut off sentences mid-thought. A 500-character window retains coherent paragraph context while fitting comfortably inside embedding model context limits. The 50-character overlap guarantees that key phrases appearing at chunk boundaries are not truncated."

---

### Q5: How do you ensure the LLM does not hallucinate answers outside the uploaded PDF documents?
**Answer:**  
"We enforce strict system prompt guardrails in `app/chatbot.py`. The prompt template mandates that the model generate answers **strictly** using the provided context passages retrieved from ChromaDB. If the retrieved context does not contain sufficient evidence to answer the query, the system prompt explicitly instructs the LLM to respond with: *'I could not find sufficient information in the uploaded documents to answer your question.'* Additionally, we require the model to attach inline citations with page numbers and exact quote snippets, making every statement verifiable."
