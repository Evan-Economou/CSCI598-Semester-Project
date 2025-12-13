# Code Style Grader - MVP Setup Guide

## Project Overview

An AI-powered code evaluation system for grading C++ assignments against custom style guides. This system combines a Python FastAPI backend with a React TypeScript frontend, utilizing Ollama with CodeLlama for AI analysis and ChromaDB for RAG capabilities.

## Tech Stack

### Backend
- **FastAPI** - Python web framework
- **Ollama** - Local LLM runtime
- **CodeLlama 7B** - Code analysis model
- **ChromaDB** - Vector database for RAG
- **Tree-sitter** - C++ syntax parsing
- **Sentence-Transformers** - Text embeddings

### Frontend
- **React** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Monaco Editor** - Code editor component
- **TailwindCSS** - Styling
- **Axios** - HTTP client

## Project Structure

```
CSCI598-Semester-Project/
├── backend/
│   ├── app/
│   │   ├── api/              # API route handlers
│   │   │   ├── files.py      # File upload/management
│   │   │   ├── analysis.py   # Code analysis endpoints
│   │   │   ├── setup.py      # System configuration
│   │   │   └── rag.py        # RAG document management
│   │   ├── services/         # Business logic
│   │   │   ├── ollama_service.py      # LLM integration
│   │   │   ├── style_guide_service.py # Style guide processing
│   │   │   └── rag_service.py         # RAG functionality
│   │   ├── parsers/          # Code parsing
│   │   │   ├── cpp_parser.py          # Tree-sitter parser
│   │   │   └── cpp_analyzer.py        # Main analysis engine
│   │   ├── models/           # Data models
│   │   │   └── core.py       # Pydantic schemas
│   │   ├── utils/            # Utility functions
│   │   └── main.py           # FastAPI application
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Environment configuration template
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── FileUploader.tsx
│   │   │   ├── CodeViewer.tsx
│   │   │   ├── ViolationPanel.tsx
│   │   │   └── RAGManager.tsx
│   │   ├── services/         # API communication
│   │   │   └── api.ts
│   │   ├── types/            # TypeScript types
│   │   │   └── index.ts
│   │   └── App.tsx           # Main application
│   ├── package.json          # Node dependencies
│   └── tsconfig.json         # TypeScript configuration
└── docs/                     # Documentation

```

## Phase 1 Setup Instructions

### Prerequisites

1. **Python 3.9+**
   - Download from [python.org](https://www.python.org/downloads/)

2. **Node.js 16+**
   - Download from [nodejs.org](https://nodejs.org/)

3. **Ollama**
   - Install from [ollama.ai](https://ollama.ai/)
   - After installation, pull CodeLlama model:
     ```bash
     ollama pull codellama:7b
     ```

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment:**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` file with your configuration

6. **Run the backend:**
   ```bash
   python -m app.main
   ```
   Or:
   ```bash
   uvicorn app.main:app --reload
   ```

   Backend will be available at `http://localhost:8000`

7. **Verify installation:**
   - Open browser to `http://localhost:8000/docs`
   - You should see the FastAPI Swagger documentation

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm start
   ```

   Frontend will be available at `http://localhost:3000`

### Verify Setup

1. **Check Ollama:**
   ```bash
   ollama list
   ```
   Verify `codellama:7b` is in the list

2. **Test backend:**
   - Visit `http://localhost:8000/health`
   - Should return JSON with system status

3. **Test frontend:**
   - Visit `http://localhost:3000`
   - Should see the Code Style Grader interface

## Development Workflow

### Running Both Services

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate  # Windows
python -m app.main
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### API Documentation

When the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Phase 1 MVP Features

### Backend (Implemented Skeleton)
- ✅ File upload endpoint (`POST /api/files/upload`)
- ✅ File list endpoint (`GET /api/files/list`)
- ✅ Analysis endpoint structure (`POST /api/analysis/analyze`)
- ✅ RAG document upload (`POST /api/rag/upload`)
- ✅ System health check (`GET /health`)

### Frontend (Implemented Skeleton)
- ✅ File upload interface with drag-drop
- ✅ File list sidebar
- ✅ Code viewer with syntax highlighting (Monaco Editor)
- ✅ Violation display panel
- ✅ RAG document management interface

### Still TODO for MVP (Week 1-2)

#### Backend
- [x] Implement actual Ollama integration ✅ **COMPLETED**
- [x] Implement LLM-powered code analysis ✅ **COMPLETED**
- [x] Create violation parsing and merging system ✅ **COMPLETED**
- [ ] Implement tree-sitter C++ parsing (advanced syntax analysis)
- [ ] Complete RAG service with ChromaDB (semantic search)
- [x] Implement style guide parser ✅ **COMPLETED**
- [x] Connect analysis pipeline (rule-based + LLM) ✅ **COMPLETED**
- [ ] Add async processing for batch analysis

#### Frontend
- [ ] Connect analysis workflow to backend
- [ ] Display LLM-generated violations in UI
- [ ] Implement violation highlighting in code editor
- [ ] Add analysis trigger button
- [ ] Add loading states and error handling
- [ ] Implement violation navigation (next/previous)

### Recent Updates (Ollama Integration)

#### ✅ LLM Integration Complete
The system now includes full Ollama + CodeLlama integration:

- **Two-phase analysis:** Rule-based + LLM semantic analysis
- **One-sentence descriptions:** Each violation gets a concise explanation
- **Smart merging:** Deduplicates violations from both sources
- **RAG-ready:** Structured to easily add RAG context in next phase

**See:** `OLLAMA_INTEGRATION.md` for detailed documentation

#### Quick Start with Ollama

1. **Install Ollama:**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Download CodeLlama:**
   ```bash
   ollama pull codellama:7b
   ```

3. **Start Ollama:**
   ```bash
   ollama serve
   ```

4. **Test the integration:**
   ```bash
   # Check system status
   curl -X POST http://localhost:8000/api/setup/check
   
   # Should return: "status": "ready"
   ```

## Testing the Current Skeleton

1. **Test file upload:**
   - Open frontend at `http://localhost:3000`
   - Click "Upload C++ Files"
   - Select a `.cpp` file
   - File should appear in the sidebar

2. **Test code viewer:**
   - Click on an uploaded file
   - Code should display in Monaco Editor

3. **Test RAG management:**
   - Click "RAG Management" tab
   - Upload a style guide (`.txt` file)
   - Document should appear in the list

## Troubleshooting

### Backend Issues

**Ollama not found:**
- Ensure Ollama is installed and running
- Check `ollama list` shows CodeLlama model
- Verify `OLLAMA_HOST` in `.env` is correct

**Import errors:**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

**Port already in use:**
- Change port in `.env` file
- Or stop other service using port 8000

### Frontend Issues

**Dependencies not installing:**
- Delete `node_modules/` and `package-lock.json`
- Run `npm install` again

**Monaco Editor not loading:**
- Clear browser cache
- Check browser console for errors

**API calls failing:**
- Verify backend is running
- Check proxy setting in `package.json`
- Verify CORS is configured in backend

## Next Steps (Week 1-2)

1. **Implement Ollama Service** (backend/app/services/ollama_service.py)
   - Test connection to Ollama
   - Implement prompt engineering for code analysis
   - Parse LLM responses into structured violations

2. **Implement Tree-sitter Parser** (backend/app/parsers/cpp_parser.py)
   - Set up tree-sitter C++ grammar
   - Implement syntax error detection
   - Extract code structure (functions, classes)

3. **Complete RAG Integration** (backend/app/services/rag_service.py)
   - Initialize ChromaDB
   - Implement document chunking
   - Implement semantic search

4. **Connect Frontend to Backend**
   - Wire up all API calls
   - Add error handling
   - Implement loading states

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Tree-sitter Documentation](https://tree-sitter.github.io/)
- [Monaco Editor](https://microsoft.github.io/monaco-editor/)
- [React Documentation](https://react.dev/)

## Support

For issues or questions:
1. Check the development plan (`development_plan.md`)
2. Check the specs (`code_grader_specs.md`)
3. Review API documentation at `http://localhost:8000/docs`
