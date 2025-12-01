import React, { useEffect, useState, useMemo, useRef } from 'react';
import FileUploader from './components/FileUploader';
import CodeViewer from './components/CodeViewer';
import ViolationPanel from './components/ViolationPanel';
import { AnalysisResult, UploadedFile, FileTreeNode } from './types';
import { analyzeCode, listRAGDocuments, uploadRAGDocument } from './services/api';
import { buildFileTree, removeFileFromTree } from './utils/fileTreeUtils';

function App() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<UploadedFile | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [styleGuides, setStyleGuides] = useState<any[]>([]);
  const [selectedGuideId, setSelectedGuideId] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState<boolean>(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const styleGuideInputRef = useRef<HTMLInputElement>(null);

  // Build file tree from flat list
  const fileTree = useMemo(() => buildFileTree(uploadedFiles), [uploadedFiles]);

  const handleFileUpload = (files: UploadedFile[]) => {
    setUploadedFiles(prev => [...prev, ...files]);
    if (files.length > 0 && !selectedFile) {
      setSelectedFile(files[0]);
    }
  };

  const handleFileSelect = (node: FileTreeNode) => {
    if (node.type === 'file' && node.file_id) {
      // Find the full file object
      const file = uploadedFiles.find(f => f.file_id === node.file_id);
      if (file) {
        setSelectedFile(file);
      }
    }
  };

  const handleFileDelete = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => {
      const id = (f as any).id || (f as any).file_id;
      return id !== fileId;
    }));
    // Clear selection if the deleted file was selected
    if (selectedFile) {
      const selectedId = (selectedFile as any).id || (selectedFile as any).file_id;
      if (selectedId === fileId) {
        setSelectedFile(null);
        setAnalysisResult(null);
      }
    }
  };

  // Load style guides on mount
  const loadGuides = async () => {
    try {
      const resp = await listRAGDocuments();
      const docs = Array.isArray(resp) ? resp : resp?.documents ?? [];
      const guides = docs.filter((d: any) => (d.type ?? d.doc_type) === 'style_guide');
      setStyleGuides(guides);
      if (!selectedGuideId && guides.length > 0) {
        const firstId = guides[0].id ?? guides[0].doc_id;
        setSelectedGuideId(firstId || null);
      }
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    loadGuides();
  }, []);

  const handleStyleGuideUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      await uploadRAGDocument(file, 'style_guide');
      await loadGuides(); // Reload guides after upload
      if (styleGuideInputRef.current) {
        styleGuideInputRef.current.value = ''; // Reset input
      }
    } catch (err: any) {
      alert('Failed to upload style guide: ' + (err.message || 'Unknown error'));
    }
  };

  const handleStyleGuideSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    if (value === '__upload__') {
      styleGuideInputRef.current?.click();
    } else {
      setSelectedGuideId(value || null);
    }
  };

  const runAnalysis = async () => {
    setAnalysisError(null);
    if (!selectedFile || !selectedGuideId) {
      setAnalysisError('Select a file and a style guide.');
      return;
    }
    setAnalyzing(true);
    try {
      const fileId = (selectedFile as any).id ?? (selectedFile as any).file_id;
      const result = await analyzeCode(fileId, selectedGuideId, true); // Always use RAG
      setAnalysisResult(result as any);
    } catch (e: any) {
      setAnalysisError(e?.message || 'Failed to run analysis.');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gray-900 text-gray-100">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <h1 className="text-2xl font-bold text-white">Code Style Grader</h1>
        <p className="text-sm text-gray-400">AI-powered C++ code analysis</p>
      </header>

      {/* Analysis Controls */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-3">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-300">Style Guide</label>
            <select
              className="bg-gray-900 border border-gray-700 text-gray-100 text-sm rounded px-2 py-1"
              value={selectedGuideId ?? ''}
              onChange={handleStyleGuideSelect}
            >
              <option value="">Select style guide...</option>
              {styleGuides.map((g: any) => {
                const id = g.id || g.doc_id;
                const name = g.name || g.filename || 'Style Guide';
                return (
                  <option key={id} value={id}>
                    {name}
                  </option>
                );
              })}
              <option value="__upload__">📁 Upload New Style Guide...</option>
            </select>
            <input
              ref={styleGuideInputRef}
              type="file"
              accept=".txt,.md"
              onChange={handleStyleGuideUpload}
              className="hidden"
            />
          </div>

          <button
            onClick={runAnalysis}
            disabled={analyzing || !selectedFile || !selectedGuideId}
            className={`px-3 py-1 rounded text-sm ${
              analyzing || !selectedGuideId
                ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-500 text-white'
            }`}
          >
            {analyzing ? 'Analyzing…' : 'Run Analysis'}
          </button>

          {analysisError && (
            <span className="text-red-400 text-sm">{analysisError}</span>
          )}
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - File Manager */}
        <aside className="w-64 bg-gray-800 border-r border-gray-700 overflow-y-auto">
          <FileUploader
            onFileUpload={handleFileUpload}
            fileTree={fileTree}
            selectedFile={selectedFile}
            onFileSelect={handleFileSelect}
            onFileDelete={handleFileDelete}
          />
        </aside>

        {/* Center - Code Viewer */}
        <section className="flex-1 flex flex-col overflow-hidden">
          <CodeViewer file={selectedFile} analysisResult={analysisResult} />
        </section>

        {/* Right Sidebar - Violation Details */}
        <aside className="w-96 bg-gray-800 border-l border-gray-700 overflow-y-auto">
          <ViolationPanel analysisResult={analysisResult} />
        </aside>
      </main>
    </div>
  );
}

export default App;

