"""
Convenience script to run the backend server
"""
import uvicorn
import os

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))

    print(f"""
==============================================
  Code Style Grader - Backend Server
==============================================

Starting server at http://{host}:{port}

API Documentation:
- Swagger UI: http://localhost:{port}/docs
- ReDoc:      http://localhost:{port}/redoc

Press CTRL+C to stop the server
""")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
