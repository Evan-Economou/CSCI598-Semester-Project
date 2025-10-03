"""
System setup and configuration endpoints
"""
from fastapi import APIRouter
import os

router = APIRouter()


@router.post("/check")
async def check_system():
    """
    Check if Ollama and CodeLlama are properly installed and configured
    """
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "codellama:7b")

    # TODO: Actually check Ollama connectivity
    # For now, return configuration info

    return {
        "ollama_configured": ollama_host is not None,
        "ollama_host": ollama_host,
        "ollama_model": ollama_model,
        "status": "check_not_implemented"
    }


@router.get("/config")
async def get_configuration():
    """
    Get current system configuration
    """
    return {
        "ollama_host": os.getenv("OLLAMA_HOST"),
        "ollama_model": os.getenv("OLLAMA_MODEL"),
        "max_file_size_mb": os.getenv("MAX_FILE_SIZE_MB", "10"),
        "rag_enabled": True
    }
