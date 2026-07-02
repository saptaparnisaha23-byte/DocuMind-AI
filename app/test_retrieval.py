from retrieve import retrieve_chunks

question = input("Ask a question: ")

results = retrieve_chunks(question)

print("\nTop Results\n")

for i, doc in enumerate(results["documents"][0]):

    print("=" * 60)

    print(f"Result {i+1}")

    print(doc[:500])

    print()