# Code Style Grader - Frontend

React TypeScript frontend for code analysis interface.

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm start
   ```

   Opens at http://localhost:3000

3. **Build for production:**
   ```bash
   npm run build
   ```

## Features

### Code Analysis Tab
- Upload C++ files (.cpp, .hpp, .h)
- View code with syntax highlighting (Monaco Editor)
- See violations with severity levels
- Navigate between files

### RAG Management Tab
- Upload style guides
- Upload reference documents
- Manage knowledge base

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── FileUploader.tsx
│   │   ├── CodeViewer.tsx
│   │   ├── ViolationPanel.tsx
│   │   └── RAGManager.tsx
│   ├── services/         # API client
│   │   └── api.ts
│   ├── types/            # TypeScript types
│   │   └── index.ts
│   ├── App.tsx           # Main app
│   └── index.tsx         # Entry point
└── package.json
```

## Development

### Available Scripts

- `npm start` - Run dev server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

### Environment Variables

Create `.env.local`:
```
REACT_APP_API_URL=http://localhost:8000/api
```

## Components

### FileUploader
- Drag-and-drop file upload
- File list display
- File selection

### CodeViewer
- Monaco Editor integration
- C++ syntax highlighting
- Line numbers
- Violation markers (TODO)

### ViolationPanel
- Severity breakdown
- Violation list
- Click to jump to line (TODO)

### RAGManager
- Document upload
- Document list
- Document deletion
