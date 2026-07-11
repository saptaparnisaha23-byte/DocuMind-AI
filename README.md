# DocuMind-AI

> Enterprise-style Retrieval-Augmented Generation (RAG) system for PDF-based Knowledge Retrieval, Semantic Search, Citation Generation, and LLM-powered Question Answering.

---

## 📌 Internship Details

**Internship:** 2-Year AI/ML Internship

**Segment:** Segment 3 — Foundations of Applied Machine Learning

**Problem Statement:** I2 — Document Question Answering

**Project:** DocuMind-AI

**Author:** Saptaparni Saha

---

# Project Overview

DocuMind-AI is an enterprise-style Retrieval-Augmented Generation (RAG) application that enables users to upload PDF documents and ask questions in natural language.

Instead of relying only on the Large Language Model's general knowledge, the system retrieves the most relevant sections from uploaded documents using semantic search and generates context-aware responses using Google's Gemini API.

This architecture minimizes hallucinations while producing accurate, document-grounded answers.

---

# Project Architecture

```
                 User
                   │
                   ▼

          Upload PDF Document
                   │
                   ▼

         PDF Text Extraction
            (PyMuPDF)
                   │
                   ▼

      Recursive Text Chunking
                   │
                   ▼

      SentenceTransformer Embeddings
                   │
                   ▼

             ChromaDB
        (Vector Database)
                   │
                   ▼

        Semantic Retrieval
                   │
                   ▼

          Relevant Chunks
                   │
                   ▼

         Gemini LLM API
                   │
                   ▼

      Context-Aware Answer
```

---

# Features Implemented

- PDF Upload Support
- PDF Text Extraction
- Recursive Text Chunking
- Semantic Embedding Generation
- ChromaDB Vector Storage
- Semantic Similarity Search
- Google Gemini API Integration
- Modular Python Project Structure

---

# Technology Stack

| Component | Technology |
|------------|------------|
| Programming Language | Python 3.12 |
| Frontend *(Upcoming)* | Streamlit |
| PDF Processing | PyMuPDF |
| Text Chunking | LangChain |
| Embedding Model | Sentence Transformers |
| Vector Database | ChromaDB |
| Large Language Model | Google Gemini |
| Version Control | Git & GitHub |

---

# Project Structure

```
DocuMind-AI/

│
├── app/
│   ├── app.py
│   ├── ingest.py
│   ├── embed.py
│   ├── retrieve.py
│   ├── chatbot.py
│   └── test_gemini.py
│
├── data/
│   └── pdfs/
│
├── docs/
│   └── design_doc.md
│
├── tests/
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

# Current Workflow

### Step 1

Upload a PDF document.

↓

### Step 2

Extract text using PyMuPDF.

↓

### Step 3

Split the text into overlapping chunks.

↓

### Step 4

Generate semantic embeddings.

↓

### Step 5

Store embeddings inside ChromaDB.

↓

### Step 6

Search the vector database for the most relevant chunks.

↓

### Step 7

Send retrieved chunks to Gemini.

↓

### Step 8

Generate a context-aware answer.

---

# Progress

## Week 1 ✅

- Repository Setup
- GitHub Workflow
- Project Documentation
- Design Document
- Folder Structure
- Initial Commits
- PDF Text Extraction

---

## Week 2 ✅

- Recursive Text Chunking
- Embedding Generation
- ChromaDB Integration
- Semantic Retrieval
- Google Gemini API Integration

---

# Upcoming Work

- Connect Retriever with Gemini
- Build Complete RAG Pipeline
- Streamlit Chat Interface
- Multi-PDF Support
- Source Citation Display
- Conversation Memory
- Deployment

---

# What I Learned

- Git and GitHub version control workflow.
- Markdown documentation and project organization.
- PDF text extraction using PyMuPDF.
- Text chunking using LangChain.
- Semantic embeddings using Sentence Transformers.
- Vector databases with ChromaDB.
- Semantic retrieval using vector similarity search.
- Integrating Google Gemini API with Python.
- Fundamentals of Retrieval-Augmented Generation (RAG).

---

# Current Status

**Project Stage:** Retrieval pipeline completed. LLM integration and user interface are planned for Week 3.

**Status:** In Progress

The project can successfully:

- Read PDF documents
- Extract document text
- Split text into chunks
- Generate embeddings
- Store vectors in ChromaDB
- Retrieve relevant chunks
- Connect to Gemini API

The next milestone is to combine retrieval with Gemini to build a fully functional RAG-powered PDF Question Answering system.

---

## Author

**Saptaparni Saha**

B.Tech AI & Data Engineering

Lovely Professional University

---
