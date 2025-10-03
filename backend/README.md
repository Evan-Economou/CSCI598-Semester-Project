# Code Style Grader - Backend

Python FastAPI backend for AI-powered C++ code analysis.

## Quick Start

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment:**
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run server:**
   ```bash
   python -m app.main
   ```

   Or with auto-reload:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Endpoints

### Files
- `POST /api/files/upload` - Upload C++ file
- `GET /api/files/list` - List uploaded files
- `GET /api/files/{file_id}` - Get file content
- `DELETE /api/files/{file_id}` - Delete file

### Analysis
- `POST /api/analysis/analyze` - Analyze code
- `GET /api/analysis/results/{analysis_id}` - Get results
- `GET /api/analysis/status/{analysis_id}` - Check status

### RAG
- `POST /api/rag/upload` - Upload RAG document
- `GET /api/rag/documents` - List documents
- `DELETE /api/rag/documents/{doc_id}` - Delete document

### Setup
- `POST /api/setup/check` - Check system setup
- `GET /api/setup/config` - Get configuration

## Development

### Project Structure
```
backend/
├── app/
│   ├── api/              # API endpoints
│   ├── services/         # Business logic
│   ├── parsers/          # Code parsing
│   ├── models/           # Data models
│   └── main.py           # FastAPI app
└── requirements.txt
```

### Testing

```bash
pytest
```

### API Documentation

When running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
