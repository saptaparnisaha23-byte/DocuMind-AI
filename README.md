# 📚 DocuMind-AI

An AI-powered Retrieval-Augmented Generation (RAG) based Document Question Answering System that enables users to process PDF documents, perform semantic search using vector embeddings, and generate context-aware answers using Google Gemini.

---

## 🌟 Features

- 📄 PDF text extraction using PyMuPDF
- ✂️ Intelligent document chunking
- 🧠 Semantic embeddings using Sentence Transformers
- 🗂️ ChromaDB vector database
- 🔍 Semantic similarity search
- 🤖 Google Gemini integration
- 📚 Retrieval-Augmented Generation (RAG)
- 💻 Modular Python project structure
- 📝 Environment variable support using python-dotenv

---

## 📌 Project Information

| Item | Details |
|------|---------|
| Project Name | DocuMind-AI |
| Problem Statement | I2 – Document Q&A (RAG over a Focused Corpus) |
| Segment | Foundations of Applied Machine Learning |
| Internship | Summer Internship 2026 |

---

# 📖 Project Overview

DocuMind-AI is a Retrieval-Augmented Generation (RAG) based application developed as part of the Summer Internship 2026 under the Foundations of Applied Machine Learning segment.

The project allows users to query information from PDF documents using natural language. Instead of sending an entire document to a Large Language Model, the system first retrieves the most relevant document sections using semantic vector search and then provides those sections as context to Google Gemini for answer generation.

The workflow includes:

- Extracting text from PDF documents
- Splitting text into semantic chunks
- Creating vector embeddings using Sentence Transformers
- Storing embeddings in ChromaDB
- Retrieving relevant document chunks using similarity search
- Generating grounded answers using Google Gemini

This approach reduces hallucinations while providing more accurate, document-based responses.

---

# 🎯 Objectives

- Extract text from PDF documents
- Generate semantic document chunks
- Build vector embeddings
- Store embeddings in ChromaDB
- Retrieve relevant information using semantic search
- Integrate Google Gemini for answer generation
- Implement an end-to-end Retrieval-Augmented Generation pipeline

---

# 📅 Internship Progress

## ✅ Week 1

- GitHub Repository Setup
- Project Structure
- README
- Design Document
- PDF Text Extraction using PyMuPDF
- Initial Git Commits

---

## ✅ Week 2

- Document Chunking
- Sentence Transformer Embeddings
- ChromaDB Integration
- Semantic Retrieval Pipeline
- ADR-001 Documentation
- Retrieval Testing

---

## ✅ Week 3 (Current Progress)

- Google Gemini Integration
- Complete Retrieval-Augmented Generation Pipeline
- End-to-End Question Answering through Terminal

---

# ✨ Current Capabilities

### 📄 Document Processing

- PDF Text Extraction
- Intelligent Text Chunking

### 🧠 Artificial Intelligence

- Sentence Transformer Embeddings
- Semantic Similarity Search
- Google Gemini Response Generation

### 🗂️ Vector Database

- ChromaDB Storage
- Vector Retrieval

### 💻 Software Engineering

- Modular Codebase
- Environment Variable Support
- Git Version Control

---

# 🏗️ System Architecture

```
                PDF Document
                     │
                     ▼
          PyMuPDF Text Extraction
                     │
                     ▼
            Document Chunking
                     │
                     ▼
    Sentence Transformer Embeddings
                     │
                     ▼
             ChromaDB Vector Store
                     │
                     ▼
             Semantic Retrieval
                     │
                     ▼
              Google Gemini
                     │
                     ▼
        Context-Aware AI Response
```

---

# 📂 Project Structure

```
DocuMind-AI
│
├── app/
│   ├── app.py
│   ├── chatbot.py
│   ├── embed.py
│   ├── ingest.py
│   ├── retrieve.py
│   ├── main.py
│   ├── test_gemini.py
│   └── test_retrieval.py
│
├── data/
│   └── pdfs/
│
├── docs/
│   ├── adr/
│   └── design_doc.md
│
├── tests/
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# 🛠 Tech Stack

| Layer | Technology |
|---------|------------|
| Language | Python |
| PDF Processing | PyMuPDF |
| Chunking | LangChain RecursiveCharacterTextSplitter |
| Embedding Model | Sentence Transformers (all-MiniLM-L6-v2) |
| Vector Database | ChromaDB |
| LLM | Google Gemini |
| Environment Variables | python-dotenv |
| Version Control | Git & GitHub |

---

# ⚙️ Installation

```bash
git clone <your-repository-url>

cd DocuMind-AI

pip install -r requirements.txt
```

Create a `.env` file:

```
GEMINI_API_KEY=YOUR_API_KEY
```

Run the application:

```bash
python app/main.py
```

---

# 📊 Current Progress

| Feature | Status |
|---------|--------|
| Repository Setup | ✅ |
| Design Document | ✅ |
| PDF Extraction | ✅ |
| Document Chunking | ✅ |
| Sentence Transformer Embeddings | ✅ |
| ChromaDB Integration | ✅ |
| Semantic Search | ✅ |
| Gemini Integration | ✅ |
| End-to-End RAG Pipeline | ✅ |
| Streamlit Interface | ⏳ Planned |
| Source Citations | ⏳ Planned |
| Multi-PDF Support | ⏳ Planned |
| Unit Testing | ⏳ Planned |

---

# 📚 What I Learned

### Week 1

- Project organization using GitHub
- PDF processing with PyMuPDF
- Fundamentals of Retrieval-Augmented Generation

### Week 2

- Document chunking
- Vector embeddings
- ChromaDB
- Semantic search

### Week 3

- Google Gemini integration
- Prompt engineering
- Building a complete Retrieval-Augmented Generation pipeline

---

# 🚀 Future Enhancements

- Streamlit Web Interface
- Source Citations
- Dynamic PDF Upload
- Multi-document Support
- Chat History
- Hybrid Search
- Cloud Deployment
- Docker Support

---

# 👩‍💻 Developer

**Saptaparni Saha**

B.Tech – Artificial Intelligence & Data Engineering

Lovely Professional University

Summer Internship 2026

Problem Statement: **I2 – Document Q&A (RAG over a Focused Corpus)**
