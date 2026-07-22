from app.retrieve import retrieve_chunks, collection
from google import genai
from dotenv import load_dotenv
import os
import traceback
import re
import time
import json
from pathlib import Path
from app.memory import (
    get_history,
    add_message,
    get_retrieval_memory,
    save_retrieval_memory,
)

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def is_conversational(text):
    text_clean = re.sub(r'[^\w\s]', '', text.lower().strip())
    greetings = {"hi", "hello", "hey", "hola", "who are you", "what is your name", "greetings", "good morning", "good afternoon", "good evening", "help", "thanks", "thank you"}
    return text_clean in greetings

def triage_user_query(history, question, documents_list):
    docs_pool = ", ".join(documents_list) if documents_list else "None"
    history_str = ""
    for msg in history[-6:]:
        role = msg["role"]
        content = msg["content"]
        if "||CITATIONS||" in content:
            content = content.split("||CITATIONS||")[0]
        history_str += f"{role}: {content}\n"
        
    prompt = f"""
    Analyze the recent conversation history and the student's latest follow-up question.
    You must classify the user's query intent, identify the specific query type, identify the active topic, determine if the user has switched subjects/topics, and generate a standalone rewritten search query.
    
    Uploaded documents list: [{docs_pool}]
    
    Conversation History:
    {history_str}
    
    Student's Latest Question:
    {question}
    
    PRONOUN & CONTEXT RESOLUTION RULES:
    1. Resolve all pronouns/references (e.g. "this", "that", "these", "those", "them", "it", "first one", "second one", "former", "latter", "previous one") to their concrete names/documents from the conversation history.
    2. Comparison context preservation: If the history discussed a comparison between A and B (e.g. MTH176 and MTH178) and the follow-up asks "What changed?", rewrite it to: "What changed between A and B?".
    3. Diagram-specific rewriting: If the student asks to "explain the graph" or "explain the figure", rewrite it to target the active topic (e.g. "Explain the graph associated with Polynomial Regression").
    
    CLASSIFICATION RULES:
    - INTENT: Choose one of:
      1. "Follow-up" (asking for more examples, formula, advantages, explanation of the active topic).
      2. "New Topic" (explicitly asking about a new concept, like switching from OLS to Sets, or starting a new topic).
      3. "Document Task" (requesting MCQs, notes, exam summaries, or syllabus outlines).
      4. "General Knowledge" (asking questions completely unrelated to the course documents).
      
    - QUERY TYPE: Classify the specific query style:
      1. "definition": Student wants a definition, meaning, or brief concept description.
      2. "comparison": Student wants comparison, difference, or comparison table.
      3. "summary": Student wants a summary, overview, or bullet-point synopsis.
      4. "formula": Student wants mathematical equations, expressions, derivations, or formulas.
      5. "mcq": Student requests MCQs, quizzes, or is asking/answering options.
      6. "viva": Student requests viva prep, oral test questions, or interactive study.
      7. "notes": Student requests study notes, outlines, or curriculum revision.
      8. "explanation": Student requests detailed conceptual explanation.
      9. "general": General search/queries.
      
    - ACTIVE TOPIC: Identify the main subject of discussion (e.g. "OLS", "Sets"). If the intent is "New Topic", identify the new topic.
    - REWRITTEN QUERY: Formulate a standalone query that replaces relative pronouns ("it", "this", "explain more") with concrete names.
    - TARGET PDF HINT: Identify if one of the uploaded documents matches the active topic (e.g. if topic is Sets and a math pdf exists in the list, hint that pdf).
    
    Respond ONLY with a valid JSON object matching this structure:
    {{
      "intent": "Follow-up" | "New Topic" | "Document Task" | "General Knowledge",
      "query_type": "definition" | "comparison" | "summary" | "formula" | "mcq" | "viva" | "notes" | "explanation" | "general",
      "active_topic": "topic name",
      "active_subject": "subject area",
      "rewritten_query": "standalone search query",
      "target_pdf_hint": "filename.pdf or null",
      "reason_for_topic_switch": "reason statement",
      "reason_for_document_selection": "reason statement"
    }}
    Do not add markdown formatting, code block markers (like ```json), or any surrounding text.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt
        )
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("\n", 1)[0]
        text = text.strip()
        
        data = json.loads(text)
        return data
    except Exception as e:
        print(f"DEBUG - Triage failed: {e}")
        return {
            "intent": "New Topic",
            "query_type": "general",
            "active_topic": question,
            "active_subject": "General",
            "rewritten_query": question,
            "target_pdf_hint": None,
            "reason_for_topic_switch": "Fallback due to parser error",
            "reason_for_document_selection": "Fallback"
        }

def compute_keyword_score(query, text):
    stopwords = {"what", "is", "explain", "why", "how", "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "with", "about", "of", "it", "this", "that"}
    query_tokens = set(re.findall(r'\b\w{3,}\b', query.lower())) - stopwords
    if not query_tokens:
        return 0.0
    text_lower = text.lower()
    
    ACRONYMS = {
        "mlr": ["multiple", "linear", "regression"],
        "slr": ["simple", "linear", "regression"],
        "ols": ["ordinary", "least", "squares"],
        "mse": ["mean", "squared", "error"],
        "rmse": ["root", "mean", "squared", "error"],
        "mae": ["mean", "absolute", "error"],
        "rss": ["residual", "sum", "squares"],
    }
    for acronym, full_forms in ACRONYMS.items():
        if acronym in text_lower:
            text_lower += " " + " ".join(full_forms)
            
    matches = sum(1 for token in query_tokens if token in text_lower)
    return matches / len(query_tokens)

def is_noisy_chunk(text):
    text_clean = text.strip()
    if len(text_clean) < 40:
        return True
    if re.match(r'^\d+$', text_clean) or re.match(r'^page \d+ of \d+$', text_clean.lower()):
        return True
    return False

def compute_mmr(scored_candidates, penalty_factor=0.4):
    selected = []
    candidates = list(scored_candidates)
    
    def get_words(text):
        return set(re.findall(r'\b\w{3,}\b', text.lower()))
        
    while candidates:
        best_candidate = None
        best_index = -1
        best_mmr_score = -9999.0
        
        for i, cand in enumerate(candidates):
            cand_words = get_words(cand["doc"])
            max_overlap = 0.0
            
            for sel in selected:
                sel_words = get_words(sel["doc"])
                intersection = len(cand_words.intersection(sel_words))
                union = len(cand_words.union(sel_words))
                jaccard = intersection / union if union > 0 else 0.0
                if jaccard > max_overlap:
                    max_overlap = jaccard
            
            mmr_score = cand["score"] - (penalty_factor * max_overlap)
            cand["mmr_score"] = round(mmr_score, 4)
            
            if mmr_score > best_mmr_score:
                best_mmr_score = mmr_score
                best_candidate = cand
                best_index = i
                
        if best_candidate:
            selected.append(best_candidate)
            candidates.pop(best_index)
        else:
            break
            
    return selected

def extract_chapter_context(text, document_name):
    """Detect if chunk contains specific Chapter/Unit reference, else fallback to filename stem."""
    m = re.search(r'\b(?:chapter|unit|module|part)\s*([0-9a-zA-Z\-_]+)\b', text, re.IGNORECASE)
    if m:
        val = m.group(1)
        chapter_type = m.group(0).split()[0].capitalize()
        return f"{chapter_type} {val} ({document_name})"
    return Path(document_name).stem

def get_mcq_chunks(q_num, document=None):
    """Retrieve all chunks matching a specific MCQ question number from ChromaDB."""
    where = {"document": document} if document else None
    try:
        db_res = collection.get(
            where=where,
            where_document={"$contains": str(q_num)},
            include=["documents", "metadatas"]
        )
    except Exception:
        db_res = collection.get(
            where=where,
            include=["documents", "metadatas"]
        )
        
    qn_regex = re.compile(rf'(?:^|\n)\s*(?:(?:Question|Q|Qn|No|No\.)\s*)?{q_num}\s*[\.\):]\s*', re.IGNORECASE)
    matching_chunks = []
    
    documents = db_res.get("documents", [])
    metadatas = db_res.get("metadatas", [])
    
    for idx, text in enumerate(documents):
        if qn_regex.search(text):
            matching_chunks.append({
                "doc": text,
                "meta": metadatas[idx] if idx < len(metadatas) else {}
            })
    return matching_chunks

def group_chunks_by_chapter(chunks):
    """Group lists of chunks based on their chapter contexts."""
    grouped_matches = {}
    for match in chunks:
        text = match["doc"]
        meta = match["meta"]
        doc_name = meta.get("document", "Unknown")
        chapter = extract_chapter_context(text, doc_name)
        if chapter not in grouped_matches:
            grouped_matches[chapter] = []
        grouped_matches[chapter].append(match)
    return grouped_matches

def clean_rtl_notation(text):
    """Replace LaTeX arrow statements and Greek/Math symbols with clean Unicode counterparts, and strip math wrappers."""
    if not text:
        return text
    
    replacements = {
        # Greek letters
        r'\lambda': 'λ', r'\\lambda': 'λ',
        r'\alpha': 'α', r'\\alpha': 'α',
        r'\beta': 'β', r'\\beta': 'β',
        r'\gamma': 'γ', r'\\gamma': 'γ',
        r'\theta': 'θ', r'\\theta': 'θ',
        r'\mu': 'μ', r'\\mu': 'μ',
        r'\sigma': 'σ', r'\\sigma': 'σ',
        r'\pi': 'π', r'\\pi': 'π',
        r'\phi': 'φ', r'\\phi': 'φ',
        r'\omega': 'ω', r'\\omega': 'ω',
        r'\Delta': 'Δ', r'\\Delta': 'Δ',
        # Arrows
        r'\leftarrow': '←', r'\\leftarrow': '←',
        r'\rightarrow': '→', r'\\rightarrow': '→',
        r'\leftrightarrow': '↔', r'\\leftrightarrow': '↔',
        r'\Leftarrow': '⇐', r'\\Leftarrow': '⇐',
        r'\Rightarrow': '⇒', r'\\Rightarrow': '⇒',
        r'\to': '→', r'\\to': '→',
        # Math operations
        r'\times': '×', r'\\times': '×',
        r'\cdot': '·', r'\\cdot': '·',
        r'\leq': '≤', r'\\leq': '≤',
        r'\le': '≤', r'\\le': '≤',
        r'\geq': '≥', r'\\geq': '≥',
        r'\ge': '≥', r'\\ge': 'ge',
        r'\neq': '≠', r'\\neq': '≠',
        r'\ne': '≠', r'\\ne': '≠',
        r'\approx': '≈', r'\\approx': '≈',
        r'\in': '∈', r'\\in': '∈',
    }
    
    # Process replacements
    for lat, uni in replacements.items():
        text = text.replace(lat, uni)
        
    # Remove $ delimiters around simple math expressions (e.g. $v$ -> v, $Av = λv$ -> Av = λv)
    text = re.sub(r'\$([^$]+)\$', r'\1', text)
    
    # Strip residual double/single backslashes from unmatched LaTeX commands
    text = re.sub(r'\\([a-zA-Z]+)', r'\1', text)
    
    return text

def score_and_filter_candidates(documents, metadatas, distances, query, active_topic, target_pdf_hint):
    """Apply hybrid BM25 and Semantic Similarity scoring to retrieved chunks."""
    candidates = []
    for idx, doc in enumerate(documents):
        if is_noisy_chunk(doc):
            continue
            
        meta = metadatas[idx] if idx < len(metadatas) else {}
        dist = distances[idx] if idx < len(distances) else 1.0
        
        semantic_score = 1.0 / (1.0 + dist)
        keyword_score = compute_keyword_score(query, doc)
        
        # Hybrid score (0.5 * semantic_score + 0.5 * keyword_score)
        hybrid_score = 0.5 * semantic_score + 0.5 * keyword_score
        
        # Target PDF Boost
        meta_doc = meta.get("document")
        doc_boost = 0.0
        if target_pdf_hint and meta_doc == target_pdf_hint:
            doc_boost = 0.25
            hybrid_score += doc_boost
            
        # Topic Match Boost
        topic_boost = 0.0
        if active_topic.lower() in doc.lower():
            topic_boost = 0.1
            hybrid_score += topic_boost
            
        candidates.append({
            "doc": doc,
            "meta": meta,
            "score": round(hybrid_score, 4),
            "semantic_score": round(semantic_score, 4),
            "keyword_score": round(keyword_score, 4),
            "doc_boost": doc_boost,
            "topic_boost": topic_boost,
            "mmr_score": 0.0
        })
    return candidates

import html

def normalize_query(query):
    # Remove common introductory questions/phrases to ensure consistent retrieval
    q = query.strip().lower()
    # Strip punctuation at the end
    q = re.sub(r'[?.!,;:]+$', '', q)
    # Strip common prefixes
    prefixes = [
        r'^\s*(?:what\s+is\s+a|what\s+is\s+an|what\s+is|what\s+are|what\s+do\s+you\s+mean\s+by|what\s+does|what\s+do)\b',
        r'^\s*(?:define\s+the|define\s+a|define\s+an|define)\b',
        r'^\s*(?:explain\s+the|explain\s+a|explain\s+an|explain\s+in\s+detail|explain)\b',
        r'^\s*(?:tell\s+me\s+about\s+the|tell\s+me\s+about\s+a|tell\s+me\s+about|tell\s+me)\b',
        r'^\s*(?:give\s+me\s+details\s+on\s+the|give\s+me\s+details\s+on|give\s+me\s+an\s+example\s+of|give\s+me)\b',
        r'^\s*(?:can\s+you\s+explain|can\s+you\s+tell\s+me|can\s+you\s+define)\b'
    ]
    for pattern in prefixes:
        q = re.sub(pattern, '', q).strip()
    return q if q else query

def classify_evidence_strength(similarity_pct):
    if similarity_pct >= 85:
        return "High"
    elif similarity_pct >= 60:
        return "Medium"
    else:
        return "Low"

def identify_mentioned_documents(query, documents_list):
    matched = []
    q_lower = query.lower()
    for doc in documents_list:
        stem = Path(doc).stem.lower()
        # Replace underscores, dashes and non-alphanumeric with spaces to avoid \w+ greedy matching
        clean_stem_text = re.sub(r'[^a-zA-Z0-9]', ' ', stem)
        stem_words = clean_stem_text.split()
        
        # Match explicit course codes (e.g. MTH176, CSE211, CSR304)
        course_codes = re.findall(r'\b[a-zA-Z]{2,4}\d{3,4}\b', clean_stem_text)
        if course_codes:
            if any(code in q_lower for code in course_codes):
                matched.append(doc)
                continue
                
        # Match exact stem name or clean stem words
        clean_stem = " ".join(stem_words)
        if clean_stem in q_lower or stem in q_lower or stem.split()[0] in q_lower:
            matched.append(doc)
            continue
            
        # Match significant overlapping keywords (e.g., Computer Networks, Operating Systems)
        ignored_stem_words = {"unit", "syllabus", "pdf", "2026", "2025", "2024", "doc", "document", "chapter", "lecture", "07", "01"}
        meaningful_stem_words = [w for w in stem_words if w not in ignored_stem_words and len(w) > 2]
        
        if meaningful_stem_words and all(w in q_lower for w in meaningful_stem_words):
            matched.append(doc)
            
    return list(set(matched))

def extract_preview_with_highlights(text, query):
    # 1. Clean query to get keywords
    stopwords = {"what", "is", "explain", "why", "how", "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "with", "about", "of", "it", "this", "that"}
    query_tokens = set(re.findall(r'\b\w{3,}\b', query.lower())) - stopwords
    
    # 2. Split chunk text into logical sentences safely
    raw_sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = []
    temp_sent = ""
    abbreviations = {"eg.", "ie.", "fig.", "etc.", "no.", "q.", "ans.", "vs."}
    
    for rs in raw_sentences:
        if temp_sent:
            temp_sent += " " + rs
        else:
            temp_sent = rs
        
        last_word = temp_sent.split()[-1].lower() if temp_sent.split() else ""
        # Clean last word punctuation for matching
        last_word_clean = re.sub(r'[^\w\.]', '', last_word)
        if last_word_clean in abbreviations:
            continue
        else:
            sentences.append(temp_sent)
            temp_sent = ""
            
    if temp_sent:
        sentences.append(temp_sent)
    
    if not sentences or not query_tokens:
        preview = text[:250] + ("..." if len(text) > 250 else "")
        return html.escape(preview)
        
    # 3. Find the sentence with the highest keyword overlap (best match)
    best_sent_idx = 0
    max_overlap = -1
    
    for idx, sent in enumerate(sentences):
        sent_words = set(re.findall(r'\b\w{3,}\b', sent.lower()))
        overlap = len(query_tokens.intersection(sent_words))
        if overlap > max_overlap:
            max_overlap = overlap
            best_sent_idx = idx
            
    # 4. Include the best match, along with one preceding and one succeeding sentence for context
    start_idx = max(0, best_sent_idx - 1)
    end_idx = min(len(sentences) - 1, best_sent_idx + 1)
    
    selected_sentences = sentences[start_idx:end_idx + 1]
    
    # 5. Highlight matching query terms inside the selected sentences
    highlighted_list = []
    for sent in selected_sentences:
        sent_words = set(re.findall(r'\b\w{3,}\b', sent.lower()))
        overlap_tokens = query_tokens.intersection(sent_words)
        
        escaped_sent = html.escape(sent.strip())
        if overlap_tokens:
            for term in sorted(list(overlap_tokens), key=len, reverse=True):
                pattern = re.compile(rf'\b({re.escape(term)})\b', re.IGNORECASE)
                escaped_sent = pattern.sub(
                    r'<mark style="background:rgba(254, 240, 138, 0.4); color:inherit; padding:0 2px; border-radius:2px; font-weight:600;">\1</mark>',
                    escaped_sent
                )
        highlighted_list.append(escaped_sent)
        
    preview_html = " ".join(highlighted_list)
    
    if start_idx > 0 or end_idx < len(sentences) - 1:
        if start_idx > 0:
            preview_html = "... " + preview_html
        if end_idx < len(sentences) - 1:
            preview_html = preview_html + " ..."
            
    return preview_html


def merge_adjacent_chunks(candidates):
    if not candidates:
        return []
        
    groups = {}
    for cand in candidates:
        meta = cand["meta"]
        doc = meta.get("document", "Unknown")
        page = meta.get("page", 1)
        key = (doc, page)
        if key not in groups:
            groups[key] = []
        groups[key].append(cand)
        
    merged_candidates = []
    
    for key, group in groups.items():
        doc, page = key
        group.sort(key=lambda x: x["meta"].get("chunk", 0))
        
        current_merged = None
        for cand in group:
            if current_merged is None:
                current_merged = cand.copy()
                current_merged["merged_chunks"] = [cand["meta"].get("chunk", 0)]
                current_merged["original_cands"] = [cand]
            else:
                last_chunk_idx = current_merged["merged_chunks"][-1]
                curr_chunk_idx = cand["meta"].get("chunk", 0)
                
                if curr_chunk_idx - last_chunk_idx == 1:
                    current_merged["doc"] += "\n\n" + cand["doc"]
                    current_merged["merged_chunks"].append(curr_chunk_idx)
                    current_merged["original_cands"].append(cand)
                    current_merged["score"] = max(current_merged["score"], cand["score"])
                    current_merged["semantic_score"] = max(current_merged["semantic_score"], cand["semantic_score"])
                    current_merged["keyword_score"] = max(current_merged["keyword_score"], cand["keyword_score"])
                else:
                    merged_candidates.append(current_merged)
                    current_merged = cand.copy()
                    current_merged["merged_chunks"] = [cand["meta"].get("chunk", 0)]
                    current_merged["original_cands"] = [cand]
                    
        if current_merged:
            merged_candidates.append(current_merged)
            
    merged_candidates.sort(key=lambda x: x["score"], reverse=True)
    return merged_candidates

def ask_question(session_id, question, document=None):
    """
    Process a user's question using Retrieval-Augmented Generation (RAG).
    """
    start_time = time.time()
    question = question.strip()

    fallback_answer = (
        "This topic was not found in the uploaded documents.\n\n"
        "To ensure factual accuracy, I only answer using information contained in the uploaded PDFs.\n\n"
        "Upload a document containing this topic if you would like me to answer it."
    )

    if not question:
        return {
            "success": False,
            "answer": "Please enter a question.",
            "sources": [],
            "confidence": 0,
            "debug": None
        }

    if len(question) < 3:
        return {
            "success": False,
            "answer": "Please enter a more meaningful question.",
            "sources": [],
            "confidence": 0,
            "debug": None
        }

    try:
        history = get_history(session_id)
        retrieval_mem = get_retrieval_memory(session_id)
        
        topic_before = "None"
        for message in reversed(history):
            if message["role"].lower() == "assistant" and "||DEBUG||" in message["content"]:
                try:
                    debug_part = message["content"].split("||DEBUG||", 1)[1]
                    debug_data = json.loads(debug_part)
                    topic_before = debug_data.get("active_topic", "None")
                    break
                except Exception:
                    pass

        try:
            db_res = collection.get(include=["metadatas"])
            docs_set = set(m.get("document") for m in db_res.get("metadatas", []) if m)
            documents_list = list(docs_set)
        except Exception:
            documents_list = []

        # 1. Intent Triage and Query Rewriting via Gemini
        triage = triage_user_query(history, question, documents_list)
        intent = triage.get("intent", "New Topic")
        
        # If the user switches topic, clear previous context
        if intent == "New Topic":
            retrieval_mem["compared_documents"] = []
            retrieval_mem["documents"] = []
            retrieval_mem["chapter"] = None
            retrieval_mem["page"] = None
            save_retrieval_memory(session_id, retrieval_mem)
            
        query_type = triage.get("query_type", "general")
        active_topic = triage.get("active_topic", question)
        active_subject = triage.get("active_subject", "General")
        rewritten_query = triage.get("rewritten_query", question)
        target_pdf_hint = triage.get("target_pdf_hint")
        
        reason_topic_switch = triage.get("reason_for_topic_switch", "None")
        reason_doc_selection = triage.get("reason_for_document_selection", "None")

        comparison_docs = identify_mentioned_documents(question, documents_list)
        
        # Restore comparison context in case of follow-ups
        if not comparison_docs and intent == "Follow-up" and len(retrieval_mem.get("compared_documents", [])) >= 2:
            comparison_docs = retrieval_mem["compared_documents"]

        if (query_type == "comparison" or "compare" in question.lower() or "difference" in question.lower() or "change" in question.lower()):
            if document and document not in comparison_docs:
                comparison_docs.append(document)
            if len(comparison_docs) < 2:
                for doc_name in documents_list:
                    if doc_name not in comparison_docs:
                        comparison_docs.append(doc_name)
                    if len(comparison_docs) >= 2:
                        break

        is_example_request = False
        if intent == "Follow-up":
            low_question = question.lower()
            trigger_words = {"example", "analogy", "simplify", "simplification", "real life", "scenario", "metaphor", "explain like", "eli5", "illustrate"}
            if any(word in low_question for word in trigger_words):
                is_example_request = True

        # 2. MCQ Specific Question Number Search
        q_num_match = re.search(r'\b(?:question|qn|q\.?|no\.?|number)\s*(?:no\.?\s*)?(\d+)\b', question, re.IGNORECASE)
        if not q_num_match and re.match(r'^\s*(\d+)\s*$', question):
            q_num_match = re.match(r'^\s*(\d+)\s*$', question)

        q_num = q_num_match.group(1) if q_num_match else None

        active_mcq_num = None
        for msg in reversed(history):
            content = msg["content"]
            if "||CITATIONS||" in content:
                content = content.split("||CITATIONS||")[0]
            m = re.search(r'I found multiple Question (\d+) entries', content)
            if m:
                active_mcq_num = m.group(1)
                break

        is_resolving_ambiguity = False
        matched_chapter_chunks = []

        if not q_num and active_mcq_num:
            temp_q_num = active_mcq_num
            temp_matches = get_mcq_chunks(temp_q_num, document)
            temp_groups = group_chunks_by_chapter(temp_matches)
            
            matched_key = None
            for ch in temp_groups.keys():
                if question.lower() in ch.lower() or ch.lower() in question.lower():
                    matched_key = ch
                    break
                    
            if matched_key:
                is_resolving_ambiguity = True
                matched_chapter_chunks = temp_groups[matched_key]
                q_num = temp_q_num

        if q_num and not is_resolving_ambiguity:
            matching_chunks = get_mcq_chunks(q_num, document)
            grouped_matches = group_chunks_by_chapter(matching_chunks)
            
            if len(grouped_matches) > 1:
                chapters_list = "\n".join(f"- {ch}" for ch in grouped_matches.keys())
                answer_text = f"I found multiple Question {q_num} entries.\nWhich chapter do you mean?\n\n{chapters_list}"
                
                add_message(session_id, "User", question, question if len(history) == 0 else None)
                
                latency_ms = round((time.time() - start_time) * 1000)
                debug_payload = {
                    "intent": "MCQ Ambiguity",
                    "topic_before": topic_before,
                    "topic_after": f"Question {q_num}",
                    "selected_document": document or "All",
                    "selected_chapter": "Multiple Chapters",
                    "query_rewrite": rewritten_query,
                    "top_k": 0,
                    "latency": latency_ms,
                    "reason_for_document_selection": "MCQ Match",
                    "reason_for_topic_switch": "Question number ambiguity",
                    "reason_for_retrieval_rejection": "None",
                    "retrieved_chunks": [],
                    "final_prompt_summary": "Ambiguity response generated."
                }
                
                full_content = answer_text + "||CITATIONS||[]||DEBUG||" + json.dumps(debug_payload)
                add_message(session_id, "Assistant", full_content)
                
                return {
                    "success": True,
                    "answer": answer_text,
                    "sources": [],
                    "confidence": 100,
                    "debug": debug_payload
                }
            elif len(grouped_matches) == 1:
                matched_key = list(grouped_matches.keys())[0]
                matched_chapter_chunks = grouped_matches[matched_key]

        # 3. Normalized Query for consistent retrieval across variants
        normalized_search_query = normalize_query(rewritten_query)

        # 4. Dynamic Hybrid Retrieval and Reranking
        selected_candidates = []
        if matched_chapter_chunks:
            scored_candidates = []
            for item in matched_chapter_chunks:
                text = item["doc"]
                meta = item["meta"]
                keyword_score = compute_keyword_score(normalized_search_query, text)
                
                doc_name = meta.get("document", "Unknown")
                page_num = meta.get("page", 1)
                chunk_num = meta.get("chunk", 1)
                unique_chunk_id = f"{doc_name}_page_{page_num}_chunk_{chunk_num}"
                
                scored_candidates.append({
                    "doc": text,
                    "meta": meta,
                    "score": round(1.0 + keyword_score, 4),
                    "semantic_score": 1.0,
                    "keyword_score": round(keyword_score, 4),
                    "doc_boost": 0.0,
                    "topic_boost": 0.0,
                    "mmr_score": 0.0,
                    "distance": 0.0,
                    "id": unique_chunk_id
                })
            scored_candidates.sort(key=lambda x: x["score"], reverse=True)
            mmr_ranked = compute_mmr(scored_candidates)
            selected_candidates = merge_adjacent_chunks(mmr_ranked[:3])
        else:
            # Check if this is a comparison query comparing multiple documents
            if len(comparison_docs) >= 2:
                # We will retrieve chunks from each target comparison document separately
                all_candidates = []
                seen_ids = set()
                
                # Strip names of documents from search query to make search semantic
                clean_search_query = normalized_search_query
                for doc_name in comparison_docs:
                    stem = Path(doc_name).stem
                    clean_search_query = re.sub(rf'\b{re.escape(stem)}\b', '', clean_search_query, flags=re.IGNORECASE)
                    clean_search_query = re.sub(rf'\b{re.escape(stem.split("_")[0])}\b', '', clean_search_query, flags=re.IGNORECASE)
                    clean_search_query = re.sub(rf'\b{re.escape(Path(doc_name).stem.split()[0])}\b', '', clean_search_query, flags=re.IGNORECASE)
                
                clean_search_query = clean_search_query.strip()
                if not clean_search_query:
                    clean_search_query = normalized_search_query
                    
                # Retrieve from each document
                for doc_name in comparison_docs:
                    results = retrieve_chunks(
                        question=clean_search_query,
                        top_k=12,
                        document=doc_name
                    )
                    
                    raw_documents = results.get("documents", [[]])[0]
                    raw_metadatas = results.get("metadatas", [[]])[0]
                    raw_distances = results.get("distances", [[]])[0]
                    
                    for idx, doc_text in enumerate(raw_documents):
                        meta = raw_metadatas[idx] if idx < len(raw_metadatas) else {}
                        dist = raw_distances[idx] if idx < len(raw_distances) else 1.0
                        page_num = meta.get("page", 1)
                        chunk_num = meta.get("chunk", 1)
                        unique_chunk_id = f"{doc_name}_page_{page_num}_chunk_{chunk_num}"
                        
                        if unique_chunk_id not in seen_ids:
                            seen_ids.add(unique_chunk_id)
                            all_candidates.append({
                                "doc": doc_text,
                                "meta": meta,
                                "distance": dist,
                                "id": unique_chunk_id
                            })
            else:
                # 3. Document Persistence Check: If previous turn had retrieved documents, search them first
                used_persistence = False
                prev_docs = retrieval_mem.get("documents", [])
                if intent == "Follow-up" and prev_docs and not document:
                    all_candidates = []
                    seen_ids = set()
                    for doc_name in prev_docs:
                        results = retrieve_chunks(
                            question=normalized_search_query,
                            top_k=12,
                            document=doc_name
                        )
                        raw_documents = results.get("documents", [[]])[0]
                        raw_metadatas = results.get("metadatas", [[]])[0]
                        raw_distances = results.get("distances", [[]])[0]
                        
                        for idx, doc_text in enumerate(raw_documents):
                            meta = raw_metadatas[idx] if idx < len(raw_metadatas) else {}
                            dist = raw_distances[idx] if idx < len(raw_distances) else 1.0
                            page_num = meta.get("page", 1)
                            chunk_num = meta.get("chunk", 1)
                            unique_chunk_id = f"{doc_name}_page_{page_num}_chunk_{chunk_num}"
                            
                            if unique_chunk_id not in seen_ids:
                                seen_ids.add(unique_chunk_id)
                                all_candidates.append({
                                    "doc": doc_text,
                                    "meta": meta,
                                    "distance": dist,
                                    "id": unique_chunk_id
                                })
                    # We will temporarily score candidates to see if we have any good matches.
                    # If the maximum hybrid score of these chunks is extremely low (meaning no good chunks matched), 
                    # we set used_persistence to False so it falls back to full database search.
                    if all_candidates:
                        temp_max_score = 0.0
                        for cand in all_candidates:
                            dist = cand["distance"]
                            semantic_score = 1.0 / (1.0 + dist)
                            keyword_score = compute_keyword_score(normalized_search_query, cand["doc"])
                            h_score = 0.5 * semantic_score + 0.5 * keyword_score
                            if h_score > temp_max_score:
                                temp_max_score = h_score
                        if temp_max_score >= 0.25:
                            used_persistence = True
                            
                if not used_persistence:
                    # First Pass: Semantic Search (Top 25)
                    search_doc = document if document else None
                    results = retrieve_chunks(
                        question=normalized_search_query,
                        top_k=25,
                        document=search_doc
                    )
                    
                    raw_documents = results.get("documents", [[]])[0]
                    raw_metadatas = results.get("metadatas", [[]])[0]
                    raw_distances = results.get("distances", [[]])[0]
                    
                    seen_ids = set()
                    all_candidates = []
                    
                    for idx, doc in enumerate(raw_documents):
                        meta = raw_metadatas[idx] if idx < len(raw_metadatas) else {}
                        dist = raw_distances[idx] if idx < len(raw_distances) else 1.0
                        doc_name = meta.get("document", "Unknown")
                        page_num = meta.get("page", 1)
                        chunk_num = meta.get("chunk", 1)
                        unique_chunk_id = f"{doc_name}_page_{page_num}_chunk_{chunk_num}"
                    
                        seen_ids.add(unique_chunk_id)
                        all_candidates.append({
                            "doc": doc,
                            "meta": meta,
                            "distance": dist,
                            "id": unique_chunk_id
                        })
                
            # Second Pass: Keyword/Exact Term search
            exact_terms = re.findall(r'"([^"]+)"', question)
            if q_num:
                exact_terms.append(f"question {q_num}")
                exact_terms.append(q_num)
            
            if exact_terms:
                if len(comparison_docs) >= 2:
                    for comp_doc in comparison_docs:
                        where_clause = {"document": comp_doc}
                        for term in exact_terms:
                            term_clean = term.strip()
                            if len(term_clean) < 2:
                                continue
                            try:
                                db_res = collection.get(
                                    where=where_clause,
                                    where_document={"$contains": term_clean},
                                    include=["documents", "metadatas"]
                                )
                                k_docs = db_res.get("documents", [])
                                k_metas = db_res.get("metadatas", [])
                                for k_idx, k_doc in enumerate(k_docs):
                                    k_meta = k_metas[k_idx] if k_idx < len(k_metas) else {}
                                    k_doc_name = k_meta.get("document", "Unknown")
                                    k_page_num = k_meta.get("page", 1)
                                    k_chunk_num = k_meta.get("chunk", 1)
                                    k_unique_id = f"{k_doc_name}_page_{k_page_num}_chunk_{k_chunk_num}"
                                    if k_unique_id not in seen_ids:
                                        seen_ids.add(k_unique_id)
                                        all_candidates.append({
                                            "doc": k_doc,
                                            "meta": k_meta,
                                            "distance": 0.5,
                                            "id": k_unique_id
                                        })
                            except Exception:
                                pass
                else:
                    where_clause = {"document": document} if document else None
                    for term in exact_terms:
                        term_clean = term.strip()
                        if len(term_clean) < 2:
                            continue
                        try:
                            db_res = collection.get(
                                where=where_clause,
                                where_document={"$contains": term_clean},
                                include=["documents", "metadatas"]
                            )
                            k_docs = db_res.get("documents", [])
                            k_metas = db_res.get("metadatas", [])
                            for k_idx, k_doc in enumerate(k_docs):
                                k_meta = k_metas[k_idx] if k_idx < len(k_metas) else {}
                                k_doc_name = k_meta.get("document", "Unknown")
                                k_page_num = k_meta.get("page", 1)
                                k_chunk_num = k_meta.get("chunk", 1)
                                k_unique_id = f"{k_doc_name}_page_{k_page_num}_chunk_{k_chunk_num}"
                                if k_unique_id not in seen_ids:
                                    seen_ids.add(k_unique_id)
                                    all_candidates.append({
                                        "doc": k_doc,
                                        "meta": k_meta,
                                        "distance": 0.5,
                                        "id": k_unique_id
                                    })
                        except Exception:
                            pass
                        
            # Dynamic weighting based on intent
            if query_type in ("mcq", "formula", "definition"):
                w_semantic, w_keyword = 0.4, 0.6
            elif query_type in ("summary", "notes", "explanation"):
                w_semantic, w_keyword = 0.7, 0.3
            else:
                w_semantic, w_keyword = 0.5, 0.5
                
            # Compute Hybrid Scores & Boosts
            for cand in all_candidates:
                doc = cand["doc"]
                dist = cand["distance"]
                meta = cand["meta"]
                
                semantic_score = 1.0 / (1.0 + dist)
                keyword_score = compute_keyword_score(normalized_search_query, doc)
                hybrid_score = w_semantic * semantic_score + w_keyword * keyword_score
                
                doc_boost = 0.0
                meta_doc = meta.get("document")
                if target_pdf_hint and meta_doc == target_pdf_hint:
                    doc_boost = 0.25
                    hybrid_score += doc_boost
                    
                topic_boost = 0.0
                if active_topic.lower() in doc.lower():
                    topic_boost = 0.15
                    hybrid_score += topic_boost
                    
                # Adaptive Context and Retrieval Memory Boosts
                mem_doc_boost = 0.0
                prev_docs = retrieval_mem.get("documents", [])
                if prev_docs and meta_doc in prev_docs:
                    mem_doc_boost = 0.20
                    hybrid_score += mem_doc_boost
                    
                proximity_boost = 0.0
                prev_page = retrieval_mem.get("page")
                curr_page = meta.get("page")
                if prev_page is not None and curr_page is not None:
                    try:
                        if abs(int(curr_page) - int(prev_page)) <= 1:
                            proximity_boost = 0.15
                            hybrid_score += proximity_boost
                    except Exception:
                        pass
                        
                chapter_boost = 0.0
                prev_chapter = retrieval_mem.get("chapter")
                curr_chapter = extract_chapter_context(doc, meta_doc)
                if prev_chapter and curr_chapter and prev_chapter.lower() == curr_chapter.lower():
                    chapter_boost = 0.10
                    hybrid_score += chapter_boost
                    
                cand["score"] = round(hybrid_score, 4)
                cand["semantic_score"] = round(semantic_score, 4)
                cand["keyword_score"] = round(keyword_score, 4)
                cand["doc_boost"] = doc_boost
                cand["topic_boost"] = topic_boost
                cand["mmr_score"] = 0.0
                
            # Rerank & MMR
            # Sort candidates preferring highest score, semantic score, and nearest page
            def candidate_sort_key(cand):
                score = cand["score"]
                sem_score = cand.get("semantic_score", 0.0)
                meta = cand["meta"]
                prev_p = retrieval_mem.get("page")
                curr_p = meta.get("page")
                try:
                    p_dist = abs(int(curr_p) - int(prev_p)) if (prev_p is not None and curr_p is not None) else 9999
                except Exception:
                    p_dist = 9999
                return (-score, -sem_score, p_dist)
                
            all_candidates.sort(key=candidate_sort_key)
            mmr_ranked = compute_mmr(all_candidates)
            
            # Select target candidate size based on intent
            target_size = 6 if query_type in ("summary", "notes", "explanation") else 4
            top_ranked = mmr_ranked[:target_size]
            
            # Merge contiguous adjacent chunks on same page
            selected_candidates = merge_adjacent_chunks(top_ranked)

        # Early out-of-scope validation
        out_of_scope = False
        is_conv = is_conversational(question)
        max_final_score = max([x["score"] for x in selected_candidates]) if selected_candidates else 0.0
        
        if not is_conv and max_final_score < 0.25 and not is_example_request:
            out_of_scope = True
            
        if len(comparison_docs) >= 2:
            out_of_scope = False
            
        if out_of_scope:
            title = question if len(history) == 0 else None
            add_message(session_id, "User", question, title)
            
            latency_ms = round((time.time() - start_time) * 1000)
            debug_payload = {
                "intent": intent,
                "query_type": query_type,
                "topic_before": topic_before,
                "topic_after": active_topic,
                "selected_document": document or "All / Multi-PDF Search",
                "selected_chapter": active_subject,
                "query_rewrite": rewritten_query,
                "top_k": len(selected_candidates),
                "latency": latency_ms,
                "reason_for_document_selection": reason_doc_selection,
                "reason_for_topic_switch": reason_topic_switch,
                "reason_for_retrieval_rejection": f"Context weak (max score {max_final_score} < 0.25). Rejected to prevent hallucination.",
                "retrieved_chunks": [],
                "final_prompt_summary": "Grounding failed. Returned fallback statement."
            }
            
            full_content = fallback_answer + "||CITATIONS||[]||DEBUG||" + json.dumps(debug_payload)
            add_message(session_id, "Assistant", full_content)
            
            return {
                "success": True,
                "answer": fallback_answer,
                "sources": [],
                "confidence": 0,
                "debug": debug_payload
            }

        # 5. Build prompt context and citations
        context_parts = []
        for idx, item in enumerate(selected_candidates):
            doc_name = item["meta"].get("document", "Unknown Document")
            page_num = item["meta"].get("page", "Unknown Page")
            snippet = item["doc"]
            context_parts.append(f"=== [Chunk {idx + 1}] (Source: {doc_name}, Page {page_num}) ===\n{snippet}")
            
        context = "\n\n".join(context_parts)
        
        confidence = 100
        if selected_candidates:
            avg_score = sum(x["score"] for x in selected_candidates) / len(selected_candidates)
            confidence = min(100, max(0, round(avg_score * 100)))

        conversation = ""
        for message in history[-6:]:
            content = message['content']
            if "||CITATIONS||" in content:
                content = content.split("||CITATIONS||")[0]
            conversation += f"{message['role']}: {content}\n"

        # Diagram mode detection
        diagram_keywords = {"graph", "figure", "flowchart", "architecture", "image", "table", "diagram"}
        has_diagram_keyword = any(word in question.lower() or word in rewritten_query.lower() for word in diagram_keywords)
        has_diagram_chunk = False
        for item in selected_candidates:
            doc_text = item["doc"].lower()
            if any(word in doc_text for word in diagram_keywords):
                has_diagram_chunk = True
                break
                
        diagram_mode = has_diagram_keyword or has_diagram_chunk
        
        diagram_instructions = ""
        if diagram_mode:
            diagram_instructions = """
            DIAGRAM EXPLANATION MODE IS ACTIVE:
            The context contains or refers to a diagram, graph, figure, table, flowchart, or architecture. You MUST structure your answer to explicitly explain:
            - What the figure/diagram shows
            - The X-axis and Y-axis labels and ranges (if it is a graph)
            - The meaning of any curves, points, shapes, or rows
            - Step-by-step interpretation of the diagram
            - Practical exam takeaways or key formulas associated with it
            Do not list every graph/figure in the document; only explain the specific one relevant to the retrieval.
            """
            
        simple_explanation_keywords = {"explain simply", "explain like i'm 10", "easy words", "simple explanation", "eli5", "analogy", "example", "simplification"}
        is_simple_explanation = any(word in question.lower() for word in simple_explanation_keywords) or is_example_request
        
        analogy_instructions = ""
        if is_simple_explanation:
            analogy_instructions = """
            SIMPLE EXPLANATION & ANALOGY MODE ACTIVE:
            1. First, provide a clear, grounded explanation of the concept based ONLY on the retrieved document chunks.
            2. Then, provide a creative, easy-to-understand analogy or example from everyday life to simplify the concept.
            3. You MUST clearly separate the analogy from the grounded facts by using the exact heading:
               🤖 Simple Analogy (Generated by AI)
               (Not from the uploaded document)
               [Insert analogy here]
            4. Never mix or blend the analogy text with the grounded citation-backed explanation. Keep them strictly separate.
            """

        # 6. Prompt Engineering
        prompt = f"""
        You are DocuMind-AI, an expert AI Grounding Tutor. Your absolute priority is accuracy, grounding, textbook-quality writing, and providing clean, compact, exam-oriented responses.
        
        Retrieved Context from Uploaded Documents:
        {context}
        
        Conversation History:
        {conversation}
        
        Student's Question:
        {question}
        
        {diagram_instructions}
        {analogy_instructions}
        
        STRICT GROUNDING INSTRUCTIONS:
        1. Always answer from the retrieved context first. Never hallucinate or rely on outside knowledge when grounding is enabled.
        2. If the topic, subject, or keywords of the question are completely absent from the retrieved chunks (i.e. the query is completely out-of-scope):
           - You MUST output EXACTLY:
             "This topic was not found in the uploaded documents.
             
             To ensure factual accuracy, I only answer using information contained in the uploaded PDFs.
             
             Upload a document containing this topic if you would like me to answer it."
           - Do not output anything else.
           - NOTE: Conversational greetings/general chat queries (like "hello", "hi", "how are you") are exceptions; answer them conversationally and keep it short.
        3. For every fact you state that comes from a specific context chunk, append `[Citation X]` at the end of the sentence (where X is the 1-based index of the chunk, e.g. [Citation 1], [Citation 2]). If multiple chunks are referenced, list them all, e.g. [Citation 1][Citation 2]. Do not create your own citations or reference anything not in the context.
        4. If a retrieved context chunk contains descriptions of diagrams, charts, flowcharts, or architecture, describe the components, flow, connections, and structure instead of repeating the neighboring text verbatim.
        5. Write in an academic textbook prose style: use clear paragraphs, logical transitions, consistent terminology, and proper formatting. Avoid sounding robotic.
           
        ADAPTIVE LAYOUT TEMPLATES:
        Choose the formatting structure matching the student's request:
        
        - [REQUESTS FOR EXAMPLES / ANALOGIES / SIMPLIFICATIONS / SCENARIOS]:
          If the student asks for another example, analogy, simplification, or scenario of the active concept/topic:
          1. You are explicitly authorized to generate this example/analogy/scenario using your general knowledge, rather than replying "This topic was not found...".
          2. You MUST clearly label the generated content as:
             🤖 AI Illustration
             (Not from the uploaded document)
             [analogy/illustration text]
          3. Continue citing the original document/page for the underlying concept at the bottom: "Source: [Document Name] - Page [Page Number] (Concept)".
          4. Keep the explanation concise and easy to understand. Do not mix AI-generated illustrations with grounded facts.
          
        - [SIMPLE QUESTIONS / DEFINITIONS] (e.g. "What is OLS?", "What is eigenvalue?", "Define deadlock"):
          Output a clean, compact 2–4 line explanation with important keywords in bold.
          At the bottom, append EXACTLY: "Source: [Document Name] - Page [Page Number]".
          Do NOT use any structural headers (no `📘 Overview`, no `🧠 Core Concept`, etc.) to keep it clean and compact.
          
        - [COMPARISON / DIFFERENCES]:
          Compare the terms using a clean markdown table. Include columns like Feature, Concept A, and Concept B. Highlight key differences in bold.
          At the bottom, append: "Source: [Document Name] - Page [Page Number]".
          Do NOT use structural headers unless detailed explanations are requested.
          Include rows whenever relevant: Definition, Formula, Advantages, Disadvantages, Feature Selection, Use Cases, Real-world Example, Memory Trick (optional). Only include rows relevant to the topic.
          CRITICAL: If any values inside the table cells contain absolute value bars or pipe symbols (e.g. '|beta|' or '|x|'), you MUST escape them as '\\|' (e.g., '\\|beta\\|') so they do not break the markdown table columns.
          
        - [SUMMARY REQUESTS]:
          Return a concise list of bullet points highlighting key conditions, rules, or takeaways.
          At the bottom, append: "Source: [Document Name] - Page [Page Number]".
          Do NOT use structural headers unless detailed notes are requested.
          
        - [MCQ QUESTIONS]:
          Return EXACTLY this format:
          Correct Option: [Option letter, e.g. b]
          Correct Answer: [Option content, e.g. R1 ← R2]
          Short Explanation: [1-2 sentences maximum, explaining why the option is correct based on the context]
          Source: [Document Name] - Page [Page Number]
          Do NOT use structural headers.
          
        - ["EXPLAIN" / "DETAILED NOTES" / "EXAM PREP" REQUESTS]:
          Use the custom structured template to display visual styled boxes:
          
          📘 Overview
          [Brief high-level overview of the concept/topic]
          
          🧠 Core Concept
          [Grounded academic definition and description of the core concept]
          
          ⚙️ How it Works
          [Step-by-step mechanism or flow of operation]
          
          🛠️ Important Components
          [Break down of key structures, components, or parts]
          
          📝 Detailed Explanation
          [In-depth discussion, wrap code/syntax in backticks.]
          
          📌 Summary
          - [Bullet points of key textbook takeaways]
          
          📚 Source
          - [Document Name] (Page [Page Number])
          
          Note: Only include an illustration section (`🤖 AI Illustration` formatted as above) if it genuinely improves understanding.
        """

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt
        )
        
        raw_answer = response.text.strip()
        clean_answer = clean_rtl_notation(raw_answer)
        
        # 7. Citation Post-Processing & Validation
        cited_indices_str = re.findall(r'\[Citation (\d+)\]', clean_answer)
        cited_indices = sorted(list(set(int(x) for x in cited_indices_str)))
        
        if not cited_indices and selected_candidates:
            for idx, item in enumerate(selected_candidates):
                words = set(re.findall(r'\b\w{4,}\b', item["doc"].lower()))
                answer_words = set(re.findall(r'\b\w{4,}\b', clean_answer.lower()))
                if len(words.intersection(answer_words)) >= 3:
                    cited_indices.append(idx + 1)
            if not cited_indices:
                cited_indices.append(1)
                
        formatted_sources = []
        new_citation_map = {}
        
        for new_idx, old_idx in enumerate(cited_indices, start=1):
            if old_idx <= len(selected_candidates):
                item = selected_candidates[old_idx - 1]
                meta = item["meta"]
                doc_name = meta.get("document", "Unknown Document")
                page_num = meta.get("page", "Unknown Page")
                snippet = item["doc"]
                
                score_val = item.get("score", 0.8)
                similarity_pct = min(100, max(40, round(score_val * 100)))
                confidence_pct = min(100, max(40, round(item.get("semantic_score", score_val) * 100)))
                
                # Evidence strength categorization instead of raw confidence percentage
                evidence_strength = classify_evidence_strength(similarity_pct)
                
                chunk_id = item.get("id") or f"{doc_name}_page_{page_num}_chunk_{meta.get('chunk', 1)}"
                preview_html = extract_preview_with_highlights(snippet, normalized_search_query)
                
                formatted_sources.append({
                    "document": doc_name,
                    "page": page_num,
                    "chunk": meta.get("chunk", 1),
                    "chunk_id": chunk_id,
                    "content": snippet,
                    "preview": preview_html,
                    "confidence": confidence_pct,
                    "similarity": similarity_pct,
                    "evidence_strength": evidence_strength,
                    "rank": new_idx
                })
                
                new_citation_map[old_idx] = new_idx

        # Replace [Citation X] with [Y] in the answer text
        for old_idx, new_idx in new_citation_map.items():
            clean_answer = clean_answer.replace(f"[Citation {old_idx}]", f" [{new_idx}]")
            
        clean_answer = re.sub(r'\[Citation \d+\]', '', clean_answer)
        
        title = question if len(history) == 0 else None
        add_message(session_id, "User", question, title)

        latency_ms = round((time.time() - start_time) * 1000)
        debug_payload = {
            "intent": intent,
            "topic_before": topic_before,
            "topic_after": active_topic,
            "selected_document": document or "All / Multi-PDF Search",
            "selected_chapter": active_subject,
            "query_rewrite": rewritten_query,
            "top_k": len(formatted_sources),
            "latency": latency_ms,
            "reason_for_document_selection": reason_doc_selection,
            "reason_for_topic_switch": reason_topic_switch,
            "reason_for_retrieval_rejection": f"MMR and citation validation selected {len(formatted_sources)} chunks.",
            "retrieved_chunks": [
                {
                    "id": item.get("id", "Unknown"),
                    "chunk_text": item["doc"],
                    "score": item["score"],
                    "semantic_score": item.get("semantic_score", 0.0),
                    "keyword_score": item.get("keyword_score", 0.0),
                    "doc_boost": item.get("doc_boost", 0.0),
                    "topic_boost": item.get("topic_boost", 0.0),
                    "mmr_score": item.get("mmr_score", 0.0),
                    "document": item["meta"].get("document", "Unknown"),
                    "page": item["meta"].get("page", "Unknown")
                }
                for item in selected_candidates
            ],
            "final_prompt_summary": prompt[:450] + "..."
        }

        citations_str = json.dumps(formatted_sources)
        debug_str = json.dumps(debug_payload)
        full_content = clean_answer + "||CITATIONS||" + citations_str + "||DEBUG||" + debug_str

        # Update and save retrieval memory
        last_doc_names = list(set(src["document"] for src in formatted_sources if "document" in src))
        if len(comparison_docs) >= 2:
            retrieval_mem["compared_documents"] = comparison_docs
        else:
            retrieval_mem["compared_documents"] = []
            
        retrieval_mem["documents"] = last_doc_names
        retrieval_mem["topic"] = active_topic
        
        if formatted_sources:
            retrieval_mem["page"] = formatted_sources[0]["page"]
            retrieval_mem["chapter"] = extract_chapter_context(formatted_sources[0]["content"], formatted_sources[0]["document"])
            
        save_retrieval_memory(session_id, retrieval_mem)

        add_message(session_id, "Assistant", full_content)

        return {
            "success": True,
            "answer": clean_answer,
            "sources": formatted_sources,
            "confidence": confidence,
            "debug": debug_payload
        }

    except Exception:
        traceback.print_exc()
        return {
            "success": False,
            "answer": "An unexpected error occurred.",
            "sources": [],
            "confidence": 0,
            "debug": None
        }