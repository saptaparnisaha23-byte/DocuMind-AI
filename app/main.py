try:
    from .chatbot import ask_question
except ImportError:
    from chatbot import ask_question


def main() -> None:
    while True:
        try:
            question = input("\nAsk a question (type exit to quit): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if question.lower() == "exit":
            print("Goodbye!")
            break

        if not question:
            print("Please enter a question.")
            continue

        try:
            result = ask_question(question)

            print("\nAnswer:\n")
            print(result.get("answer", "No answer was returned."))

            print("\nSources:\n")

            sources = result.get("sources", [])

            if not sources:
                print("No sources found.")
                continue

            for source in sources:
                source_name = source.get("source", "Unknown source")
                page = source.get("page", "Unknown")
                chunk = source.get("chunk", "Unknown")

                print(
                    f"📄 {source_name} "
                    f"(Page {page}, Chunk {chunk})"
                )

        except Exception as error:
            print(f"\nAn error occurred: {error}")


if __name__ == "__main__":
    main()