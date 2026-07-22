from app.retrieve import retrieve_chunks

question = input("Ask a question: ")

results = retrieve_chunks(question)

print("\n========== RETRIEVAL RESULTS ==========\n")

print(results)

print("\n=======================================\n")

if results["documents"][0]:

    for i, doc in enumerate(results["documents"][0], start=1):

        print(f"\nResult {i}")
        print("-" * 70)
        print(doc)

else:
    print("No documents found.")