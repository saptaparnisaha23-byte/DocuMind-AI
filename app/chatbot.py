from retrieve import retrieve_chunks
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def ask_question(question):

    results = retrieve_chunks(question)

    context = "\n\n".join(results["documents"][0])

    prompt = f"""
You are an AI assistant.

Answer ONLY using the context below.

If the answer is not present, say:
"I could not find the answer in the uploaded document."

Context:

{context}

Question:

{question}
"""

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )

    return response.text