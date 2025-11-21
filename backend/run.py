"""
Convenience script to run the backend server
"""
import os

try:
    import uvicorn
except ModuleNotFoundError:
    import sys
    import subprocess
    print("\nERROR: Failed to import 'uvicorn'. Diagnostic information:\n")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}\n")
    print("sys.path:")
    for p in sys.path:
        print(f"  {p}")
    print("\nContents of backend/venv/bin (first 40 entries):")
    try:
        for i, name in enumerate(sorted(os.listdir(os.path.join(os.path.dirname(__file__), '..', 'venv', 'bin')))):
            if i >= 40:
                break
            print(f"  {name}")
    except Exception:
        pass
    print("\nInstalled packages (via pip):")
    try:
        out = subprocess.check_output([sys.executable, "-m", "pip", "list"], text=True)
        print(out)
    except Exception as e:
        print(f"  (failed to run pip list: {e})")
    raise

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
