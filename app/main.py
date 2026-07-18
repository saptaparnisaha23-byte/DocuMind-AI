from chatbot import ask_question

while True:

    question = input("\nAsk a question (type exit to quit): ")

    if question.lower() == "exit":
        break

    answer = ask_question(question)

    print("\nAnswer:\n")
    print(answer)