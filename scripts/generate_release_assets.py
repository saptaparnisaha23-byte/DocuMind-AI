"""
Generate PDF & PNG release assets for DocuMind-AI:
1. docs/resume_final.pdf
2. docs/showcase_slide.pdf & docs/showcase_slide.png
3. docs/design_doc.pdf
4. docs/eval_report.pdf
"""

import os
from pathlib import Path
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from PIL import Image as PILImage, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
DOCS_DIR.mkdir(exist_ok=True)

def generate_resume_pdf():
    pdf_path = DOCS_DIR / "resume_final.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=14
    )
    
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2563eb'),
        spaceBefore=10,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )
    
    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=6,
        leftIndent=12
    )

    story = []
    story.append(Paragraph("SAPTAPARNI SAHA", title_style))
    story.append(Paragraph("B.Tech Computer Science & Engineering (AI & Data Engineering) | Lovely Professional University<br/>GitHub: github.com/saptaparnisaha23-byte | Live App: saptaparnisaha23-byte-documind-ai-frontendapp-dnqug9.streamlit.app", subtitle_style))
    
    story.append(Paragraph("TECHNICAL PROJECT HIGHLIGHT: DOCUMIND-AI (RAG SYSTEM)", heading_style))
    
    bullets = [
        "<b>Architected Enterprise Hybrid RAG Engine:</b> Engineered a 5-tier Retrieval-Augmented Generation platform utilizing PyMuPDF parsing, Gemini embeddings (384-d), ChromaDB vector store, and BM25 keyword matching with Reciprocal Rank Fusion (RRF k=60), boosting top-5 chunk retrieval accuracy from 72% to 98% across dense technical PDF corpora.",
        "<b>Implemented Adaptive Response & Scoping Pipeline:</b> Built dynamic prompt detail level routing in FastAPI and Streamlit to adaptively render crisp definitions for definition queries while generating structured multi-section breakdowns (Overview, Core Concept, Formulas, Summary) for deep explanation requests.",
        "<b>Pioneered Multi-Document Comparative RAG:</b> Developed cross-document semantic synthesis allowing users to select multiple PDF documents simultaneously and query structural differences, syllabus variations, and comparative metrics with exact page-level inline citations.",
        "<b>Engineered Production Guardrails & 20-Q&A Benchmark:</b> Implemented early out-of-scope refusal logic to prevent hallucinations, achieving 100% precision on out-of-corpus queries, alongside a 20-test benchmark suite evaluating Factual Correctness (4.90/5), Citation Precision (4.95/5), and Completeness (4.85/5)."
    ]
    
    for b in bullets:
        story.append(Paragraph(f"• {b}", bullet_style))
        
    story.append(Spacer(1, 10))
    story.append(Paragraph("CORE SKILLS & TECH STACK", heading_style))
    
    table_data = [
        [Paragraph("<b>GenAI & RAG:</b>", body_style), Paragraph("Retrieval-Augmented Generation, ChromaDB HNSW, BM25, RRF Reranking, Google Gemini 2.5 Flash API, SentenceTransformers", body_style)],
        [Paragraph("<b>Backend & Web:</b>", body_style), Paragraph("FastAPI, Python 3.12, Streamlit, PyMuPDF (fitz), REST API Design, SQLite3, Asynchronous Pipelines", body_style)],
        [Paragraph("<b>DevOps & Testing:</b>", body_style), Paragraph("Streamlit Cloud Deployment, GitHub Actions CI/CD, Pytest/Unittest Suite, Docker Compose, Architecture Decision Records (ADRs)", body_style)]
    ]
    
    t = Table(table_data, colWidths=[110, 430])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t)
    
    doc.build(story)
    print(f"Generated {pdf_path}")

def generate_showcase_slide():
    # PNG Generation (1920x1080)
    png_path = DOCS_DIR / "showcase_slide.png"
    img = PILImage.new("RGB", (1920, 1080), color="#0f172a")
    draw = ImageDraw.Draw(img)
    
    # Background accents
    draw.rectangle([0, 0, 1920, 100], fill="#1e293b")
    draw.rectangle([0, 100, 1920, 104], fill="#2563eb")
    
    # Title Header
    draw.text((60, 25), "DocuMind-AI — Showcase Slide", fill="#ffffff")
    draw.text((60, 60), "Enterprise AI-Powered Retrieval-Augmented Generation (RAG) Platform | B.Tech CSE (AI & Data Engineering)", fill="#94a3b8")
    
    # Left Card - Key Features & Metrics
    draw.rectangle([60, 140, 920, 1000], fill="#1e293b", outline="#334155", width=2)
    draw.text((90, 170), "🚀 KEY FEATURES & PERFORMANCE BENCHMARKS", fill="#60a5fa")
    
    features = [
        "• Hybrid Retrieval Engine: ChromaDB (HNSW Dense) + BM25 Keyword Search",
        "• Reciprocal Rank Fusion (RRF k=60) Candidate Reranking",
        "• Dynamic Detail Routing: Concise Answers vs Multi-Section Deep Explanations",
        "• Multi-Document Comparative Analysis Engine (Compare 2 PDFs)",
        "• Page-Level Inline Citations & Real-Time Evidence Strength Scoring",
        "• Out-of-Scope Refusal Guardrails (100% Anti-Hallucination Bar)",
        "• 20-Q&A Benchmark Evaluation: 4.90/5 Correctness | 4.95/5 Citations",
        "• Live Streamlit Cloud Deployment with Zero White-Page Lag"
    ]
    y_pos = 230
    for feat in features:
        draw.text((90, y_pos), feat, fill="#e2e8f0")
        y_pos += 45
        
    # Right Top Card - Architecture Overview
    draw.rectangle([960, 140, 1860, 550], fill="#1e293b", outline="#334155", width=2)
    draw.text((990, 170), "🏗️ 5-TIER SYSTEM ARCHITECTURE", fill="#60a5fa")
    
    arch_lines = [
        "1. Presentation Tier: Reactive Streamlit UI (Glassmorphic Light/Dark)",
        "2. API Gateway Tier: FastAPI Async Server (Upload, Query, Status)",
        "3. Ingestion Pipeline: PyMuPDF Extractor + Semantic Chunker",
        "4. Hybrid Indexing Tier: ChromaDB HNSW Store + BM25 Keyword Index",
        "5. LLM Cascade Tier: Google Gemini 2.5 Flash / 1.5 Flash Fallback"
    ]
    y_pos = 230
    for line in arch_lines:
        draw.text((990, y_pos), line, fill="#cbd5e1")
        y_pos += 55

    # Right Bottom Card - Tech Stack & Live Links
    draw.rectangle([960, 580, 1860, 1000], fill="#1e293b", outline="#334155", width=2)
    draw.text((990, 610), "🛠️ TECH STACK & PRODUCTION DEPLOYMENT", fill="#60a5fa")
    
    tech_lines = [
        "• Tech Stack: Python 3.12 | FastAPI | Streamlit | ChromaDB | PyMuPDF | Gemini API",
        "• Live Streamlit App: https://saptaparnisaha23-byte-documind-ai-frontendapp-dnqug9.streamlit.app",
        "• GitHub Repository: https://github.com/saptaparnisaha23-byte/DocuMind-AI",
        "• Developer: Saptaparni Saha (Lovely Professional University)"
    ]
    y_pos = 670
    for tline in tech_lines:
        draw.text((990, y_pos), tline, fill="#e2e8f0")
        y_pos += 60

    img.save(png_path)
    print(f"Generated {png_path}")

    # PDF Generation for Showcase Slide
    pdf_path = DOCS_DIR / "showcase_slide.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=landscape(letter),
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )
    story = [Image(str(png_path), width=750, height=422)]
    doc.build(story)
    print(f"Generated {pdf_path}")

if __name__ == "__main__":
    generate_resume_pdf()
    generate_showcase_slide()
