from pathlib import Path
import shutil
from typing import Annotated

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import WithJsonSchema

from app.ingest import ingest_pdf
from app.embed import delete_document
from app.database import delete_document_metadata

router = APIRouter(
    prefix="",
    tags=["Documents"]
)

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = PROJECT_ROOT / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Force Swagger to show file picker
UploadFileBinary = Annotated[
    UploadFile,
    WithJsonSchema({"type": "string", "format": "binary"})
]


@router.post("/upload")
async def upload_documents(
    files: Annotated[list[UploadFileBinary], File()]
):
    """
    Upload one or more PDF documents.
    """

    uploaded = []

    for file in files:

        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail=f"{file.filename} is not a PDF."
            )

        save_path = UPLOAD_FOLDER / file.filename

        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = ingest_pdf(save_path)

        uploaded.append(result)

    return {
        "success": True,
        "message": f"{len(uploaded)} document(s) uploaded successfully.",
        "documents": uploaded
    }


@router.get("/documents")
def list_documents():
    """
    List all uploaded PDFs.
    """

    # Sort by modification time descending (most recent first)
    pdf_files = list(UPLOAD_FOLDER.glob("*.pdf"))
    pdf_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    documents = [file.name for file in pdf_files]

    return {
        "success": True,
        "count": len(documents),
        "documents": documents
    }


@router.delete("/documents/{filename}")
def delete_document_route(filename: str):
    """
    Delete a document from uploads and ChromaDB.
    """

    file_path = UPLOAD_FOLDER / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    # Delete PDF
    file_path.unlink()

    # Delete embeddings from ChromaDB
    delete_document(filename)

    # Delete document metadata from SQLite
    delete_document_metadata(filename)

    return {
        "success": True,
        "message": f"{filename} deleted successfully."
    }
