import unittest
import os
from pathlib import Path
from app.embed import chunk_text, get_model, store_chunks
from app.retrieve import retrieve_chunks

class TestRAGPipeline(unittest.TestCase):

    def test_chunk_text(self):
        sample_text = "DocuMind-AI is an artificial intelligence platform designed to parse PDF documents, construct semantic vector chunks, and perform hybrid retrieval for Google Gemini LLM answer generation. " * 10
        chunks = chunk_text(sample_text)
        self.assertTrue(len(chunks) > 0)
        self.assertIsInstance(chunks[0], str)

    def test_generate_embeddings(self):
        sample_chunks = [
            "DocuMind-AI processes unstructured PDF text into embeddings.",
            "ChromaDB stores high dimensional dense vectors."
        ]
        model = get_model()
        embeddings = model.encode(sample_chunks).tolist()
        self.assertEqual(len(embeddings), 2)
        self.assertIn(len(embeddings[0]), [384, 768])

    def test_retrieve_chunks_structure(self):
        query = "What is Multiple Linear Regression?"
        results = retrieve_chunks(query, top_k=3)
        self.assertIsInstance(results, dict)
        self.assertIn("documents", results)
        self.assertIn("metadatas", results)

if __name__ == "__main__":
    unittest.main()
