# Code Style Grader - AI-Powered C++ Code Analysis Tool

**An educational tool that combines algorithmic static analysis with Large Language Model intelligence to automatically grade student C++ code against customizable style guidelines.**

---

## 📋 Table of Contents

1. [Project Summary](#-project-summary)
2. [Installation Guide](#-installation-guide)
3. [Quick Start](#-quick-start)

---

## 🎯 Project Summary

The **Code Style Grader** is a web-based application designed to help educators efficiently grade student C++ assignments by automatically detecting style violations. The system uses a **two-tier analysis architecture**:

### Two-Tier Analysis

1. **Tier 1: Built-in Algorithmic Checks** (Fast, Deterministic)
   - Indentation validation (mixed tabs/spaces, incorrect nesting)
   - Line length enforcement
   - Missing braces on control structures
   - Memory leak detection (new/delete matching)
   - Naming conventions (camelCase, PascalCase)
   - NULL vs nullptr usage

2. **Tier 2: LLM Semantic Analysis** (Intelligent, Context-Aware)
   - Comment quality assessment
   - Complex semantic issues
   - Code structure analysis

### Why This Approach?

- **Speed**: Algorithmic checks are instant (~0.5 seconds)
- **Accuracy**: Rule-based checks have 100% precision
- **Intelligence**: LLM adds contextual understanding for nuanced issues
- **Privacy**: All analysis runs locally - no cloud APIs, no data transmission
- **Cost**: Zero API fees - uses local Ollama + CodeLlama 7B

### Key Features

✅ **Analysis Capabilities:**
- Many violation types detected automatically
- Color-coded severity levels (🔴 CRITICAL, 🟠 WARNING, 🔵 MINOR)
- Customizable style guidelines via plain-text files

✅ **User Interface:**
- Monaco Editor (same as VS Code) with syntax highlighting
- Violation highlighting with hover tooltips
- File tree for navigating submissions
- Detailed violation panel with line references

---

## 🚀 Installation Guide

### Prerequisites

Verify you have the required software:

```bash
# Check Python version (3.11+ required)
python --version

# Check Node.js version (16+ required)
node --version

# Check npm version (8+ required)
npm --version
```

If any are missing or outdated, install them first:
- **Python 3.11+**: https://www.python.org/downloads/
- **Node.js 16+**: https://nodejs.org/

---

### Step 1: Install Ollama and CodeLlama Model

Ollama provides the local LLM infrastructure for semantic analysis.

1. Download Ollama from https://ollama.com/download
2. Run the installer (OllamaSetup.exe)
3. Open Command Prompt or PowerShell
4. Pull the CodeLlama model:
   ```bash
   ollama pull codellama:7b
   ```
5. Verify installation:
   ```bash
   ollama list
   ```
   You should see `codellama:7b` in the list (~3.8GB download)

---

### Step 2: Clone the Repository

```bash
cd C:\Users\YourUsername\Desktop  # or your preferred directory
git clone <repository-url>
cd CSCI598-Semester-Project
```

---

### Step 3: Backend Setup (Python/FastAPI)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

### Step 4: Frontend Setup (React/TypeScript)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

---

## ⚡ Quick Start

### Running the Application

You'll need **THREE terminal windows** to run all services:

#### Terminal 1: Start Ollama Service

```bash
ollama serve
```

**Leave this running.** You should see:
```
Ollama is running on http://localhost:11434
```

#### Terminal 2: Start Backend Server

```bash
# Navigate to backend
cd backend

# Activate virtual environment
venv\Scripts\activate

# Start backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Leave this running.** You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

#### Terminal 3: Start Frontend

```bash
# Navigate to frontend
cd frontend

# Start React development server
npm start
```

**Your browser should automatically open to http://localhost:3000**

---

### Using the Application (High-Level Overview)

Once all three services are running, follow these steps:

#### 1. Upload Style Guide
- Click the **Style Guide dropdown** in the top control bar
- Select **"📁 Upload New Style Guide..."**
- Navigate to `$(project_directory)/semantic_style_guide.txt`
- Upload the file
- The dropdown should now show "semantic_style_guide.txt" as selected

#### 2. Upload Student Submission
- Click **"📁 Upload Files"** in the left sidebar
- **Important**: You must select a **folder**, not individual files
- Navigate to and select the `test_files/` folder
- All `.cpp` files will appear in the file tree on the left

#### 3. Run Analysis and View Results
- Click on any file in the tree (e.g., `test_algorithmic.cpp`)
- The file content will appear in the Monaco editor (center panel)
- Click the **"Run Analysis"** button in the top control bar
- Wait 1-2 seconds for analysis to complete
- **View Results:**
  - Violations appear in the right panel with severity levels
  - Code highlights appear in the editor:
    - 🔴 Red background = CRITICAL
    - 🟠 Amber background = WARNING
    - 🔵 Blue background = MINOR
  - Hover over highlighted lines to see violation details
  - Click on violations in the right panel to jump to that line

---

### Test Files Overview

The `test_files/` directory contains examples demonstrating a breadth of capabilities:

| File | Demonstrates |
|------|--------------|
| `test_algorithmic.cpp` | Mixed tabs/spaces, missing braces |
| `test_semantic.cpp` | Memory leaks, naming conventions, NULL vs nullptr |
| `test_comment_quality.cpp` | Improper indentation detection |
| `test_clean.cpp` | Clean code example (gold standard) |
| `test_no_comments.cpp` | Missing comments violation |

**Recommended Test Sequence:**
1. Start with `test_algorithmic.cpp` (basic formatting checks)
2. Try `test_semantic.cpp` (LLM-detected memory leaks)
3. Test `test_clean.cpp` (clean code example)
4. Experiment with `test_no_comments.cpp` (CRITICAL severity)

---

### Troubleshooting

**If the browser doesn't open automatically:**
- Manually navigate to http://localhost:3000

**If you see connection errors:**
- Verify all three terminals are still running
- Check Ollama: http://localhost:11434 (should show "Ollama is running")
- Check Backend: http://127.0.0.1:8000/docs (should show API documentation)
- Check Frontend: http://localhost:3000 (should show the application)

**If analysis is slow (>10 seconds):**
- This is normal due to Ollama response time

**For detailed documentation:**
- See `GRADING_GUIDE.md` for a 10-minute walkthrough with expected outputs
- See `PROJECT_SUMMARY.md` for comprehensive technical details
- See `test_files/TEST_DOCUMENTATION.md` for detailed test file explanations

---

## 📁 Project Structure

```
CSCI598-Semester-Project/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── main.py         # API endpoints
│   │   ├── models.py       # Data models
│   │   ├── parsers/        # Algorithmic analyzers
│   │   └── llm/            # LLM integration
│   └── requirements.txt    # Python dependencies
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── App.tsx         # Main application
│   │   ├── components/     # UI components
│   │   └── services/       # API client
│   └── package.json        # Node dependencies
├── style_guides/           # Style guide files
│   └── semantic_style_guide.txt
└── test_files/             # Test C++ files
    ├── test_algorithmic.cpp
    ├── test_semantic.cpp
    ├── test_comment_quality.cpp
    ├── test_clean.cpp
    └── test_no_comments.cpp
```

---

**Built with**: FastAPI, React, TypeScript, Monaco Editor, Ollama, CodeLlama 7B

**License**: Educational use - CSCI 598 Semester Project
