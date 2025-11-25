"""
RAG system management endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.rag_service import RAGService

router = APIRouter()

# Initialize RAG service
rag_service = RAGService()

# Keep in-memory storage for backward compatibility and quick access
rag_documents = {}


@router.post("/upload")
async def upload_rag_document(file: UploadFile = File(...), doc_type: str = "style_guide"):
    """
    Upload a document to the RAG knowledge base

    doc_type: "style_guide" or "reference"
    """
    content = await file.read()
    content_text = content.decode("utf-8")

    # Add to vector database
    doc_id = rag_service.add_document(
        content=content_text,
        doc_type=doc_type,
        metadata={"filename": file.filename}
    )

    # Also store in memory for quick access
    rag_documents[doc_id] = {
        "id": doc_id,
        "filename": file.filename,
        "type": doc_type,
        "content": content_text,
        "status": "stored"
    }

    return {
        "id": doc_id,
        "doc_id": doc_id,  # Alias for compatibility
        "document_id": doc_id,  # Alias for compatibility
        "filename": file.filename,
        "name": file.filename,  # Alias for compatibility
        "type": doc_type,
        "doc_type": doc_type,  # Alias for compatibility
        "status": "uploaded"
    }


@router.get("/documents")
async def list_rag_documents():
    """List all documents in RAG knowledge base"""
    return {
        "documents": [
            {
                "id": doc_id,
                "doc_id": doc_id,  # Alias for compatibility
                "filename": doc["filename"],
                "name": doc["filename"],  # Alias for compatibility
                "type": doc["type"],
                "doc_type": doc["type"]  # Alias for compatibility
            }
            for doc_id, doc in rag_documents.items()
        ]
    }


@router.delete("/documents/{doc_id}")
async def delete_rag_document(doc_id: str):
    """Remove document from RAG knowledge base"""
    # Delete from vector database
    success = rag_service.delete_document(doc_id)

    # Also delete from memory
    if doc_id in rag_documents:
        del rag_documents[doc_id]

    if not success and doc_id not in rag_documents:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"status": "deleted", "document_id": doc_id}
