from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Create ChromaDB client
client = chromadb.PersistentClient(path="chroma_db")

# Create or get collection
collection = client.get_or_create_collection("askmybook")


def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    return splitter.split_text(text)


def store_chunks(chunks):
    """
    Convert chunks into embeddings and store them in ChromaDB.
    """

    for index, chunk in enumerate(chunks):

        embedding = model.encode(chunk).tolist()

        collection.add(
            ids=[f"doc_chunk_{index}"],
            documents=[chunk],
            embeddings=[embedding]
        )

    print(f"\nStored {len(chunks)} chunks successfully!")
try:
    client.delete_collection("askmybook")
except:
    pass

collection = client.get_or_create_collection("askmybook")