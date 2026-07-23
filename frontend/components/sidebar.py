import html
import os
from pathlib import Path
from urllib.parse import urlencode
import streamlit as st
import fitz  # PyMuPDF
from datetime import datetime, timedelta

def _safe(value):
    return html.escape(str(value or ""), quote=True)

def _link(theme="dark", **params):
    """Build a safely encoded Streamlit navigation URL."""
    clean_params = {"theme": theme}
    for key, value in params.items():
        if value is not None and value != "":
            clean_params[key] = value
    return "/?" + urlencode(clean_params)

def _relative_time(dt_str):
    """Convert a datetime string to relative time like '2m ago', 'Yesterday'."""
    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        now = datetime.utcnow()
        delta = now - dt
        
        if delta.total_seconds() < 0 or delta < timedelta(minutes=1):
            return "Just now"
        elif delta < timedelta(hours=1):
            mins = int(delta.total_seconds() / 60)
            return f"{mins}m ago"
        elif delta < timedelta(hours=24):
            hours = int(delta.total_seconds() / 3600)
            return f"{hours}h ago"
        elif delta < timedelta(days=2):
            return "Yesterday"
        elif delta < timedelta(days=7):
            days = int(delta.days)
            return f"{days}d ago"
        else:
            return dt.strftime("%b %d")
    except Exception:
        return dt_str or ""

@st.cache_data(show_spinner=False)
def get_doc_metadata(filename):
    """Retrieve and cache PDF pages and upload time dynamically."""
    if "doc_metadata_cache" not in st.session_state:
        st.session_state.doc_metadata_cache = {}
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    file_path = PROJECT_ROOT / "uploads" / filename
    if not file_path.exists():
        return {"pages": 0, "upload_time": "Unknown", "size": "Unknown", "last_modified": "Unknown"}
        
    mtime = file_path.stat().st_mtime
    size_bytes = file_path.stat().st_size
    cache_key = f"{filename}_{mtime}_{size_bytes}"
    
    if cache_key in st.session_state.doc_metadata_cache:
        return st.session_state.doc_metadata_cache[cache_key]
        
    try:
        doc = fitz.open(file_path)
        pages = len(doc)
        doc.close()
    except Exception:
        pages = 0
        
    # Format file size
    if size_bytes < 1024 * 1024:
        size_str = f"{size_bytes / 1024:.1f} KB"
    else:
        size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
        
    upload_time = datetime.fromtimestamp(mtime).strftime("%b %d, %Y, %I:%M %p")
    last_mod_str = datetime.fromtimestamp(mtime).strftime("%b %d, %Y, %I:%M %p")
    
    meta = {
        "pages": pages,
        "upload_time": upload_time,
        "size": size_str,
        "last_modified": last_mod_str
    }
    st.session_state.doc_metadata_cache[cache_key] = meta
    return meta

def render_sidebar(
    documents,
    chats,
    active_session_id=None,
    current_page="home",
    current_theme="dark",
    active_document=None,
):
    documents = documents or []
    chats = chats or []
    pinned_chats = st.session_state.get("pinned_chats", set())

    # --- PDF LIBRARY SECTION ---
    if not documents:
        doc_items = (
            '<div class="sidebar-nav-item" style="pointer-events: none; opacity: 0.5; padding: 6px 8px;">'
            '<div class="nav-item-left">'
            '<span class="sidebar-item-icon">📄</span>'
            '<span class="nav-item-text" style="font-size: 11.5px; color: var(--text-muted);">No files uploaded</span>'
            '</div>'
            '</div>'
        )
    else:
        doc_items = '<div class="scrollable-list" style="position: relative;">'
        # Sort documents by modification time descending (most recent first)
        def get_doc_mtime(doc_name):
            try:
                PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
                file_path = PROJECT_ROOT / "uploads" / doc_name
                if file_path.exists():
                    return file_path.stat().st_mtime
            except Exception:
                pass
            return 0
            
        sorted_documents = sorted(documents, key=get_doc_mtime, reverse=True)
        for doc in sorted_documents:
            doc_text = _safe(doc)
            active_class = "active" if doc == active_document else ""
            href = _link(theme=current_theme, document=doc)
            
            # Fetch metadata
            meta = get_doc_metadata(doc)
            pages = meta["pages"]
            upload_time = meta["upload_time"]
            
            is_active = (doc == active_document)
            
            # Scoped status indicator beside document name
            scoped_badge_html = ""
            if is_active:
                scoped_badge_html = '<span class="active-status-badge active-scoped">Scoped</span>'
            
            # Use for chat option
            if is_active:
                menu_use_chat = '<div class="doc-dropdown-item active-item" style="pointer-events: none; opacity: 0.5; cursor: default;">✓ Currently Active</div>'
            else:
                menu_use_chat = f'<a href="{_link(theme=current_theme, document=doc)}" target="_self" class="doc-dropdown-item">✓ Use for Current Chat</a>'
                
            # Search all documents option (clears PDF scope)
            if current_page == "chat" and active_session_id:
                search_all_href = _link(theme=current_theme, session_id=active_session_id)
            else:
                search_all_href = _link(theme=current_theme, page="home")
                
            menu_search_all = f'<a href="{search_all_href}" target="_self" class="doc-dropdown-item">🌍 Search All Documents</a>'
            
            # View details navigates to URL query params
            details_href = _link(theme=current_theme, view_details_doc=doc)
            menu_details = f'<a href="{details_href}" target="_self" class="doc-dropdown-item">👁 View Details</a>'
            
            # Rename options
            menu_rename = f'<a href="{_link(theme=current_theme, rename_doc=doc)}" target="_self" class="doc-dropdown-item">✏ Rename</a>'
            
            # Delete confirmation triggers confirm_delete_doc query parameter
            delete_href = _link(theme=current_theme, confirm_delete_doc=doc)
            menu_delete = f'<a href="{delete_href}" target="_self" class="doc-dropdown-item destructive-item">🗑 Delete PDF</a>'
            
            doc_items += f'''
            <div class="sidebar-nav-item {active_class}" style="padding: 6px 8px; position: relative;">
                <a href="{href}" target="_self" class="nav-item-left" style="text-decoration: none; color: inherit; display: flex; align-items: center; gap: 8px; min-width: 0; padding-right: 28px;">
                    <span class="sidebar-item-icon">📄</span>
                    <div style="min-width: 0; flex: 1;">
                        <div class="nav-item-text" title="{doc_text}" style="font-size: 12px; font-weight: 500; display: flex; align-items: center; justify-content: space-between; gap: 4px;">
                            <span style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{doc_text}</span>
                            {scoped_badge_html}
                        </div>
                        <div class="nav-item-meta" style="font-size: 10px; opacity: 0.7;">{pages} pgs • {upload_time}</div>
                    </div>
                </a>
                
                <!-- Pure CSS dropdown using tab focus container -->
                <div class="three-dots-container" tabindex="0">
                    <button class="three-dots-btn" aria-label="More options">⋮</button>
                    
                    <!-- Floating options dropdown menu -->
                    <div class="doc-options-dropdown">
                        {menu_use_chat}
                        <div class="doc-dropdown-divider"></div>
                        {menu_details}
                        {menu_rename}
                        {menu_delete}
                        <div class="doc-dropdown-divider"></div>
                        {menu_search_all}
                    </div>
                </div>
            </div>
            '''
        doc_items += '</div>'

    # --- RECENT CHATS SECTION ---
    if not chats:
        chat_items = (
            '<div class="sidebar-nav-item" style="pointer-events: none; opacity: 0.5; padding: 6px 8px;">'
            '<div class="nav-item-left">'
            '<span class="sidebar-item-icon">💬</span>'
            '<span class="nav-item-text" style="font-size: 11.5px; color: var(--text-muted);">No recent chats</span>'
            '</div>'
            '</div>'
        )
    else:
        # Sort chats: pinned first, then by date (newest first)
        sorted_chats = sorted(
            chats,
            key=lambda c: (c.get("session_id") in pinned_chats, c.get("created_at") or ""),
            reverse=True
        )
        
        chat_items = '<div class="scrollable-list chat-history-list">'
        for chat in sorted_chats:
            session_id = chat.get("session_id")
            raw_title = str(chat.get("title") or "Untitled chat")
            title = raw_title
            
            is_pinned = session_id in pinned_chats
            pin_icon_style = 'style="color: var(--accent); opacity: 1;"' if is_pinned else ""
            pin_title = "Unpin Chat" if is_pinned else "Pin Chat"

            active_class = (
                "active"
                if session_id == active_session_id and current_page == "chat"
                else ""
            )

            href = _link(theme=current_theme, session_id=session_id)
            
            # Format timestamp with relative time
            time_str = ""
            if chat.get("created_at"):
                time_str = _relative_time(chat["created_at"])

            # Pin icon SVG
            pin_svg = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width: 12px; height: 12px;"><path stroke-linecap="round" stroke-linejoin="round" d="M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0 1 11.186 0Z" /></svg>'
            
            # Edit icon SVG
            edit_svg = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width: 12px; height: 12px;"><path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.83 20.013a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125" /></svg>'
            # Pinned indicator
            pin_indicator = '<span style="font-size: 9px; margin-left: 2px;">📌</span>' if is_pinned else ''

            chat_items += f'''
            <div class="sidebar-nav-item chat-list-item {active_class}" style="padding: 6px 8px;">
                <a href="{href}" target="_self" class="nav-item-left" style="text-decoration: none; color: inherit; display: flex; align-items: center; gap: 8px; min-width: 0;">
                    <span class="sidebar-item-icon">&#x1F4AC;</span>
                    <div style="min-width: 0; flex: 1;">
                        <div class="nav-item-text" title="{_safe(title)}" style="font-size: 12px;">{_safe(title)}{pin_indicator}</div>
                        <div class="nav-item-meta" style="font-size: 10px; opacity: 0.7;">{time_str}</div>
                    </div>
                </a>
                <div class="three-dots-container" tabindex="0" style="flex-shrink: 0;">
                    <button class="sidebar-action-icon-btn" style="background:none;border:none;cursor:pointer;padding:4px;color:var(--text-secondary);font-size:16px;line-height:1;font-weight:bold;" title="Chat options">&#x22EE;</button>
                    <div class="doc-options-dropdown" style="right:-4px;top:24px;min-width:160px;">
                        <a href="{_link(theme=current_theme, pin_chat=session_id)}" target="_self" class="doc-dropdown-item" {pin_icon_style}>&#x1F4CC; {"Unpin" if is_pinned else "Pin"}</a>
                        <a href="{_link(theme=current_theme, rename_chat=session_id)}" target="_self" class="doc-dropdown-item">&#x270F;&#xFE0F; Rename</a>
                        <div class="doc-dropdown-divider"></div>
                        <a href="{_link(theme=current_theme, delete_chat=session_id)}" target="_self" class="doc-dropdown-item destructive-item">&#x1F5D1;&#xFE0F; Delete</a>
                    </div>
                </div>
            </div>
            '''
        chat_items += '<div class="no-chats-found" id="noChatsMsg">No chats found</div>'
        chat_items += '</div>'

    home_active = (
        "active"
        if current_page == "home" and not active_document and not active_session_id
        else ""
    )

    sidebar_html = f"""
    <aside class="sidebar" id="sidebarPanel">
        <button class="sidebar-close-btn" id="sidebarCloseBtn" aria-label="Close sidebar">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" style="width:18px;height:18px;">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
            </svg>
        </button>

        <div class="logo-container">
            <div class="logo-shield" aria-hidden="true">&#x1F9E0;</div>
            <div class="logo-title-wrap">
                <div class="logo-title-row"><span class="logo-title-text">DocuMind AI</span></div>
                <span class="logo-sub-text">Enterprise Knowledge Assistant</span>
            </div>
        </div>

        <a href="{_link(theme=current_theme, page='upload')}" target="_self" class="upload-card" style="text-decoration:none;display:block;color:inherit;">
            <div class="upload-icon" aria-hidden="true">&#x1F4E4;</div>
            <div class="upload-main-text">Click to Ingest PDF</div>
            <div class="upload-sub-text">Max size 200MB</div>
        </a>

        <div class="section-label-row">
            <span class="section-label">PDF Library</span>
            <span class="section-pill">{len(documents)} FILES</span>
        </div>
        {doc_items}

        <div class="section-label-row">
            <span class="section-label">Recent Chats</span>
            <a href="{_link(theme=current_theme, page='home')}" target="_self" class="new-chat-link">+ NEW CHAT</a>
        </div>

        <div class="history-search-container">
            <span class="history-search-icon">&#x1F50D;</span>
            <input type="text" class="history-search-input" placeholder="Search chat history..." onkeyup="filterChats(this.value)">
        </div>

        {chat_items}
    </aside>

    <script>
    function filterChats(query) {{
        const items = document.querySelectorAll('.chat-list-item');
        const noMsg = document.getElementById('noChatsMsg');
        const q = query.toLowerCase().trim();
        let visibleCount = 0;
        items.forEach(item => {{
            const textEl = item.querySelector('.nav-item-text');
            if (!textEl) return;
            const text = textEl.textContent.toLowerCase();
            if (!q || text.includes(q)) {{ item.style.display='flex'; visibleCount++; }}
            else {{ item.style.display='none'; }}
        }});
        if (noMsg) {{ noMsg.style.display = (visibleCount===0 && q) ? 'block' : 'none'; }}
    }}

    // Mobile sidebar toggle - injects button into PARENT page so it's always visible
    (function() {{
        var parentDoc = window.parent.document;
        var sidebar = document.getElementById('sidebarPanel');
        var closeBtn = document.getElementById('sidebarCloseBtn');
        if (!sidebar) return;

        // Cleanup previous rerun elements
        var old1 = parentDoc.getElementById('dm-sidebar-toggle');
        var old2 = parentDoc.getElementById('dm-sidebar-backdrop');
        if (old1) old1.remove();
        if (old2) old2.remove();

        // Create hamburger toggle button in parent page
        var toggleBtn = parentDoc.createElement('button');
        toggleBtn.id = 'dm-sidebar-toggle';
        toggleBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" style="width:20px;height:20px;"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"/></svg>';
        toggleBtn.style.cssText = 'display:none;position:fixed;top:12px;left:12px;z-index:1000000;background:var(--bg-card,#161b22);border:1px solid var(--border-color,#30363d);border-radius:10px;color:var(--text-primary,#e6edf3);width:40px;height:40px;align-items:center;justify-content:center;cursor:pointer;box-shadow:0 4px 12px rgba(0,0,0,0.3);transition:all 0.2s ease;padding:0;';

        // Create backdrop in parent page
        var backdrop = parentDoc.createElement('div');
        backdrop.id = 'dm-sidebar-backdrop';
        backdrop.style.cssText = 'display:none;position:fixed;inset:0;background:rgba(0,0,0,0.5);backdrop-filter:blur(2px);-webkit-backdrop-filter:blur(2px);z-index:999998;opacity:0;pointer-events:none;transition:opacity 0.3s ease;';

        parentDoc.body.appendChild(toggleBtn);
        parentDoc.body.appendChild(backdrop);

        function checkMobile() {{
            var isMobile = window.parent.innerWidth <= 768;
            toggleBtn.style.display = isMobile ? 'flex' : 'none';
            backdrop.style.display = isMobile ? 'block' : 'none';
            closeBtn.style.display = isMobile ? 'flex' : 'none';
            if (!isMobile) {{
                sidebar.classList.remove('open');
                backdrop.style.opacity = '0';
                backdrop.style.pointerEvents = 'none';
            }}
        }}
        checkMobile();
        window.parent.addEventListener('resize', checkMobile);

        function openSB() {{
            sidebar.classList.add('open');
            backdrop.style.opacity = '1';
            backdrop.style.pointerEvents = 'auto';
            toggleBtn.style.opacity = '0';
            toggleBtn.style.pointerEvents = 'none';
        }}
        function closeSB() {{
            sidebar.classList.remove('open');
            backdrop.style.opacity = '0';
            backdrop.style.pointerEvents = 'none';
            toggleBtn.style.opacity = '1';
            toggleBtn.style.pointerEvents = 'auto';
        }}

        toggleBtn.addEventListener('click', openSB);
        backdrop.addEventListener('click', closeSB);
        closeBtn.addEventListener('click', closeSB);

        // Auto-close sidebar on link click (mobile UX)
        sidebar.querySelectorAll('a[target="_self"]').forEach(function(link) {{
            link.addEventListener('click', function() {{
                if (window.parent.innerWidth <= 768) closeSB();
            }});
        }});
    }})();
    </script>
    """

    st.html(sidebar_html)