import fitz
from pathlib import Path

# Folder containing PDFs
PDF_FOLDER = Path("data/pdfs")

def extract_pdf_text(pdf_path):
    document = fitz.open(pdf_path)

    text = ""

    for page_number, page in enumerate(document):
        page_text = page.get_text()

        print(f"\n========== Page {page_number + 1} ==========\n")
        print(page_text)

        text += page_text

    return text


def main():
    pdf_files = list(PDF_FOLDER.glob("*.pdf"))

    if not pdf_files:
        print("No PDF found in data/pdfs/")
        return

    pdf = pdf_files[0]

    print(f"Reading: {pdf.name}")

    full_text = extract_pdf_text(pdf)

    print("\nTotal Characters:", len(full_text))


if __name__ == "__main__":
    main()