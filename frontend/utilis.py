import fitz
from pathlib import Path

def export_chat_to_pdf(messages, session_title="DocuMind AI Chat Export"):
    """
    Generate a beautifully formatted PDF report of the chat messages using PyMuPDF.
    Returns:
        bytes: The compiled PDF file content.
    """
    doc = fitz.open()
    
    margin = 50
    page_width = 595  # A4 width in points
    page_height = 842  # A4 height in points
    width = page_width - 2 * margin
    
    # Create the first page
    page = doc.new_page(width=page_width, height=page_height)
    
    # Header Title
    y = 50
    page.insert_text((margin, y), "DocuMind AI - Chat Session Report", fontsize=16, fontname="helvb", color=(0.1, 0.2, 0.4))
    y += 20
    page.insert_text((margin, y), f"Session: {session_title}", fontsize=11, fontname="helvb", color=(0.3, 0.3, 0.3))
    y += 15
    page.draw_line((margin, y), (page_width - margin, y), color=(0.8, 0.8, 0.8), width=1)
    y += 30
    
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        
        # Clean citations/debug info if present in assistant responses
        if "||CITATIONS||" in content:
            content = content.split("||CITATIONS||")[0]
            
        role_label = "You: " if role.lower() == "user" else "DocuMind AI: "
        role_font = "helvb"
        role_color = (0.2, 0.5, 0.2) if role.lower() == "user" else (0.1, 0.3, 0.6)
        
        # Check if we need a new page for the role label
        if y > page_height - 100:
            page = doc.new_page(width=page_width, height=page_height)
            y = 50
            
        # Draw role label
        page.insert_text((margin, y), role_label, fontsize=10, fontname=role_font, color=role_color)
        y += 15
        
        # Draw message content (handling line wraps manually)
        text_lines = []
        for line in content.split("\n"):
            words = line.split(" ")
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                # Measure width of test line using approximate font metrics
                if len(test_line) * 5.2 > width:
                    text_lines.append(current_line)
                    current_line = word
                else:
                    current_line = test_line
            if current_line:
                text_lines.append(current_line)
                
        for line in text_lines:
            if y > page_height - 50:
                page = doc.new_page(width=page_width, height=page_height)
                y = 50
            page.insert_text((margin + 10, y), line, fontsize=9.5, fontname="helv", color=(0.1, 0.1, 0.1))
            y += 13
            
        y += 15  # spacing between messages
        
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes
