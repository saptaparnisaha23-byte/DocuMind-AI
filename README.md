# 📚 DocuMind-AI: Intelligent Document Q&A System (RAG)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://saptaparnisaha23-byte-documind-ai-frontendapp-dnqug9.streamlit.app/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-red.svg)](https://www.trychroma.com/)
[![Google Gemini](https://img.shields.io/badge/LLM-Google%20Gemini-orange.svg)](https://ai.google.dev/)

An AI-powered Retrieval-Augmented Generation (RAG) Document Question-Answering System that enables users to upload PDF documents, perform hybrid vector & keyword retrieval, and generate accurate, grounded answers using Google Gemini with source citations and interactive PDF previews.

🔗 **Live Application URL**: [https://saptaparnisaha23-byte-documind-ai-frontendapp-dnqug9.streamlit.app/](https://saptaparnisaha23-byte-documind-ai-frontendapp-dnqug9.streamlit.app/)  
📂 **GitHub Repository**: [https://github.com/saptaparnisaha23-byte/DocuMind-AI](https://github.com/saptaparnisaha23-byte/DocuMind-AI)

---

## 🌟 Key Features

- 🌐 **Live Web Application**: Responsive Streamlit dashboard with custom dark/light theme switching, glassmorphic design, and instant chat sidebar.
- 📄 **Dynamic Document Ingestion & Management**: Upload multiple PDF documents, automatically extract text via PyMuPDF, and split into semantic chunks.
- 🧠 **Hybrid RAG & Reciprocal Rank Fusion (RRF)**: Combines dense vector search (`all-MiniLM-L6-v2` + ChromaDB) with sparse keyword matching and ML/SLR/OLS acronym expansion.
- 🤖 **Google Gemini Integration**: Context-grounded response generation to eliminate LLM hallucinations.
- 📌 **Interactive Source Citations & PDF Preview**: Inspect retrieved passages with confidence scores and view downloadable PDF page references.
- 🔐 **Authentication & Session History**: User sign-in/registration system, chat session history, persistent SQLite storage, and chat renaming.
- ⚡ **Dual Architecture Support**: Seamless integration between FastAPI backend (`app/main.py`) and Streamlit frontend with automatic standalone fallback.

---

## 📌 Project Information

| Item | Details |
|------|---------|
| **Project Name** | DocuMind-AI |
| **Problem Statement** | I2 – Document Q&A (RAG over a Focused Corpus) |
| **Segment** | Foundations of Applied Machine Learning |
| **Internship** | Summer Internship 2026 |
| **Developer** | Saptaparni Saha (B.Tech – AI & Data Engineering, LPU) |
| **Live App URL** | [Streamlit Cloud Demo](https://saptaparnisaha23-byte-documind-ai-frontendapp-dnqug9.streamlit.app/) |
| **GitHub Repository** | [saptaparnisaha23-byte/DocuMind-AI](https://github.com/saptaparnisaha23-byte/DocuMind-AI) |

---

## 📖 Project Overview

DocuMind-AI addresses the challenge of exploring, searching, and querying complex unstructured PDF documents. Rather than passing raw full-length documents into a LLM context window, DocuMind-AI uses a Retrieval-Augmented Generation (RAG) architecture:

1. **PDF Text Extraction**: Extracts clean text and metadata page by page using PyMuPDF (`fitz`).
2. **Recursive Chunking**: Splits extracted text into semantic blocks using LangChain's `RecursiveCharacterTextSplitter`.
3. **Vector Embeddings**: Computes 384-dimensional dense embeddings with Sentence Transformers (`all-MiniLM-L6-v2`).
4. **Vector Storage**: Stores embeddings and metadata persistently inside ChromaDB.
5. **Hybrid Retrieval**: Queries vector similarity alongside keyword candidate scoring and RRF reranking.
6. **LLM Generation**: Feeds retrieved passages to Google Gemini to construct precise, factual answers with source citations.

---

## 🏗️ System Architecture

```
                       ┌─────────────────────────┐
                       │      PDF Document       │
                       └────────────┬────────────┘
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │ PyMuPDF Text Extraction │
                       └────────────┬────────────┘
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │  Recursive Text Chunks  │
                       └────────────┬────────────┘
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │ Sentence Transformers   │
                       │   (all-MiniLM-L6-v2)    │
                       └────────────┬────────────┘
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │  ChromaDB Vector Store  │
                       └────────────┬────────────┘
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │ Hybrid RAG & RRF Search │
                       └────────────┬────────────┘
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │ Google Gemini Answer Gen│
                       └────────────┬────────────┘
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │  Streamlit App UI &     │
                       │   Source Citations      │
                       └─────────────────────────┘
```

---

## 📂 Project Structure

```
DocuMind-AI/
│
├── app/                        # Core Backend & RAG Pipeline
│   ├── app.py                  # Streamlit entry point (or legacy runner)
│   ├── auth.py                 # User authentication logic
│   ├── chatbot.py              # Gemini RAG chain & prompt template
│   ├── database.py            # SQLite session & chat database
│   ├── embed.py                # Embedding generation & ChromaDB store
│   ├── ingest.py               # PDF extraction & chunking
│   ├── main.py                 # FastAPI REST API backend
│   ├── retrieve.py             # Hybrid vector & RRF retrieval engine
│   └── test_gemini.py          # Gemini API test suite
│
├── frontend/                   # Web Application Interface
│   ├── app.py                  # Main Streamlit web application
│   ├── utilis.py               # API communication & standalone fallback
│   ├── components/             # Modular UI components
│   │   ├── auth.py             # Login & Registration views
│   │   ├── home.py             # Landing page & quick actions
│   │   ├── sidebar.py          # Sidebar navigation & theme toggle
│   │   └── upload.py           # Knowledge base upload interface
│   └── styles/                 # Custom CSS stylesheets
│       ├── main.css            # Dark/Light mode theme system
│       └── sidebar.css         # Modern sidebar styles
│
├── .streamlit/                 # Streamlit cloud & local configuration
│   └── config.toml             # Custom theme colors & settings
│
├── data/                       # Document storage directory
│   └── pdfs/                   # Uploaded PDF files
│
├── docs/                       # Project documentation & ADRs
│   ├── adr/                    # Architecture Decision Records
│   └── design_doc.md           # System design specification
│
├── tests/                      # Automated test scripts
├── requirements.txt            # Python dependencies
├── README.md                   # Project README documentation
└── .gitignore                  # Git ignore definitions
```

---

## 🛠 Tech Stack

| Component | Technology Used |
|-----------|-----------------|
| **Frontend UI** | Streamlit, Custom HTML5/CSS3 (Glassmorphism, Dark/Light mode) |
| **Backend API** | FastAPI, Uvicorn |
| **PDF Extraction** | PyMuPDF (`fitz`) |
| **Text Chunking** | LangChain `RecursiveCharacterTextSplitter` |
| **Embeddings** | Sentence Transformers (`all-MiniLM-L6-v2`) |
| **Vector Database** | ChromaDB |
| **LLM Provider** | Google Gemini (`gemini-2.5-flash` / `gemini-1.5-flash`) |
| **Session DB** | SQLite3 |
| **Deployment** | Streamlit Cloud |

---

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.10 or higher
- Google Gemini API Key ([Get an API key](https://aistudio.google.com/))

### 1. Clone Repository

```bash
git clone https://github.com/saptaparnisaha23-byte/DocuMind-AI.git
cd DocuMind-AI
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
PORT=8000
```

---

## 🚀 Running the Application

### Option A: Launch Streamlit Web UI (Frontend)

To run the full Streamlit interface (which automatically supports standalone RAG mode if the backend server is offline):

```bash
streamlit run frontend/app.py
```

Open your browser at `http://localhost:8501`.

### Option B: Launch FastAPI Backend Server

```bash
uvicorn app.main:app --reload --port 8000
```

Access the interactive API docs at `http://localhost:8000/docs`.

---

## 📊 Internship Milestones & Progress

| Feature / Task | Status |
|----------------|--------|
| GitHub Repository & Project Structure | ✅ Completed |
| System Architecture & Design Document | ✅ Completed |
| PyMuPDF PDF Text Extraction | ✅ Completed |
| Recursive Character Text Chunking | ✅ Completed |
| Sentence Transformers Embeddings | ✅ Completed |
| ChromaDB Vector Storage | ✅ Completed |
| Hybrid Retrieval & Reciprocal Rank Fusion | ✅ Completed |
| Google Gemini API Integration | ✅ Completed |
| End-to-End Terminal RAG Pipeline | ✅ Completed |
| Streamlit Web App Interface | ✅ Completed |
| Interactive Dark/Light Theme Switching | ✅ Completed |
| Source Citations & PDF Page Preview | ✅ Completed |
| Multi-Document Upload & Knowledge Base Management | ✅ Completed |
| FastAPI REST Backend & API Integration | ✅ Completed |
| Cloud Deployment on Streamlit Cloud | ✅ Deployed |

---

## 👩‍💻 Author & Credits

**Saptaparni Saha**  
B.Tech – Artificial Intelligence & Data Engineering  
Lovely Professional University  
Summer Internship 2026  
Problem Statement: **I2 – Document Q&A (RAG over a Focused Corpus)**

---

## 📄 License

This project is open-source and developed for educational & research purposes under the Summer Internship 2026.
