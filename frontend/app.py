import streamlit as st
import uuid
from pathlib import Path
import sys
import requests
import importlib
import html
from urllib.parse import quote, unquote

# Make sure project root is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Initialize local SQLite database schema for standalone deployments
from app.database import initialize_database
initialize_database()


PROJECT_ROOT = Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = PROJECT_ROOT / "uploads"

import frontend.config as config
import frontend.components.sidebar as sidebar
import frontend.components.home as home
import frontend.components.upload as upload
import frontend.api as api
import frontend.utilis as utilis

from frontend.config import configure_page
from frontend.components.sidebar import render_sidebar
from frontend.components.home import render_home
from frontend.components.upload import render_upload
from frontend.api import (
    get_documents,
    get_chats,
    get_chat,
    upload_documents,
    ask_question,
    delete_chat,
    delete_document_api,
    BASE_URL,
    STANDALONE_MODE,
)

def escape_js_string(text):
    return text.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r")

def _safe(value):
    return html.escape(str(value or ""), quote=True)

def highlight_search_terms(text, query):
    if not query:
        return text
    import re
    stopwords = {"what", "is", "explain", "why", "how", "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "with", "about", "of", "it", "this", "that"}
    tokens = set(re.findall(r'\b\w{3,}\b', query.lower())) - stopwords
    if not tokens:
        return text
    sorted_tokens = sorted(list(tokens), key=len, reverse=True)
    highlighted = text
    for token in sorted_tokens:
        pattern = re.compile(rf'\b({re.escape(token)})\b', re.IGNORECASE)
        highlighted = pattern.sub(r'<mark style="background:rgba(254, 240, 138, 0.4); color:inherit; padding:0 2px; border-radius:2px; font-weight:600;">\1</mark>', highlighted)
    return highlighted

def render_assistant_response(text):
    try:
        from markdown_it import MarkdownIt
        md = MarkdownIt().enable('table')
    except Exception:
        return f"<p>{text}</p>"
    
    mapping = [
        ("📘 Overview", "Overview"),
        ("🧠 Core Concept", "CoreConcept"),
        ("⚙️ How it Works", "HowItWorks"),
        ("🛠️ Important Components", "Components"),
        ("📝 Detailed Explanation", "DetailedExplanation"),
        ("📌 Summary", "Summary"),
        ("🤖 AI Illustration", "AIIllustration"),
        ("📘 Topic", "Topic"),
        ("📄 According to your uploaded document", "Grounding"),
        ("🧠 Explanation", "Explanation"),
        ("💡 Example", "Example"),
        ("📌 Key Points", "KeyPoints"),
        ("📝 Important Points", "KeyPoints"),
        ("⚠️ Common Mistakes", "Mistakes"),
        ("⚠ Common Mistakes", "Mistakes"),
        ("🎯 Exam Tips", "Tips"),
        ("📚 Source", "Source")
    ]
    
    sections = {}
    current_key = "General"
    current_content = []
    
    lines = text.split("\n")
    for line in lines:
        matched = False
        for head, key in mapping:
            if line.strip().startswith(head):
                if current_content:
                    sections[current_key] = "\n".join(current_content).strip()
                current_key = key
                current_content = []
                matched = True
                break
        if not matched:
            current_content.append(line)
            
    if current_content:
        sections[current_key] = "\n".join(current_content).strip()
        
    if len(sections) <= 1 and "General" in sections:
        return md.render(text)
    
    formatted_html = ""
    
    if "Overview" in sections:
        formatted_html += f'<div class="section-overview"><h3>📘 Overview</h3>{md.render(sections["Overview"])}</div>'
        
    if "CoreConcept" in sections:
        formatted_html += f'<div class="section-coreconcept"><h3>🧠 Core Concept</h3>{md.render(sections["CoreConcept"])}</div>'
        
    if "HowItWorks" in sections:
        formatted_html += f'<div class="section-howitworks"><h3>⚙️ How it Works</h3>{md.render(sections["HowItWorks"])}</div>'
        
    if "Components" in sections:
        formatted_html += f'<div class="section-components"><h3>🛠️ Important Components</h3>{md.render(sections["Components"])}</div>'
        
    if "DetailedExplanation" in sections:
        formatted_html += f'<div class="section-detailedexplanation"><h3>📝 Detailed Explanation</h3>{md.render(sections["DetailedExplanation"])}</div>'
        
    if "Summary" in sections:
        formatted_html += f'<div class="section-summary"><h3>📌 Summary</h3>{md.render(sections["Summary"])}</div>'
        
    if "AIIllustration" in sections:
        formatted_html += f'<div class="section-aiillustration" style="border: 1px dashed var(--accent); padding: 12px; border-radius: 8px; margin-bottom: 16px;"><h3>🤖 AI Illustration</h3><small style="opacity:0.7; display:block; margin-top:-8px; margin-bottom:8px;">(Not from the uploaded document)</small>{md.render(sections["AIIllustration"])}</div>'
        
    if "Topic" in sections:
        formatted_html += f'<div class="section-topic">📘 {sections["Topic"]}</div>'
        
    if "Grounding" in sections:
        formatted_html += f'<div class="section-grounding">📄 <strong>Grounding Context:</strong><br>{md.render(sections["Grounding"])}</div>'
        
    if "Explanation" in sections:
        formatted_html += f'<div class="section-explanation"><h3>🧠 Explanation</h3>{md.render(sections["Explanation"])}</div>'
        
    if "Example" in sections:
        formatted_html += f'<div class="section-example"><h3>💡 Example & Analogy</h3>{md.render(sections["Example"])}</div>'
        
    if "KeyPoints" in sections:
        formatted_html += f'<div class="section-keypoints"><h3>📌 Key Notes</h3>{md.render(sections["KeyPoints"])}</div>'
        
    if "Mistakes" in sections:
        formatted_html += f'<div class="section-mistakes"><h3>⚠️ Common Mistakes</h3>{md.render(sections["Mistakes"])}</div>'
        
    if "Tips" in sections:
        formatted_html += f'<div class="section-tips"><h3>🎯 Exam Tips</h3>{md.render(sections["Tips"])}</div>'
        
    if "Source" in sections:
        formatted_html += f'<div class="section-source"><h3>📚 Syllabus Source</h3>{md.render(sections["Source"])}</div>'
        
    if "General" in sections and sections["General"].strip():
        formatted_html += f'<div class="section-general">{md.render(sections["General"])}</div>'
        
    return formatted_html

@st.fragment
def render_chat_fragment(session_id, chats):
    session_id = st.session_state.session_id
    history_res = get_chat(session_id)
    messages = history_res.get("messages", [])

    col_h1, col_h2, col_h3 = st.columns([6, 1.5, 1.5])
    col_h1.subheader("💬 Chat Session")

    if col_h2.button("✏️ Rename Chat", use_container_width=True):
        st.session_state.show_rename = True

    if col_h3.button("🗑️ Delete Session", use_container_width=True):
        try:
            delete_chat(session_id)
        except Exception:
            pass
        current_theme = st.session_state.theme
        st.query_params.clear()
        st.query_params["theme"] = current_theme
        st.session_state.session_id = None
        st.session_state.page = "home"
        st.rerun()

    if st.session_state.get("show_rename"):
        current_title = "Untitled chat"
        for chat in chats:
            if chat.get("session_id") == session_id:
                current_title = chat.get("title") or "Untitled chat"
                break

        col_rename, col_act = st.columns([3, 1])
        new_title = col_rename.text_input("New Session Title", value=current_title, key="rename_title_input")
        col_save, col_cancel = col_act.columns(2)
        if col_save.button("Save"):
            if new_title.strip():
                try:
                    from app.database import get_connection
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE chat_messages
                        SET title = ?
                        WHERE session_id = ? AND id = (
                            SELECT MIN(id) FROM chat_messages WHERE session_id = ?
                        )
                    """, (new_title.strip(), session_id, session_id))
                    conn.commit()
                    conn.close()
                except Exception:
                    pass
            st.session_state.show_rename = False
            st.rerun()
        if col_cancel.button("Cancel"):
            st.session_state.show_rename = False
            st.rerun()

    st.html('<div class="chat-container">')

    auto_scroll_js = '''
    <script>
    (function() {
        const tryScroll = () => {
            requestAnimationFrame(() => {
                const mainEl = window.parent.document.querySelector('[data-testid="stMainBlockContainer"]');
                if (mainEl) {
                    mainEl.scrollTo({ top: mainEl.scrollHeight, behavior: 'smooth' });
                }
                window.parent.scrollTo({ top: window.parent.document.body.scrollHeight, behavior: 'smooth' });
            });
        };
        setTimeout(tryScroll, 250);
        setTimeout(tryScroll, 700);
    })();
    </script>
    '''
    st.html(auto_scroll_js)

    for idx, msg in enumerate(messages):
        role = msg["role"]
        content = msg["content"]

        if role.lower() == "user":
            user_msg_html = f'<div class="user-msg-bubble"><strong>You:</strong><br>{content}</div>'
            st.html(user_msg_html)
        else:
            import json
            sources_list = []
            debug_info = None

            if "||CITATIONS||" in content:
                parts = content.split("||CITATIONS||", 1)
                clean_content = parts[0]

                citations_and_debug = parts[1]
                if "||DEBUG||" in citations_and_debug:
                    sub_parts = citations_and_debug.split("||DEBUG||", 1)
                    citations_str = sub_parts[0]
                    debug_str = sub_parts[1]
                    try:
                        sources_list = json.loads(citations_str)
                    except Exception:
                        sources_list = []
                    try:
                        debug_info = json.loads(debug_str)
                    except Exception:
                        debug_info = None
                else:
                    try:
                        sources_list = json.loads(citations_and_debug)
                    except Exception:
                        sources_list = []
            else:
                clean_content = content

            body_html = render_assistant_response(clean_content)
            safe_text = _safe(clean_content)

            ai_card_html = f'''
            <div class="ai-response-card">
                <textarea class="copy-textarea" style="display:none;">{safe_text}</textarea>
                <div class="ai-response-header">
                    <div class="ai-avatar">DM</div>
                    <div class="ai-meta">
                        <div class="ai-title">DocuMind AI <span class="ai-verified-tag">Grounding Active</span></div>
                    </div>
                    <div class="ai-actions">
                        <button class="ai-action-btn copy-btn" onclick="navigator.clipboard.writeText(this.closest('.ai-response-card').querySelector('.copy-textarea').value); showCopyToast();" title="Copy response">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width: 16px; height: 16px;"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 0 1-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H5.25m11.9-3.664A2.251 2.251 0 0 0 15 2.25h-3a2.251 2.251 0 0 0-2.15 1.586m5.8 0c.065.21.1.433.1.664v.75h-6V4.5c0-.231.035-.454.1-.664M6.75 7.375c0-.621.504-1.125 1.125-1.125h9.75c.621 0 1.125.504 1.125 1.125v12.75c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 0 1-1.125-1.125V7.375Z" /></svg>
                        </button>
                        <button class="ai-action-btn like-btn" onclick="this.classList.toggle('active')" title="Like response">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width: 16px; height: 16px;"><path stroke-linecap="round" stroke-linejoin="round" d="M6.633 10.25c.806 0 1.533-.446 2.031-1.08a9.041 9.041 0 0 1 2.861-2.4c.723-.384 1.35-.956 1.653-1.715a4.498 4.498 0 0 0 .322-1.672V2.75a.75.75 0 0 1 .75-.75 2.25 2.25 0 0 1 2.25 2.25c0 1.152-.26 2.243-.723 3.218-.266.558.107 1.282.725 1.282m0 0h3.126c1.026 0 1.945.694 2.054 1.715.045.422.068.85.068 1.285a11.95 11.95 0 0 1-2.849 7.73c-.378.468-1.01.442-1.393.062L16.89 13.71c-.26-.26-.606-.41-.968-.41H9.513M9.513 13.15c0 .323-.1.644-.287.915l-1.413 2.12c-.229.344-.616.555-1.034.555H4.144a.75.75 0 0 1-.75-.75v-6.307c0-.312.18-.598.463-.728l3.693-1.684a.75.75 0 0 1 1.011.683v2.166Z" /></svg>
                        </button>
                        <button class="ai-action-btn dislike-btn" onclick="this.classList.toggle('active')" title="Dislike response">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width: 16px; height: 16px;"><path stroke-linecap="round" stroke-linejoin="round" d="M7.367 13.75c-.806 0-1.533.446-2.031 1.08a9.041 9.041 0 0 1-2.861 2.4c-.723.384-1.35.956-1.653 1.715a4.498 4.498 0 0 0-.322 1.672v.679c0 .414.336.75.75.75a2.25 2.25 0 0 0 2.25-2.25c0-1.152.26-2.243.723-3.218.266-.558-.107-1.282-.725-1.282m0 0h-3.126c-1.026 0-1.945-.694-2.054-1.715a12.137 12.137 0 0 1-.068-1.285 11.95 11.95 0 0 1 2.849-7.73c.378-.468 1.01-.442 1.393-.062L7.11 10.29c.26.26.606.41.968.41h6.409m0-1.15c0-.323.1-.644.287-.915l1.413-2.12c.229-.344.616-.555 1.034-.555h2.006c.414 0 .75.336.75.75v6.307c0 .312-.18.598-.463.728l-3.693 1.684a.75.75 0 0 1-1.011-.683V10.29Z" /></svg>
                        </button>
                    </div>
                </div>
                <div class="ai-response-body">
                    {body_html}
                </div>
            </div>
            '''
            st.html(ai_card_html)

            if st.session_state.get("developer_mode") and debug_info:
                with st.expander("🛠️ Developer Debug Panel", expanded=False):
                    st.html(f'''
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; font-size:12px; margin-bottom:12px; border-bottom:1px solid rgba(128,128,128,0.1); padding-bottom:10px;">
                        <div><strong>Intent:</strong> <span style="color:#3b82f6;">{debug_info.get("intent", "Unknown")}</span></div>
                        <div><strong>Topic Pipeline:</strong> {debug_info.get("topic_before", "None")} ➔ <span style="color:#10b981;">{debug_info.get("topic_after", "None")}</span></div>
                        <div><strong>Selected Document:</strong> {debug_info.get("selected_document", "All")}</div>
                        <div><strong>Subject Domain:</strong> {debug_info.get("selected_chapter", "General")}</div>
                        <div><strong>Rewritten Query:</strong> <em>"{debug_info.get("query_rewrite", "None")}"</em></div>
                        <div><strong>Pipeline Latency:</strong> <span style="color:#eab308;">{debug_info.get("latency", 0)} ms</span></div>
                    </div>

                    <div style="font-size:12px; font-weight:600; margin-bottom:6px;">Document Routing Details:</div>
                    <ul style="font-size:11px; margin-bottom:12px; margin-left:16px;">
                        <li><strong>Routing Reason:</strong> {debug_info.get("reason_for_document_selection", "None")}</li>
                        <li><strong>Topic Switch Reason:</strong> {debug_info.get("reason_for_topic_switch", "None")}</li>
                        <li><strong>Rejection Log:</strong> {debug_info.get("reason_for_retrieval_rejection", "None")}</li>
                    </ul>

                    <div style="font-size:12px; font-weight:600; margin-bottom:6px;">Ranked Candidate Chunks & Similarity Metrics:</div>
                    ''')

                    for chunk in debug_info.get("retrieved_chunks", []):
                        cid = chunk.get("id", "Unknown")
                        score = chunk.get("score", 0.0)
                        doc_name = chunk.get("document", "Unknown")
                        page = chunk.get("page", "Unknown")
                        text_preview = chunk.get("chunk_text", "")

                        st.html(f'''
                        <div style="font-size:11px; margin-top:8px; border-top:1px solid rgba(128,128,128,0.1); padding-top:6px; margin-bottom:4px;">
                            <strong>ID:</strong> {cid} | <strong>Doc:</strong> {doc_name} (Page {page})<br>
                            <strong>Scores:</strong> Semantic: {chunk.get("semantic_score", 0.0)} | Keywords: {chunk.get("keyword_score", 0.0)} | MMR Score: {chunk.get("mmr_score", 0.0)} | <strong>Final Hybrid Score:</strong> <span style="color:#3b82f6;">{score}</span>
                        </div>
                        ''')
                        st.text(text_preview[:400] + ("..." if len(text_preview) > 400 else ""))

                    st.markdown("**Final Prompt Snippet Preview:**")
                    st.code(debug_info.get("final_prompt_summary", ""))

            is_refusal = "This topic was not found" in clean_content or "To ensure factual accuracy" in clean_content
            if is_refusal:
                sources_list = []
                st.session_state.latest_sources = {"session_id": session_id, "sources": [], "confidence": 0}

            if not sources_list and not is_refusal and idx == len(messages) - 1:
                latest = st.session_state.get("latest_sources")
                if latest and latest.get("session_id") == session_id and latest.get("sources"):
                    sources_list = latest["sources"]

            if sources_list and not is_refusal:
                st.html("<div class='sources-header-title'>📁 Sources Used</div>")

                unique_sources = []
                seen_sources = set()
                for src in sources_list:
                    src_key = f'{src["document"]}_pg{src.get("page", 1)}'
                    if src_key not in seen_sources:
                        seen_sources.add(src_key)
                        unique_sources.append(src)

                for s_idx, src in enumerate(unique_sources):
                    fname = src["document"]
                    short_fname = fname if len(fname) <= 30 else fname[:12] + "..." + fname[-12:]
                    page = src.get("page", 1)

                    rank = src.get("rank", s_idx + 1)
                    chunk_id = src.get("chunk_id", "Unknown")
                    similarity = src.get("similarity", 92)
                    evidence_strength = src.get("evidence_strength", "Medium")

                    badge_color = "#3b82f6"
                    if evidence_strength == "High":
                        badge_color = "#10b981"
                    elif evidence_strength == "Low":
                        badge_color = "#ef4444"

                    if src.get("preview"):
                        highlighted_preview = src["preview"]
                    else:
                        content_preview = src.get("content", "No context preview available.")
                        q_term = debug_info.get("query_rewrite") if debug_info else ""
                        highlighted_preview = highlight_search_terms(content_preview[:300] + ("..." if len(content_preview) > 300 else ""), q_term)

                    with st.expander(f"[{rank}] 📄 {short_fname} — Page {page}"):
                        preview_html = f'''
                        <div class="source-card-preview" style="padding-top: 8px;">
                            <div class="source-meta-row" style="margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; font-size: 11px;">
                                <span style="background-color: {badge_color}; color: white; padding: 2px 8px; border-radius: 12px; font-weight: 600; font-size: 10px; text-transform: uppercase;">Evidence Strength: {evidence_strength}</span>
                                <span style="opacity:0.8;">Similarity: {similarity}% | Rank: #{rank}</span>
                            </div>
                            <div style="font-size: 10.5px; opacity: 0.6; margin-bottom: 12px; font-family: monospace;">Chunk ID: {chunk_id}</div>
                            <div class="source-quote" style="font-size: 13.5px; line-height: 1.6; border-left: 3px solid var(--accent); padding-left: 12px; margin-bottom: 12px; opacity:0.9;">
                                {highlighted_preview}
                            </div>
                        </div>
                        '''
                        st.html(preview_html)

                        try:
                            with open(UPLOAD_FOLDER / fname, "rb") as pdf_file:
                                pdf_data = pdf_file.read()
                            st.download_button(
                                label="📥 Open / Download Full PDF",
                                data=pdf_data,
                                file_name=fname,
                                mime="application/pdf",
                                key=f"dl_{fname}_{idx}_{s_idx}",
                                use_container_width=False
                            )
                        except Exception:
                            st.error("Unable to open full PDF document.")

    st.html('</div>')

    active_query = st.chat_input("Ask anything about your uploaded documents...", key="chat_page")
    if st.session_state.get("pending_query"):
        active_query = st.session_state.pop("pending_query")

    if active_query:
        user_msg_html = f'<div class="user-msg-bubble"><strong>You:</strong><br>{_safe(active_query)}</div>'
        st.html(user_msg_html)

        typing_placeholder = st.empty()
        typing_placeholder.html(
            '''
            <div class="ai-response-card">
                <div class="ai-response-header">
                    <div class="ai-avatar">DM</div>
                    <div class="ai-meta">
                        <div class="ai-title">DocuMind AI <span class="ai-verified-tag" style="background: var(--accent-light); color: var(--accent);">Thinking...</span></div>
                        <div class="ai-subtitle">Searching documents & formulating response...</div>
                    </div>
                </div>
                <div class="ai-response-body" style="display: flex; align-items: center; gap: 8px;">
                    <div class="typing-indicator"><span></span><span></span><span></span></div>
                    <span style="font-size: 12px; color: var(--text-secondary);">DocuMind is thinking...</span>
                </div>
            </div>
            '''
        )

        res = ask_question(
            session_id=session_id,
            question=active_query,
            document=st.session_state.active_document,
        )

        typing_placeholder.empty()

        if res.get("success"):
            res_data = res.get("data", {}) if "data" in res else res
            st.session_state.latest_sources = {
                "session_id": session_id,
                "sources": res_data.get("sources", []),
                "confidence": res_data.get("confidence", 95),
            }
        else:
            res_data = res.get("data", {}) if "data" in res else res
            st.error(res_data.get("answer") or res.get("answer") or res.get("detail") or "Failed to generate response.")

        st.rerun()

    st.html('<div class="footer-note">AI responses are grounded using your uploaded documents.</div>')

# Configure page config first
configure_page()

# Initialize default session state attributes safely at top level
if "session_id" not in st.session_state:
    st.session_state["session_id"] = None
if "page" not in st.session_state:
    st.session_state["page"] = "home"
if "active_document" not in st.session_state:
    st.session_state["active_document"] = None
if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"
if "pending_query" not in st.session_state:
    st.session_state["pending_query"] = None
if "show_rename" not in st.session_state:
    st.session_state["show_rename"] = False

query_params = st.query_params

# Theme handling
if "theme" in query_params:
    st.session_state.theme = query_params["theme"]
elif "theme" not in st.session_state:
    st.session_state.theme = "dark"

# Developer mode handling
if "dev" in query_params:
    st.session_state.developer_mode = (query_params["dev"].lower() == "true")
elif "developer_mode" not in st.session_state:
    st.session_state.developer_mode = False

bg_color = "#f8f9fb" if st.session_state.theme == "light" else "#0a0e14"
text_color = "#0f172a" if st.session_state.theme == "light" else "#e6edf3"

# ── CRITICAL: Dynamic Theme-Aware Anti-flash CSS injected FIRST before rendering ──
_anti_flash_css = f'''
<style>
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="stHeader"],
[data-testid="stSidebar"],
[data-testid="stBottom"],
[data-testid="stBottomBlockContainer"],
section.main {{
    background-color: {bg_color} !important;
    color: {text_color} !important;
}}

/* Hide Streamlit native loading/skeleton elements that flash white */
[data-testid="stAppViewBlockContainer"] > div:empty,
.stDeployButton,
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stToolbar"],
header[data-testid="stHeader"],
#MainMenu, footer {{
    display: none !important;
    visibility: hidden !important;
}}

/* Smooth page fade-in instead of jarring pop-in */
.stApp {{
    animation: _docuMindFadeIn 0.2s ease-out;
}}
@keyframes _docuMindFadeIn {{
    from {{ opacity: 0; }}
    to {{ opacity: 1; }}
}}

/* Hide native sidebar to prevent flash (we use custom HTML sidebar) */
section[data-testid="stSidebar"] {{
    display: none !important;
}}
</style>
'''
st.markdown(_anti_flash_css, unsafe_allow_html=True)

# Theme detection (localStorage sync without hard browser redirects)
theme_detector_js = '''
<script>
(function() {
    try {
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('theme')) {
            localStorage.setItem('documind-theme', urlParams.get('theme'));
        }
    } catch(e) {}
})();
</script>
'''
st.html(theme_detector_js)

from urllib.parse import urlencode

# Dialog and modal handlers from query parameters
if "confirm_delete_doc" in query_params:
    doc_to_delete = query_params["confirm_delete_doc"]
    
    cancel_params = {"theme": st.session_state.theme}
    for k in ["session_id", "document", "page"]:
        if k in query_params and k != "confirm_delete_doc":
            cancel_params[k] = query_params[k]
    cancel_href = "/?" + urlencode(cancel_params)
    delete_href = f"/?theme={st.session_state.theme}&delete_doc={doc_to_delete}"
    
    confirm_modal_html = f'''
    <div class="modal-backdrop" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: rgba(0,0,0,0.65); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 999999;">
        <div style="background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 24px; width: 400px; box-shadow: var(--shadow-lg); font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                <h3 style="margin: 0; font-size: 16px; font-weight: 600; color: var(--text-primary);">Delete PDF?</h3>
                <a href="{cancel_href}" target="_self" style="background: none; border: none; font-size: 20px; cursor: pointer; color: var(--text-secondary); text-decoration: none; line-height: 1; padding: 0 4px;">&times;</a>
            </div>
            <p style="font-size: 13.5px; color: var(--text-secondary); line-height: 1.5; margin: 0 0 24px 0;">
                This removes the document from the knowledge base and deletes its embeddings.
            </p>
            <div style="display: flex; justify-content: flex-end; gap: 12px;">
                <a href="{cancel_href}" target="_self" style="background-color: transparent; border: 1px solid var(--border-color); color: var(--text-primary); padding: 8px 16px; border-radius: 6px; font-size: 13px; font-weight: 500; cursor: pointer; text-decoration: none; display: inline-block; line-height: 1.5;">Cancel</a>
                <a href="{delete_href}" target="_self" style="background-color: #f85149; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; text-decoration: none; display: inline-block; line-height: 1.5;">Delete</a>
            </div>
        </div>
    </div>
    '''
    st.html(confirm_modal_html)
    st.stop()

if "view_details_doc" in query_params:
    doc_name = query_params["view_details_doc"]
    
    cancel_params = {"theme": st.session_state.theme}
    for k in ["session_id", "document", "page"]:
        if k in query_params and k != "view_details_doc":
            cancel_params[k] = query_params[k]
    cancel_href = "/?" + urlencode(cancel_params)
    
    pages_str = "0"
    size_str = "Unknown"
    upload_time = "Unknown"
    last_mod_str = "Unknown"
    
    try:
        from frontend.components.sidebar import get_doc_metadata
        meta = get_doc_metadata(doc_name)
        pages = meta.get("pages", 0)
        pages_str = f"{pages}"
        size_str = meta.get("size", "Unknown")
        upload_time = meta.get("upload_time", "Unknown")
        last_mod_str = meta.get("last_modified", "Unknown")
    except Exception:
        pass
        
    is_active = (doc_name == st.session_state.get("active_document"))
    status_text = "🟢 Active Scope" if is_active else "⚪ Available Library File"
    
    details_modal_html = f'''
    <div class="modal-backdrop" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: rgba(0,0,0,0.65); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 999999;">
        <div style="background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 24px; width: 440px; box-shadow: var(--shadow-lg); font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; border-bottom: 1px solid var(--border-color); padding-bottom: 12px;">
                <h3 style="margin: 0; font-size: 16px; font-weight: 600; color: var(--text-primary); display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 20px;">📄</span> Document Details
                </h3>
                <a href="{cancel_href}" target="_self" style="background: none; border: none; font-size: 20px; cursor: pointer; color: var(--text-secondary); text-decoration: none; line-height: 1; padding: 0 4px;">&times;</a>
            </div>
            <div style="display: flex; flex-direction: column; gap: 14px; margin-bottom: 24px;">
                <div>
                    <span style="font-size: 11px; text-transform: uppercase; color: var(--text-secondary); font-weight: 600; letter-spacing: 0.5px; display: block; margin-bottom: 4px;">Filename</span>
                    <div style="font-size: 13.5px; font-weight: 600; color: var(--text-primary); word-break: break-all;">{doc_name}</div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                    <div>
                        <span style="font-size: 11px; text-transform: uppercase; color: var(--text-secondary); font-weight: 600; letter-spacing: 0.5px; display: block; margin-bottom: 4px;">Pages</span>
                        <div style="font-size: 13.5px; font-weight: 500; color: var(--text-primary);">{pages_str} pages</div>
                    </div>
                    <div>
                        <span style="font-size: 11px; text-transform: uppercase; color: var(--text-secondary); font-weight: 600; letter-spacing: 0.5px; display: block; margin-bottom: 4px;">File Size</span>
                        <div style="font-size: 13.5px; font-weight: 500; color: var(--text-primary);">{size_str}</div>
                    </div>
                </div>
                <div>
                    <span style="font-size: 11px; text-transform: uppercase; color: var(--text-secondary); font-weight: 600; letter-spacing: 0.5px; display: block; margin-bottom: 4px;">Upload Date</span>
                    <div style="font-size: 13.5px; font-weight: 500; color: var(--text-primary);">{upload_time}</div>
                </div>
                <div>
                    <span style="font-size: 11px; text-transform: uppercase; color: var(--text-secondary); font-weight: 600; letter-spacing: 0.5px; display: block; margin-bottom: 4px;">Last Modified</span>
                    <div style="font-size: 13.5px; font-weight: 500; color: var(--text-primary);">{last_mod_str}</div>
                </div>
                <div>
                    <span style="font-size: 11px; text-transform: uppercase; color: var(--text-secondary); font-weight: 600; letter-spacing: 0.5px; display: block; margin-bottom: 4px;">Status</span>
                    <div style="font-size: 13px; font-weight: 600; color: var(--text-primary);">{status_text}</div>
                </div>
            </div>
            <div style="display: flex; justify-content: flex-end;">
                <a href="{cancel_href}" target="_self" style="background-color: var(--accent); color: white; border: none; padding: 8px 18px; border-radius: 6px; font-size: 12.5px; font-weight: 600; text-decoration: none; display: inline-block; line-height: 1.5;">Close</a>
            </div>
        </div>
    </div>
    '''
    st.html(details_modal_html)
    st.stop()

# Action handling from query parameters
if "delete_doc" in query_params:
    doc_to_delete = query_params["delete_doc"]
    delete_res = delete_document_api(doc_to_delete)
    if delete_res.get("success"):
        st.toast(f"🗑️ Deleted document {doc_to_delete}")
    else:
        st.toast(f"Failed to delete document: {delete_res.get('detail', 'Unknown error')}")
    current_theme = st.session_state.theme
    st.query_params.clear()
    st.query_params["theme"] = current_theme
    st.rerun()

if "rename_doc" in query_params:
    st.session_state.renaming_doc = query_params["rename_doc"]
    current_theme = st.session_state.theme
    st.query_params.clear()
    st.query_params["theme"] = current_theme
    st.rerun()

if "pin_chat" in query_params:
    pin_id = query_params["pin_chat"]
    if "pinned_chats" not in st.session_state:
        st.session_state.pinned_chats = set()
    if pin_id in st.session_state.pinned_chats:
        st.session_state.pinned_chats.remove(pin_id)
    else:
        st.session_state.pinned_chats.add(pin_id)
    current_theme = st.session_state.theme
    st.query_params.clear()
    st.query_params["theme"] = current_theme
    if st.session_state.get("session_id"):
        st.query_params["session_id"] = st.session_state.session_id
    st.rerun()

if "delete_chat" in query_params:
    chat_to_delete = query_params["delete_chat"]
    try:
        delete_chat(chat_to_delete)
        st.toast("🗑️ Chat session deleted.")
    except Exception:
        pass
    current_theme = st.session_state.theme
    st.query_params.clear()
    st.query_params["theme"] = current_theme
    if st.session_state.get("session_id") == chat_to_delete:
        st.session_state.session_id = None
        st.session_state.page = "home"
    st.rerun()

if "rename_chat" in query_params:
    st.session_state.show_rename = True
    st.session_state.session_id = query_params["rename_chat"]
    st.session_state.page = "chat"
    current_theme = st.session_state.theme
    st.query_params.clear()
    st.query_params["theme"] = current_theme
    st.query_params["session_id"] = st.session_state.session_id
    st.rerun()

if "query" in query_params:
    query_val = unquote(query_params["query"])
    new_session_id = str(uuid.uuid4())
    st.session_state.session_id = new_session_id
    st.session_state.page = "chat"
    st.session_state.pending_query = query_val
    current_theme = st.session_state.theme
    st.query_params.clear()
    st.query_params["session_id"] = new_session_id
    st.query_params["theme"] = current_theme
    st.rerun()

# Document Scope Handling (Preserved in st.session_state across all reruns)
if "active_document" not in st.session_state:
    st.session_state.active_document = None

if "document" in query_params:
    doc_val = query_params["document"]
    if doc_val == "CLEAR" or not doc_val:
        st.session_state.active_document = None
    else:
        st.session_state.active_document = doc_val

# Page / Session Routing Handling
if "session_id" in query_params:
    st.session_state.page = "chat"
    st.session_state.session_id = query_params["session_id"]
elif "page" in query_params:
    st.session_state.page = query_params["page"]
    if query_params["page"] == "home" and "session_id" not in query_params:
        st.session_state.session_id = None
else:
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "session_id" not in st.session_state:
        st.session_state.session_id = None

if "upload_success" in st.session_state:
    st.toast(st.session_state.pop("upload_success"), icon="✅")

if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

if "show_rename" not in st.session_state:
    st.session_state.show_rename = False

# Load CSS Styles (Cached)
@st.cache_data(show_spinner=False)
def load_css_styles_cached(theme):
    base_dir = Path(__file__).parent
    styles_dir = base_dir / "styles"
    css_content = ""

    anim_css_path = styles_dir / "animations.css"
    if anim_css_path.exists():
        css_content += anim_css_path.read_text(encoding="utf-8") + "\n"

    app_css_path = styles_dir / "app.css"
    if app_css_path.exists():
        css_content += app_css_path.read_text(encoding="utf-8") + "\n"

    theme_css_path = styles_dir / f"{theme}.css"
    if theme_css_path.exists():
        css_content += theme_css_path.read_text(encoding="utf-8") + "\n"

    return css_content

st.markdown(f"<style>{load_css_styles_cached(st.session_state.theme)}</style>", unsafe_allow_html=True)

# Pre-load embedding model in a background thread at startup to prevent lag on first query without blocking initial render
if "model_preloaded" not in st.session_state:
    st.session_state.model_preloaded = True
    import threading
    def bg_preload():
        try:
            from app.retrieve import get_model
            get_model()
        except Exception:
            pass
    threading.Thread(target=bg_preload, daemon=True).start()

# Hidden file uploader to support the chat input attachment button
st.html('<div class="hidden-uploader-trigger"></div>')
st.file_uploader(
    "Upload PDF manuals",
    type=["pdf"],
    accept_multiple_files=True,
    key="chat_uploader",
    label_visibility="collapsed",
)

# Auto-upload processor if files are selected from chat attachment uploader
if st.session_state.get("chat_uploader"):
    files = st.session_state.chat_uploader
    with st.spinner("Processing & Ingesting attached documents..."):
        try:
            res = upload_documents(files)
            if res.get("success"):
                st.session_state["upload_success"] = "Document(s) attached and indexed successfully!"
                st.session_state.chat_uploader = []
                st.rerun()
            else:
                st.error(res.get("detail", "Error processing documents."))
        except Exception as e:
            st.error(f"Upload failed: {e}")

# Standalone Mode status flag
is_active = not STANDALONE_MODE

# Fetch Dynamic Data
try:
    docs_res = get_documents()
    documents = docs_res.get("documents", [])
except Exception:
    documents = []

try:
    chats_res = get_chats()
    chats = chats_res.get("chats", [])
except Exception:
    chats = []

# Render Sidebar via st.html()
render_sidebar(
    documents=documents,
    chats=chats,
    active_session_id=st.session_state.get("session_id"),
    current_page=st.session_state.get("page", "home"),
    current_theme=st.session_state.get("theme", "dark"),
    active_document=st.session_state.get("active_document"),
)

# Theme toggle button metadata for top-right header
current_theme = st.session_state.get("theme", "dark")

light_params = "theme=light"
dark_params = "theme=dark"
if "page" in query_params:
    light_params += f"&page={query_params['page']}"
    dark_params += f"&page={query_params['page']}"
if "document" in query_params:
    light_params += f"&document={query_params['document']}"
    dark_params += f"&document={query_params['document']}"
if "session_id" in query_params:
    light_params += f"&session_id={query_params['session_id']}"
    dark_params += f"&session_id={query_params['session_id']}"
if st.session_state.get("developer_mode"):
    light_params += "&dev=true"
    dark_params += "&dev=true"

light_href = f"/?{light_params}"
dark_href = f"/?{dark_params}"

light_active = "active-segment" if current_theme == "light" else ""
dark_active = "active-segment" if current_theme == "dark" else ""

# Developer toggle params
next_dev_val = "false" if st.session_state.get("developer_mode") else "true"
dev_toggle_params = f"theme={current_theme}&dev={next_dev_val}"
if "page" in query_params:
    dev_toggle_params += f"&page={query_params['page']}"
if "document" in query_params:
    dev_toggle_params += f"&document={query_params['document']}"
if "session_id" in query_params:
    dev_toggle_params += f"&session_id={query_params['session_id']}"

dev_active_class = "active" if st.session_state.get("developer_mode") else ""

js_script = '''
<script>
(function() {
    let insertAttempts = 0;
    const maxAttempts = 30;
    const intervalId = setInterval(() => {
        insertAttempts++;
        const parentDoc = window.parent.document;
        const chatInput = parentDoc.querySelector('div[data-testid="stChatInput"] textarea')?.parentElement;
        if (chatInput && !chatInput.querySelector('.paperclip-btn')) {
            const link = parentDoc.createElement('a');
            link.className = 'paperclip-btn';
            link.style.cursor = 'pointer';
            link.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width: 18px; height: 18px; transform: rotate(45deg);"><path stroke-linecap="round" stroke-linejoin="round" d="m18.375 12.739-7.693 7.693a4.5 4.5 0 0 1-6.364-6.364l10.94-10.94A3 3 0 1 1 19.5 7.372L8.551 18.32m.009-.01-.01.01m0 0L21.75 3" /></svg>`;
            
            link.style.display = 'flex';
            link.style.alignItems = 'center';
            link.style.justifyContent = 'center';
            link.style.marginLeft = '8px';
            link.style.marginRight = '2px';
            link.style.alignSelf = 'center';
            link.style.order = '-1';
            
            link.onclick = (e) => {
                e.preventDefault();
                const fileInput = parentDoc.querySelector('div:has(.hidden-uploader-trigger) + div input[type="file"]');
                if (fileInput) {
                    fileInput.click();
                }
            };
            
            chatInput.insertBefore(link, chatInput.firstChild);
            clearInterval(intervalId);
        } else if (insertAttempts >= maxAttempts) {
            clearInterval(intervalId);
        }
    }, 500);
})();
</script>
'''

topbar_html = f'''
<div class="top-header">
    <div class="status-badge-pill">
        <span class="dot-green"></span>
        <span class="status-model-name">Gemini 2.5 Flash</span>
        <span class="status-separator">•</span>
        <span class="status-badge-subtitle">Enterprise AI Assistant</span>
    </div>
    <div class="header-actions">
        <!-- Segmented Theme Toggle -->
        <div class="theme-segmented-control">
            <a href="{light_href}" target="_self" class="theme-segment {light_active}">
                ☀️ Light
            </a>
            <a href="{dark_href}" target="_self" class="theme-segment {dark_active}">
                🌙 Dark
            </a>
        </div>
    </div>
</div>
<div id="copyToast" class="copy-toast">✓ Copied to clipboard</div>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<script>
function showCopyToast() {{
    const toast = document.getElementById('copyToast');
    if (toast) {{
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 2000);
    }}
}}
</script>
''' + js_script

# Document renaming inline dialog handler
if st.session_state.get("renaming_doc"):
    st.html(topbar_html)
    old_doc = st.session_state.renaming_doc
    
    st.html(f'''
    <div class="ai-response-card" style="max-width: 600px; margin: 40px auto;">
        <div class="ai-response-header">
            <div class="ai-avatar">✏️</div>
            <div class="ai-meta">
                <div class="ai-title">Rename Document</div>
                <div class="ai-subtitle">Enter a new name for your file. This keeps ChromaDB synchronized.</div>
            </div>
        </div>
        <div class="ai-response-body">
    ''')
    
    new_doc_name = st.text_input("New Name (must end with .pdf)", value=old_doc, key="rename_doc_text_input")
    
    c1, c2 = st.columns(2)
    if c1.button("Save Name", use_container_width=True, type="primary"):
        new_doc_name = new_doc_name.strip()
        if new_doc_name and new_doc_name.lower().endswith(".pdf") and new_doc_name != old_doc:
            old_path = UPLOAD_FOLDER / old_doc
            new_path = UPLOAD_FOLDER / new_doc_name
            if old_path.exists():
                try:
                    import shutil
                    # Copy to new name
                    shutil.copy(old_path, new_path)
                    if STANDALONE_MODE:
                        from app.ingest import ingest_pdf
                        ingest_res = ingest_pdf(new_path)
                        if ingest_res.get("filename"):
                            delete_document_api(old_doc)
                            st.toast("📄 Document renamed and re-indexed successfully!")
                        else:
                            st.error("Rename ingestion failed.")
                            if new_path.exists():
                                new_path.unlink()
                    else:
                        # Upload renamed file contents to sync vector database
                        with open(new_path, "rb") as f:
                            upload_res = requests.post(
                                f"{BASE_URL}/upload",
                                files=[("files", (new_doc_name, f, "application/pdf"))]
                            ).json()
                        
                        if upload_res.get("success"):
                            # Delete original file
                            delete_document_api(old_doc)
                            st.toast("📄 Document renamed and re-indexed successfully!")
                        else:
                            st.error(upload_res.get("detail", "Rename upload failed."))
                            if new_path.exists():
                                new_path.unlink()
                except Exception as e:
                    st.error(f"Error during renaming: {e}")
            else:
                st.error("Original file not found in uploads folder.")
        st.session_state.renaming_doc = None
        st.rerun()
        
    if c2.button("Cancel Rename", use_container_width=True):
        st.session_state.renaming_doc = None
        st.rerun()
        
    st.html('</div></div>')
    st.stop()

# Route and render main page content
if st.session_state.page == "home":
    st.html(topbar_html)

    if st.session_state.active_document:
        pages_str = ""
        indexed_time = "Unknown"
        try:
            from frontend.components.sidebar import get_doc_metadata
            meta = get_doc_metadata(st.session_state.active_document)
            pages = meta.get("pages", 0)
            if pages > 0:
                pages_str = f"{pages} Pages"
            indexed_time = meta.get("upload_time", "Unknown")
        except Exception:
            pass

        clear_scope_href = f"/?theme={st.session_state.theme}&page=home"
        scoped_card_html = f'''
        <div class="scoped-doc-card" style="display: flex; justify-content: space-between; align-items: center; gap: 20px;">
            <div class="scoped-card-left" style="flex: 1; min-width: 0;">
                <div class="scoped-doc-header" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span class="scoped-doc-icon" style="font-size: 16px;">📄</span>
                    <span class="scoped-doc-title" style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: var(--text-secondary); letter-spacing: 0.5px;">Scoped Knowledge Base</span>
                </div>
                <div class="scoped-doc-filename" style="font-size: 18px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; word-break: break-all;">{st.session_state.active_document}</div>
                <div class="scoped-doc-desc" style="font-size: 13px; color: var(--text-secondary);">All answers are currently generated only from this document.</div>
            </div>
            <div class="scoped-card-right" style="display: flex; flex-direction: column; align-items: flex-end; gap: 6px; text-align: right; flex-shrink: 0;">
                <span class="scoped-status-badge">
                    <span class="scoped-status-dot"></span>
                    Scoped
                </span>
                <span class="scoped-page-count" style="font-size: 13px; font-weight: 600; color: var(--text-primary);">{pages_str}</span>
                <span style="font-size: 10.5px; color: var(--text-secondary);">Last indexed: {indexed_time}</span>
                <a href="{clear_scope_href}" target="_self" class="clear-scope-btn">✕ Clear Scope</a>
            </div>
        </div>
        '''
        st.html(scoped_card_html)
    else:
        global_card_html = f'''
        <div class="global-search-card">
            <div class="global-search-icon-wrap">🌍</div>
            <div class="global-search-content">
                <div class="global-search-title">Searching Across All Documents</div>
                <div class="global-search-desc">All responses will use the combined context of your complete PDF library.</div>
            </div>
        </div>
        '''
        st.html(global_card_html)

    render_home(current_theme=st.session_state.theme)
    # Hide fixed bottom chat input on Home page
    st.html("<style>[data-testid='stBottom'] { display: none !important; }</style>")

    st.html('<div class="footer-note">AI responses are grounded using your uploaded documents.</div>')

elif st.session_state.page == "upload":
    st.html(topbar_html)

    uploaded_files, upload_clicked = render_upload()

    if upload_clicked and uploaded_files:
        with st.spinner("Processing & Ingesting documents..."):
            try:
                res = upload_documents(uploaded_files)
                if res.get("success"):
                    st.session_state["upload_success"] = res.get("message", "Document updated successfully!")
                    st.rerun()
                else:
                    st.error(res.get("detail", "Error processing documents."))
            except Exception as e:
                st.error(f"Ingestion failed: {e}")
    elif upload_clicked and not uploaded_files:
        st.warning("Please choose one or more PDF files to upload first.")

    st.write("---")
    st.subheader("📚 Managed Knowledge Base")
    if documents:
        for doc in documents:
            col1, col2 = st.columns([5, 1])
            col1.write(f"📄 **{doc}**")
            if col2.button("🗑️", key=f"del_{doc}"):
                with st.spinner(f"Deleting {doc}..."):
                    delete_res = delete_document_api(doc)
                    if delete_res.get("success"):
                        st.success(f"Deleted {doc}")
                        st.rerun()
                    else:
                        st.error(delete_res.get("detail", f"Failed to delete {doc}."))
    else:
        st.info("No documents uploaded yet.")

elif st.session_state.page == "chat":
    st.html(topbar_html)
    render_chat_fragment(st.session_state.session_id, chats)
