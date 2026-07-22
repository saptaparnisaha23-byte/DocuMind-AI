from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from pathlib import Path

_model = None

def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

# Create ChromaDB client
PROJECT_ROOT = Path(__file__).resolve().parent.parent
client = chromadb.PersistentClient(path=str(PROJECT_ROOT / "chroma_db"))

# Create or get collection
collection = client.get_or_create_collection("documind_ai")


import re

def chunk_text(text):
    """
    Custom semantic-aware text chunker that preserves headings, lists, tables,
    formulas, and question-answer pairs, and groups them into optimal chunks.
    """
    # Split text into logical lines/paragraphs
    raw_blocks = text.split("\n\n")
    blocks = []
    for rb in raw_blocks:
        rb_stripped = rb.strip()
        if not rb_stripped:
            continue
        blocks.append(rb_stripped)
            
    chunks = []
    current_chunk = []
    current_length = 0
    max_chunk_size = 1000
    overlap_size = 200
    
    active_heading = ""
    
    for block in blocks:
        block_len = len(block)
        
        # Detect if this block is a heading
        is_heading = False
        lines = block.split('\n')
        if len(lines) == 1 and len(block) < 100:
            # Check for heading pattern (e.g. "1.2 ", "Chapter 1", etc.)
            if re.match(r'^(?:[I|V|X\d]+\.?\s+|[a-zA-Z]\.?\s+|Chapter|Section|Unit|Part|Module|Topic)\b', block, re.IGNORECASE) or block.isupper():
                is_heading = True
                active_heading = block
        
        # If adding this block exceeds the max chunk size
        if current_length + block_len > max_chunk_size:
            if current_chunk:
                # Save the current chunk
                chunk_str = "\n\n".join(current_chunk)
                chunks.append(chunk_str)
                
                # Start new chunk with overlap
                new_chunk = []
                new_length = 0
                if active_heading and active_heading != block:
                    new_chunk.append(f"[Section: {active_heading}]")
                    new_length += len(active_heading) + 20
                
                # Add overlap from the end of the previous chunk
                overlap_blocks = []
                overlap_len = 0
                for prev_block in reversed(current_chunk):
                    if prev_block.startswith("[Section:"):
                        continue
                    if overlap_len + len(prev_block) < overlap_size:
                        overlap_blocks.insert(0, prev_block)
                        overlap_len += len(prev_block) + 2
                    else:
                        break
                
                new_chunk.extend(overlap_blocks)
                new_length += overlap_len
                
                current_chunk = new_chunk
                current_length = new_length
            
        current_chunk.append(block)
        current_length += block_len + 2
        
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
        
    return chunks



def store_chunks(chunks, source_name, page_number):
    """
    Convert chunks into embeddings and store them in ChromaDB.
    """
    if not chunks:
        return

    # Batch encode all chunks for this page in a single model call
    model = get_model()
    embeddings = model.encode(chunks).tolist()

    ids = [f"{source_name}_page_{page_number}_chunk_{index}" for index in range(len(chunks))]
    metadatas = [
        {
            "source": source_name,
            "page": page_number,
            "chunk": index + 1,
            "document": source_name,
        }
        for index in range(len(chunks))
    ]

    # Insert all chunks to ChromaDB in a single batch call
    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(f"Stored {len(chunks)} chunks successfully!")


def reset_collection():
    """
    Delete the entire ChromaDB collection.
    """

    global collection

    try:
        client.delete_collection("documind_ai")
    except Exception:
        pass

    collection = client.get_or_create_collection("documind_ai")


def delete_document(document_name):
    """
    Delete every chunk belonging to one document.
    """

    results = collection.get(
        where={"document": document_name}
    )

    if results["ids"]:
        collection.delete(
            where={"document": document_name}
        )
        print(f"{document_name} removed from ChromaDB.")
    else:
        print(f"No embeddings found for {document_name}.")