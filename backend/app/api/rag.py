"""
RAG system management endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()

# In-memory storage for uploaded RAG documents (MVP)
rag_documents = {}


@router.post("/upload")
async def upload_rag_document(file: UploadFile = File(...), doc_type: str = "style_guide"):
    """
    Upload a document to the RAG knowledge base

    doc_type: "style_guide" or "reference"
    """
    content = await file.read()

    # TODO: Process and add to vector database
    # For now, just store the content

    doc_id = f"{doc_type}_{file.filename}"
    rag_documents[doc_id] = {
        "id": doc_id,
        "filename": file.filename,
        "type": doc_type,
        "content": content.decode("utf-8"),
        "status": "stored"
    }

    return {
        "document_id": doc_id,
        "filename": file.filename,
        "type": doc_type,
        "status": "uploaded"
    }


@router.get("/documents")
async def list_rag_documents():
    """List all documents in RAG knowledge base"""
    return {
        "documents": [
            {
                "id": doc_id,
                "filename": doc["filename"],
                "type": doc["type"]
            }
            for doc_id, doc in rag_documents.items()
        ]
    }


@router.delete("/documents/{doc_id}")
async def delete_rag_document(doc_id: str):
    """Remove document from RAG knowledge base"""
    if doc_id not in rag_documents:
        raise HTTPException(status_code=404, detail="Document not found")

    del rag_documents[doc_id]
    return {"status": "deleted", "document_id": doc_id}
