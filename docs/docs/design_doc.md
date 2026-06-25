# Design Document: AskMyBook

**Author:** Saptaparni Saha

**Date:** 25 June 2026

**Segment:** Segment 3 — Foundations of Applied Machine Learning

**Problem Statement:** I2 — Document Q&A

---

# 1. Overview

AskMyBook is a Retrieval-Augmented Generation (RAG) application that enables users to upload PDF documents and ask questions in natural language.

Instead of manually searching through large documents, users can interact with their PDFs using conversational queries. The system retrieves the most relevant document sections through semantic search and generates context-aware answers using a Large Language Model (LLM).

The objective is to provide accurate, explainable, and citation-supported answers from uploaded documents.

---

# 2. Tech Stack

| Component            | Technology            | Rationale                                      |
| -------------------- | --------------------- | ---------------------------------------------- |
| Programming Language | Python 3.11           | Core development language                      |
| Frontend             | Streamlit             | Simple and interactive web interface           |
| PDF Parsing          | PyMuPDF               | Efficient text extraction from PDFs            |
| Embedding Model      | Sentence Transformers | Converts text into vector embeddings           |
| Vector Database      | ChromaDB              | Stores and retrieves embeddings efficiently    |
| RAG Framework        | LangChain             | Orchestrates retrieval and generation pipeline |
| LLM                  | Gemini 2.5 Flash      | Generates natural language answers             |
| Version Control      | GitHub                | Source code management                         |
| Deployment           | Streamlit Cloud       | Easy project deployment                        |

---

# 3. Architecture Design

The system follows a Retrieval-Augmented Generation (RAG) architecture where uploaded documents are transformed into embeddings and stored in a vector database. User queries retrieve relevant document chunks which are then passed to the LLM for answer generation.

```text
                    [ User ]
                        │
                        ▼

            ┌─────────────────────┐
            │   Streamlit UI      │
            └──────────┬──────────┘
                       │
                       ▼

            ┌─────────────────────┐
            │ Retrieval Engine    │
            │    (LangChain)      │
            └──────────┬──────────┘
                       │
                       ▼

            ┌─────────────────────┐
            │     ChromaDB        │
            │  Vector Database    │
            └──────────┬──────────┘
                       ▲
                       │
                  Embeddings
                       │
                       ▼

            ┌─────────────────────┐
            │ Sentence Transformer│
            └──────────┬──────────┘
                       ▲
                       │
                  PDF Chunks
                       │
                       ▼

            ┌─────────────────────┐
            │ PDF Parser          │
            │ (PyMuPDF)           │
            └─────────────────────┘

                       │
                       ▼

            ┌─────────────────────┐
            │    Gemini LLM       │
            └─────────────────────┘
                       │
                       ▼

                Answer + Citation
```

---

# 4. Core System Flows

## Flow A: Document Ingestion Pipeline

```text
[User]
   │
   ▼

Upload PDF
   │
   ▼

Extract Text
(PyMuPDF)
   │
   ▼

Chunk Text
   │
   ▼

Generate Embeddings
   │
   ▼

Store in ChromaDB
```

### Description

1. User uploads a PDF document.
2. Text is extracted from the document.
3. The text is divided into manageable chunks.
4. Embeddings are generated for each chunk.
5. Embeddings are stored inside ChromaDB.

---

## Flow B: Question Answering Pipeline

```text
[User]
   │
   ▼

Ask Question
   │
   ▼

Retriever Searches
ChromaDB
   │
   ▼

Relevant Chunks
Retrieved
   │
   ▼

Gemini LLM
Generates Answer
   │
   ▼

Answer with Citation
```

### Description

1. User asks a question.
2. Retriever searches the vector database.
3. Relevant chunks are selected.
4. Context is sent to Gemini.
5. Gemini generates an answer.
6. Source citations are displayed.

---

# 5. Directory Structure Blueprint

```text
2_year_Internship

├── app/
│   ├── ingest.py
│   ├── retrieve.py
│   ├── generate.py
│   └── streamlit_app.py
│
├── data/
│   └── pdfs/
│
├── docs/
│   └── design_doc.md
│
├── tests/
│   └── test_retrieval.py
│
├── requirements.txt
│
├── README.md
│
└── .gitignore
```

---

# 6. Core Features

## Document Management

* Upload PDF documents
* Manage uploaded files
* Multi-document support

## Retrieval Layer

* Semantic Search
* Top-K Retrieval
* Vector Similarity Search

## Question Answering

* Natural Language Queries
* Context-Aware Answers
* Citation-Supported Responses

## User Experience

* Streamlit Web Interface
* Fast Response Generation
* Simple PDF Upload Workflow

---

# 7. Mini Extension

## Compare Two Documents

The mini-extension allows users to upload two PDFs and compare information related to a particular topic.

Example:

* Compare two versions of DSA Notes.
* Compare two research papers.
* Compare two policy documents.

Output:

* Similarities
* Differences
* Summary Report

---

# 8. Next Milestones for Architecture Review

## Milestone 1

* Repository Setup
* Design Documentation
* PDF Upload Module

## Milestone 2

* Text Extraction
* Chunking Pipeline
* ChromaDB Integration

## Milestone 3

* Gemini Integration
* Question Answering Pipeline
* Citation Generation

## Milestone 4

* Compare-Two-Documents Extension
* Deployment on Streamlit Cloud
* Testing and Documentation

---

# Expected Outcome

By the completion of the internship, AskMyBook will function as a complete RAG-based Question Answering System capable of:

* Understanding uploaded PDF documents
* Retrieving relevant information using semantic search
* Generating context-aware answers using LLMs
* Providing source-backed citations
* Supporting multiple document analysis and comparison

