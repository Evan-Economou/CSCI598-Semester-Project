# Quick Start Guide - Code Style Grader

## Prerequisites Checklist

- [ ] Python 3.9+ installed
- [ ] Node.js 16+ installed
- [ ] Ollama installed ([ollama.ai](https://ollama.ai/))
- [ ] CodeLlama model pulled: `ollama pull codellama:7b`

## Setup (First Time Only)

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

### 2. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install
```

## Running the Application

### Option 1: Run Both Services (Recommended)

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
python run.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### Option 2: Manual Start

**Backend:**
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm start
```

## Access the Application

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

## Verify Installation

1. **Check Ollama:**
   ```bash
   ollama list
   ```
   Should show `codellama:7b`

2. **Check Backend Health:**
   Visit: http://localhost:8000/health

   Should return:
   ```json
   {
     "status": "healthy",
     "ollama_configured": true
   }
   ```

3. **Check Frontend:**
   Visit: http://localhost:3000
   Should see the Code Style Grader interface

## Test the MVP Skeleton

### 1. Upload a C++ File
- Click "Upload C++ Files" in the left sidebar
- Select a `.cpp`, `.hpp`, or `.h` file
- File appears in the file list

### 2. View Code
- Click on the uploaded file
- Code displays in the Monaco Editor (center panel)

### 3. Upload Style Guide
- Click "RAG Management" tab
- Select "Style Guide" as document type
- Upload a `.txt` file with style guide rules
- Document appears in the list

## Current MVP Status

✅ **Working:**
- File upload and storage
- File viewing with syntax highlighting
- Basic UI layout
- API endpoint structure
- RAG document upload

⚠️ **TODO (Week 1-2):**
- Actual code analysis with Ollama
- Tree-sitter C++ parsing
- RAG semantic search
- Violation detection and display
- Analysis workflow integration

## Common Issues

### Backend won't start
- Ensure virtual environment is activated
- Check Python version: `python --version` (must be 3.9+)
- Reinstall dependencies: `pip install -r requirements.txt`

### Frontend won't start
- Delete `node_modules/` and run `npm install`
- Check Node version: `node --version` (must be 16+)

### Ollama connection fails
- Ensure Ollama is running: `ollama list`
- Check `OLLAMA_HOST` in `.env` is correct
- Default: `http://localhost:11434`

### Port conflicts
- Change backend port in `.env`: `PORT=8001`
- Update frontend proxy in `package.json`

## Next Steps

See `README_PROJECT.md` for:
- Detailed project structure
- Development workflow
- Phase 1 implementation tasks
- Full documentation

## Getting Help

1. Check `README_PROJECT.md` for detailed setup
2. Review API docs at http://localhost:8000/docs
3. Check `development_plan.md` for implementation roadmap
4. Review `code_grader_specs.md` for requirements
