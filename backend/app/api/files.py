"""
File upload and management endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List, Optional
import os
import uuid

router = APIRouter()

# Temporary file storage (in-memory for MVP, will be improved)
uploaded_files = {}


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    relative_path: Optional[str] = Form(None)
):
    """
    Upload a single C++ file for analysis

    Supports both individual file uploads and folder uploads with relative paths.
    Supported extensions: .cpp, .hpp, .h
    """
    # Validate file extension
    allowed_extensions = {".cpp", ".hpp", ".h"}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )

    # Read file content
    content = await file.read()

    # Check file size (max 10MB as per specs)
    max_size = 10 * 1024 * 1024  # 10MB
    if len(content) > max_size:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 10MB limit"
        )

    # Generate unique file ID
    file_id = str(uuid.uuid4())

    # Use relative_path if provided, otherwise just use filename
    display_path = relative_path if relative_path else file.filename

    # Store file (in-memory for MVP)
    uploaded_files[file_id] = {
        "id": file_id,
        "name": file.filename,
        "path": display_path,  # Full path with directory structure
        "content": content.decode("utf-8"),
        "size": len(content)
    }

    return {
        "id": file_id,
        "file_id": file_id,  # Alias for compatibility
        "file_name": file.filename,
        "filename": file.filename,  # Alias for compatibility
        "file_path": display_path,  # Path with directory structure
        "file_size": len(content),
        "status": "uploaded"
    }


@router.get("/list")
async def list_files():
    """Get list of all uploaded files with directory structure"""
    return {
        "files": [
            {
                "id": fid,
                "file_id": fid,  # Alias for compatibility
                "file_name": fdata["name"],
                "filename": fdata["name"],  # Alias for compatibility
                "file_path": fdata.get("path", fdata["name"]),  # Full path with directory
                "file_size": fdata["size"]
            }
            for fid, fdata in uploaded_files.items()
        ]
    }


@router.get("/{file_id}")
async def get_file(file_id: str):
    """Get file content by ID"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    return uploaded_files[file_id]


@router.delete("/{file_id}")
async def delete_file(file_id: str):
    """Delete uploaded file"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    del uploaded_files[file_id]
    return {"status": "deleted", "file_id": file_id}
