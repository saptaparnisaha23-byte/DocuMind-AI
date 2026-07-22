import chromadb
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
client = chromadb.PersistentClient(path=str(PROJECT_ROOT / "chroma_db"))
collection = client.get_or_create_collection("documind_ai")

print("Total Chunks:", collection.count())

results = collection.get()

print("\nFirst 10 metadata entries:\n")

for meta in results["metadatas"][:10]:
    print(meta)

print("\nDocuments Found:\n")

docs = set()

for meta in results["metadatas"]:
    docs.add(meta["document"])

for doc in docs:
    print(doc)