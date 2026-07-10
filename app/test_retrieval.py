from retrieve import retrieve_chunks

question = input("Ask a question: ")

results = retrieve_chunks(question)

print("\nTop Matching Chunks\n")

for i, doc in enumerate(results["documents"][0]):

    print("=" * 70)
    print(f"Result {i+1}")
    print("=" * 70)

    print(doc)
    print()