from pathlib import Path
import fitz
from app.embed import chunk_text, store_chunks, reset_collection
PROJECT_ROOT = Path(__file__).resolve().parent.parent
# Default folder containing PDFs
PDF_FOLDER = PROJECT_ROOT / "data" / "pdfs"


def extract_pdf_text(pdf_path):
    """
    Extract text from each page of a PDF.
    Returns:
        List of dictionaries:
        [
            {
                "page": 1,
                "text": "..."
            }
        ]
    """

    document = fitz.open(pdf_path)
    pages = []

    for page_number, page in enumerate(document, start=1):
        page_text = page.get_text()

        pages.append(
            {
                "page": page_number,
                "text": page_text
            }
        )

    document.close()

    return pages


def ingest_pdf(pdf_path, reset_db=False):
    """
    Ingest a single PDF into ChromaDB.

    Args:
        pdf_path: Path to PDF
        reset_db: True to clear database before ingesting

    Returns:
        Dictionary containing ingestion statistics.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"{pdf_path} not found.")

    if reset_db:
        print("Resetting vector database...")
        reset_collection()

    print(f"\nReading: {pdf_path.name}")

    pages = extract_pdf_text(pdf_path)

    total_characters = 0
    total_chunks = 0

    for page in pages:

        page_text = page["text"]
        page_number = page["page"]

        if not page_text.strip():
            print(f"Page {page_number} is empty. Skipping...")
            continue

        total_characters += len(page_text)

        chunks = chunk_text(page_text)

        total_chunks += len(chunks)

        store_chunks(
            chunks,
            pdf_path.name,
            page_number
        )

    print("\n===================================")
    print(f"PDF: {pdf_path.name}")
    print(f"Pages: {len(pages)}")
    print(f"Characters: {total_characters}")
    print(f"Chunks: {total_chunks}")
    print("===================================")

    return {
        "filename": pdf_path.name,
        "pages": len(pages),
        "characters": total_characters,
        "chunks": total_chunks
    }


def ingest_all_pdfs(reset_db=True):
    """
    Ingest every PDF inside data/pdfs.
    """

    pdf_files = list(PDF_FOLDER.glob("*.pdf"))

    if not pdf_files:
        print("No PDF found in data/pdfs/")
        return

    if reset_db:
        reset_collection()

    for pdf in pdf_files:
        ingest_pdf(pdf)


def main():
    ingest_all_pdfs(reset_db=True)


if __name__ == "__main__":
    main()