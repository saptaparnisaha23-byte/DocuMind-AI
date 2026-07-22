import streamlit as st


def render_home():

    st.markdown("""

<div class="main-area">

<div class="hero">

<div class="hero-icon">
📚
</div>

<h1>DocuMind AI</h1>

<p>
Private AI assistant for chatting with your documents
</p>

</div>

<div class="prompt-row">

<div class="prompt-card">
<h3>Summarize PDF</h3>
<p>Generate a concise summary of uploaded documents.</p>
</div>

<div class="prompt-card">
<h3>Explain Concepts</h3>
<p>Understand technical content in simple language.</p>
</div>

<div class="prompt-card">
<h3>Create Notes</h3>
<p>Generate revision notes from PDFs instantly.</p>
</div>

</div>

<div class="chat-input">

<input placeholder="Ask anything about your documents..." />

<button>➜</button>

</div>

</div>

""", unsafe_allow_html=True)