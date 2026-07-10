from sentence_transformers import SentenceTransformer
import chromadb

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to ChromaDB
client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection("askmybook")


def retrieve_chunks(question, top_k=3):
    """
    Retrieve the most relevant chunks for a question.
    """

    question_embedding = model.encode(question).tolist()

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k
    )

    return results