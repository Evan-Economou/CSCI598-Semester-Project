"""
System setup and configuration endpoints
"""
from fastapi import APIRouter
import os
from app.services.ollama_service import OllamaService

router = APIRouter()


@router.post("/check")
async def check_system():
    """
    Check if Ollama and CodeLlama are properly installed and configured
    """
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "codellama:7b")

    # Check actual Ollama connectivity
    ollama_service = OllamaService()
    ollama_running = await ollama_service.check_connection()
    model_available = False
    
    if ollama_running:
        model_available = await ollama_service.check_model()

    return {
        "ollama_configured": True,
        "ollama_host": ollama_host,
        "ollama_model": ollama_model,
        "ollama_running": ollama_running,
        "model_available": model_available,
        "status": "ready" if (ollama_running and model_available) else "not_ready",
        "message": _get_status_message(ollama_running, model_available)
    }


def _get_status_message(ollama_running: bool, model_available: bool) -> str:
    """Generate helpful status message"""
    if not ollama_running:
        return "Ollama is not running. Please start Ollama service."
    elif not model_available:
        return f"Ollama is running but CodeLlama model not found. Run: ollama pull codellama:7b"
    else:
        return "System ready for code analysis"


@router.get("/config")
async def get_configuration():
    """
    Get current system configuration
    """
    return {
        "ollama_host": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        "ollama_model": os.getenv("OLLAMA_MODEL", "codellama:7b"),
        "max_file_size_mb": os.getenv("MAX_FILE_SIZE_MB", "10"),
        "rag_enabled": True,
        "temperature": os.getenv("OLLAMA_TEMPERATURE", "0.3")
    }
