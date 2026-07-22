from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer("all-MiniLM-L6-v2")

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
client = chromadb.PersistentClient(path=str(PROJECT_ROOT / "chroma_db"))

collection = client.get_or_create_collection("documind_ai")


def retrieve_chunks(question, top_k=3, document=None):

    question = question.strip()

    if not question:
        return {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }

    embedding = model.encode(question).tolist()

    if document:

        results = collection.query(
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

        results = collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

    return results