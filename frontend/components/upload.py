import streamlit as st

def render_upload():
    header_html = '''
    <div class="upload-page-container">
        <div class="upload-page-icon">📤</div>
        <div class="upload-page-title">Ingest New Documents</div>
        <div class="upload-page-desc">
            Expand your enterprise knowledge base. Upload one or multiple PDF files to process and embed them for grounded question answering.
        </div>
    </div>
    '''
    st.html(header_html)

    # Wrap the Streamlit file uploader in styled div
    st.html('<div style="max-width: 640px; margin: 0 auto 24px auto;">')
    
    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="main_page_uploader"
    )
    
    col1, col2, col3 = st.columns([2, 2, 2])
    with col2:
        upload_clicked = st.button("🚀 Process & Ingest Files", use_container_width=True, type="primary")

    st.html('</div>')

    return uploaded_files, upload_clicked