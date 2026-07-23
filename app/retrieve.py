import chromadb
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent

@st.cache_resource(show_spinner=False)
def get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_resource(show_spinner=False)
def get_chroma_client():
    return chromadb.PersistentClient(path=str(PROJECT_ROOT / "chroma_db"))

@st.cache_resource(show_spinner=False)
def get_chroma_collection():
    client = get_chroma_client()
    return client.get_or_create_collection("documind_ai")

# Expose module-level proxies for backward compatibility
class CollectionProxy:
    def __getattr__(self, name):
        return getattr(get_chroma_collection(), name)

collection = CollectionProxy()


def retrieve_chunks(question, top_k=3, document=None):
    question = question.strip()

    if not question:
        return {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }

    model = get_model()
    coll = get_chroma_collection()
    embedding = model.encode(question).tolist()

    if document:
        results = coll.query(
            query_embeddings=[embedding],
            n_results=top_k,
            where={"document": document},
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )
    else:
        results = coll.query(
            query_embeddings=[embedding],
            n_results=top_k,
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

    return results