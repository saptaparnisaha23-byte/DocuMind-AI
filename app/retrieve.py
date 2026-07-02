from sentence_transformers import SentenceTransformer
import chromadb

# Load the same embedding model used during storage
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to ChromaDB
client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_collection("askmybook")


def retrieve_chunks(question, top_k=3):
    """
    Retrieve the most relevant document chunks.
    """

    # Convert question into embedding
    question_embedding = model.encode(question).tolist()

    # Search database
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k
    )

    return results