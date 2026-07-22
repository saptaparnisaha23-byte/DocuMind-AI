import streamlit as st
from urllib.parse import quote
import html

def render_home(current_theme="dark"):
    # Define prompt cards and queries
    prompts = [
        {
            "icon": "📘",
            "title": "Summarize this PDF",
            "desc": "Generate a concise summary of the key takeaways and main concepts.",
            "query": "Summarize the key takeaways and main concepts of the uploaded documents."
        },
        {
            "icon": "📝",
            "title": "Generate Notes",
            "desc": "Create structured study or reference notes from the document contents.",
            "query": "Generate comprehensive study or reference notes from the uploaded documents."
        },
        {
            "icon": "🎯",
            "title": "Important Questions",
            "desc": "Identify and answer the top questions answered by these materials.",
            "query": "Identify the top 5 most important questions answered by these documents."
        },
        {
            "icon": "❓",
            "title": "Explain Like I'm 10",
            "desc": "Break down complex topics and rules in simple, easy terms.",
            "query": "Explain the core concepts of these documents in simple terms as if I'm 10 years old."
        },
        {
            "icon": "📚",
            "title": "Generate MCQs",
            "desc": "Create multiple-choice questions with answers for review.",
            "query": "Generate 5 multiple-choice questions with answers based on the uploaded documents."
        }
    ]

    cards_html = ""
    for p in prompts:
        encoded_query = quote(p["query"])
        url = f"/?theme={current_theme}&query={encoded_query}"
        cards_html += f'''
        <a href="{url}" target="_self" class="prompt-card-link">
            <div class="prompt-card-box">
                <div class="prompt-card-title">
                    <span style="font-size: 16px;">{p["icon"]}</span> {p["title"]}
                </div>
                <div class="prompt-card-desc">{p["desc"]}</div>
            </div>
        </a>
        '''

    active_doc = st.session_state.get("active_document")
    scoped_input_html = f'<input type="hidden" name="document" value="{html.escape(active_doc)}">' if active_doc else ''

    home_html = f'''
    <div style="max-width: 750px; margin: 0 auto; padding: 0 10px;">
        <div class="hero-container">
            <div class="hero-logo">🧠</div>
            <h1 class="hero-h1">DocuMind AI</h1>
            <p class="hero-p">
                Enterprise Document Intelligence Platform. Upload your PDFs and ask questions to receive grounded answers with full citations.
            </p>
        </div>
        
        <div class="cards-grid">
            {cards_html}
        </div>

        <form action="/" method="get" target="_self" style="width: 100%; max-width: 680px; margin: 32px auto 0 auto;">
            <input type="hidden" name="theme" value="{current_theme}">
            {scoped_input_html}
            <div class="home-inline-input-container">
                <input type="text" name="query" class="home-inline-input" placeholder="Ask anything about your uploaded documents..." autocomplete="off" required>
                <button type="submit" class="home-inline-submit-btn">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" style="width: 14px; height: 14px;"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 10.5 12 3m0 0 7.5 7.5M12 3v18" /></svg>
                </button>
            </div>
        </form>
    </div>
    '''

    st.html(home_html)