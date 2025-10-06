"""
Code analysis endpoints
"""
from fastapi import APIRouter, HTTPException
from app.models.core import AnalysisRequest, AnalysisResult
from app.parsers.cpp_analyzer import CppAnalyzer
from app.api.files import uploaded_files
from app.api.rag import rag_documents

router = APIRouter()

# Initialize analyzer
analyzer = CppAnalyzer()


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_code(request: AnalysisRequest):
    """
    Analyze uploaded C++ file for style violations

    This endpoint will:
    1. Retrieve the file from storage
    2. Retrieve the style guide from RAG storage
    3. Run basic C++ analysis (text-based heuristics)
    4. Return violations with details
    """
    # Retrieve uploaded file
    if request.file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_id}")

    file_data = uploaded_files[request.file_id]
    file_content = file_data["content"]
    file_name = file_data["name"]

    # Retrieve style guide
    if not request.style_guide_id:
        raise HTTPException(status_code=400, detail="Style guide ID is required")

    if request.style_guide_id not in rag_documents:
        raise HTTPException(status_code=404, detail=f"Style guide not found: {request.style_guide_id}")

    style_guide_data = rag_documents[request.style_guide_id]
    style_guide_content = style_guide_data["content"]

    # Run analysis
    try:
        result = await analyzer.analyze_file(
            file_content=file_content,
            file_name=file_name,
            file_path=file_name,  # Use filename as path for MVP
            style_guide=style_guide_content,
            use_rag=request.use_rag
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/results/{analysis_id}")
async def get_analysis_results(analysis_id: str):
    """
    Retrieve analysis results by ID
    (Not implemented in MVP - analysis is synchronous)
    """
    raise HTTPException(status_code=501, detail="Not yet implemented - use synchronous /analyze endpoint")


@router.get("/status/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """
    Check analysis progress status
    (Not implemented in MVP - analysis is synchronous)
    """
    return {
        "analysis_id": analysis_id,
        "status": "not_implemented",
        "message": "Use synchronous /analyze endpoint for MVP"
    }
