# Development Plan - Code Style Grader (Accelerated Timeline)

## Technical Architecture Decisions

### Core Technology Stack
- **Local LLM**: Ollama with CodeLlama 7B (specialized for code analysis)
- **Vector Database**: ChromaDB (lightweight, embedded, cross-platform)
- **Backend**: FastAPI (Python) with async processing
- **Frontend**: React with TypeScript
- **Deployment**: PyInstaller + Electron wrapper for cross-platform executable
- **Code Analysis**: Tree-sitter for C++ parsing + LLM for semantic analysis

### Project Structure
```
code-style-grader/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/                 # FastAPI routes
│   │   ├── services/            # Core business logic
│   │   ├── models/              # Data models
│   │   ├── parsers/             # C++ syntax & semantic analysis
│   │   └── utils/
│   ├── requirements.txt
│   └── build_exe.py            # PyInstaller script
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── utils/
│   ├── package.json
│   └── electron/               # Electron wrapper
├── installer/                  # Cross-platform installer scripts
└── docs/
```

---

## ACCELERATED TIMELINE: 4 Weeks Total

### Week 1-2: MVP Development (Parallel Teams)
**Goal**: Working prototype with core functionality

### Week 3-4: Full Feature Implementation + Deployment
**Goal**: Production-ready application with installer

---

## WEEK 1-2: MVP SPRINT

### Backend MVP (Week 1-2)
**MVP Deliverables:**
- Basic file upload and C++ parsing
- Ollama integration with CodeLlama
- Simple style guide processing
- Core analysis pipeline
- REST API for frontend communication

#### Day 1-2: Environment & Core Setup
**Technical Implementation:**
```python
# requirements.txt (MVP)
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
pydantic==2.5.0
tree-sitter==0.20.4
tree-sitter-cpp==0.23.4
ollama==0.1.7
chromadb==0.4.18
python-dotenv==1.0.0
```

**Core Files to Implement:**
1. **`app/main.py`** - FastAPI app with CORS
2. **`app/services/ollama_service.py`** - Ollama integration
3. **`app/parsers/cpp_parser.py`** - Tree-sitter C++ parsing
4. **`app/models/core.py`** - Pydantic models

```python
# Key MVP API Endpoints:
POST /api/files/upload          # Single file upload
POST /api/analysis/analyze      # Analyze uploaded file
GET /api/analysis/results/{id}  # Get analysis results
POST /api/setup/check           # Check Ollama installation
```

#### Day 3-4: C++ Analysis Engine
**File: `app/parsers/cpp_analyzer.py`**
```python
class CppAnalyzer:
    def __init__(self):
        self.tree_sitter_parser = TreeSitterParser()
        self.ollama_client = OllamaClient()
    
    def analyze_file(self, file_content: str, style_guide: str):
        # 1. Syntax analysis with tree-sitter
        syntax_issues = self.tree_sitter_parser.find_issues(file_content)
        
        # 2. Semantic analysis with CodeLlama
        semantic_violations = self.ollama_client.analyze_code(
            code=file_content, 
            style_guide=style_guide
        )
        
        return self.merge_violations(syntax_issues, semantic_violations)
```

**Key Components:**
- Tree-sitter integration for syntax parsing
- Ollama prompt engineering for code analysis
- Basic violation detection and classification
- Simple style guide text parsing

#### Day 5-7: Style Guide Processing & API
**File: `app/services/style_guide_service.py`**
```python
class StyleGuideProcessor:
    def parse_style_guide(self, content: str):
        # Parse severity sections (CRITICAL, WARNING, MINOR)
        sections = self._extract_sections(content)
        rules = self._extract_rules(sections)
        return self._structure_rules(rules)
```

**API Implementation:**
- File upload handling with validation
- Analysis queue management
- Result storage and retrieval
- Error handling and status reporting

### Frontend MVP (Week 1-2)
**MVP Deliverables:**
- File upload interface
- Basic code viewer with syntax highlighting
- Violation display panel
- Simple analysis workflow

#### Day 1-2: React Setup & Core Components
**Setup:**
```bash
npx create-react-app frontend --template typescript
npm install @monaco-editor/react axios lucide-react
npm install @tailwindcss/forms tailwindcss
```

**Core Components Structure:**
```tsx
src/
├── components/
│   ├── FileUploader.tsx        # Drag-drop file upload
│   ├── CodeViewer.tsx          # Monaco editor with highlighting
│   ├── ViolationPanel.tsx      # Show analysis results
│   └── AnalysisStatus.tsx      # Processing status
├── services/
│   └── api.ts                  # Backend communication
└── App.tsx                     # Main application
```

#### Day 3-4: File Management & Code Display
**Key Features:**
1. **FileUploader Component**
   - Drag-and-drop C++ files
   - File validation (.cpp, .hpp, .h)
   - Upload progress indication

2. **CodeViewer Component**
   ```tsx
   import Editor from '@monaco-editor/react';
   
   function CodeViewer({ code, violations }) {
     return (
       <Editor
         language="cpp"
         value={code}
         options={{ readOnly: true, lineNumbers: 'on' }}
         onMount={handleEditorMount}
       />
     );
   }
   ```

#### Day 5-7: Analysis Interface & Results
**Features:**
1. **Analysis Workflow**
   - Upload file → Start analysis → Show progress → Display results
   - Basic error handling and user feedback

2. **Violation Display**
   - List violations with severity color coding
   - Click violation to jump to line in code
   - Basic violation details (type, description, line number)

---

## WEEK 3-4: FULL FEATURE IMPLEMENTATION

### Backend Full Features (Week 3-4)

#### Week 3: RAG System & Advanced Analysis
**Day 1-3: RAG Implementation**
```python
# Additional requirements
sentence-transformers==2.2.2
numpy==1.24.3
```

**File: `app/services/rag_service.py`**
```python
class RAGService:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path="./rag_data")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
    def add_document(self, content: str, doc_type: str):
        chunks = self._chunk_document(content)
        embeddings = self.embedder.encode(chunks)
        self.chroma_client.add(embeddings=embeddings, documents=chunks)
    
    def search_relevant_context(self, query: str, top_k=3):
        query_embedding = self.embedder.encode([query])
        results = self.chroma_client.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
        return results['documents'][0]
```

**Day 4-7: Enhanced Analysis Pipeline**
- Batch file processing
- Progress tracking with WebSocket updates
- Enhanced Ollama prompting with RAG context
- Violation confidence scoring

#### Week 4: Performance & Deployment Prep
**Day 1-4: Optimization & Testing**
- Async processing for multiple files
- Memory optimization for large codebases
- Comprehensive error handling
- Unit and integration tests

**Day 5-7: Deployment Preparation**
```python
# build_exe.py - PyInstaller configuration
import PyInstaller.__main__

PyInstaller.__main__.run([
    'app/main.py',
    '--onefile',
    '--add-data', 'rag_data;rag_data',
    '--hidden-import', 'chromadb',
    '--hidden-import', 'tree_sitter',
    '--name', 'code-grader-backend',
    '--distpath', 'dist'
])
```

### Frontend Full Features (Week 3-4)

#### Week 3: Advanced UI & RAG Management
**Day 1-3: RAG Document Management**
```tsx
// components/RAGManager.tsx
function RAGManager() {
  return (
    <div className="rag-panel">
      <DocumentUploader onUpload={handleDocumentUpload} />
      <DocumentList documents={documents} onDelete={handleDelete} />
      <StyleGuideEditor value={styleGuide} onChange={setStyleGuide} />
    </div>
  );
}
```

**Day 4-7: Enhanced Code Viewer**
- Violation highlighting with Monaco decorations
- Violation navigation (next/previous buttons)
- Multiple file tabs
- Search within code functionality

#### Week 4: Polish & Electron Wrapper
**Day 1-3: UI Polish & Export**
- Results export to JSON
- Print-friendly reports
- Advanced violation filtering
- Keyboard shortcuts and accessibility

**Day 4-7: Electron Packaging**
```javascript
// electron/main.js
const { app, BrowserWindow, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let backendProcess;

function createWindow() {
  // Start Python backend as subprocess
  backendProcess = spawn('code-grader-backend.exe', [], {
    cwd: path.join(__dirname, '../backend/dist')
  });
  
  // Create browser window
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  });
  
  mainWindow.loadURL('http://localhost:3000');
}
```

---

## DEPLOYMENT STRATEGY

### Cross-Platform Executable Creation

#### Backend Executable (PyInstaller)
```bash
# Build script for backend
pip install pyinstaller
python build_exe.py

# Result: Single executable containing:
# - FastAPI backend
# - Ollama integration
# - ChromaDB embedded
# - All Python dependencies
```

#### Frontend Executable (Electron)
```bash
# Build script for frontend
npm install electron electron-builder
npm run build
npm run electron-pack

# Result: Electron app containing:
# - React frontend (built)
# - Embedded backend executable
# - Auto-start backend on app launch
```

#### Installer Creation
```bash
# Windows: NSIS installer
# Linux: AppImage or .deb package
# Cross-platform: electron-builder handles both

npm run dist  # Creates installers for current platform
```

### Installation Requirements
1. **Ollama**: Installer should check and auto-install Ollama
2. **CodeLlama Model**: Auto-download CodeLlama 7B on first run
3. **Permissions**: Ensure proper file system permissions

### Installation Flow
```bash
# 1. User runs installer
# 2. Installer extracts application
# 3. First launch checks dependencies:
#    - Ollama installation
#    - CodeLlama model download
#    - RAG database initialization
# 4. Application ready for use
```

---

## DEVELOPMENT WORKFLOW

### Week 1-2 Daily Standup Points
- **Backend Focus**: Can frontend upload files and get analysis results?
- **Frontend Focus**: Can user upload file and see basic analysis?
- **Integration**: Are API contracts working as expected?

### Week 3-4 Daily Standup Points
- **Backend Focus**: Are advanced features working with real C++ files?
- **Frontend Focus**: Is the user experience smooth and intuitive?
- **Integration**: Is the full workflow working end-to-end?

### Critical Success Metrics
- **Week 2**: Can analyze a simple C++ file and show violations
- **Week 4**: Can deploy as executable and analyze real student code

---

## RISK MITIGATION

### Technical Risks & Solutions
1. **Ollama Installation Issues**
   - Fallback: Bundle Ollama with installer
   - Alternative: Provide manual installation guide

2. **Large File Performance**
   - Solution: Implement file size limits (max 10MB per file)
   - Optimization: Stream processing for large files

3. **Cross-Platform Compatibility**
   - Solution: Test on both Windows and Linux throughout development
   - CI/CD: Set up automated builds for both platforms

### Timeline Risks & Solutions
1. **MVP Delay Risk**
   - Mitigation: Focus on core analysis pipeline first
   - Fallback: Reduce MVP scope to single file analysis only

2. **Integration Complexity**
   - Mitigation: Daily integration testing
   - Solution: Mock services for independent development

### Quality Assurance
- **Week 2**: Test with sample C++ files from real assignments
- **Week 4**: User acceptance testing with educators
- **Continuous**: Automated testing for core functionality

This accelerated plan delivers a working MVP in 2 weeks and a production-ready application in 4 weeks, with clear parallel development paths for frontend and backend teams.