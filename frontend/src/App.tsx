import React, { useEffect, useState, useMemo } from 'react';
import FileUploader from './components/FileUploader';
import CodeViewer from './components/CodeViewer';
import ViolationPanel from './components/ViolationPanel';
import RAGManager from './components/RAGManager';
import { AnalysisResult, UploadedFile, FileTreeNode } from './types';
import { analyzeCode, listRAGDocuments } from './services/api';
import { buildFileTree, removeFileFromTree } from './utils/fileTreeUtils';

function App() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<UploadedFile | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [activeTab, setActiveTab] = useState<'analysis' | 'rag'>('analysis');
  const [styleGuides, setStyleGuides] = useState<any[]>([]);
  const [selectedGuideId, setSelectedGuideId] = useState<string | null>(null);
  const [useRag, setUseRag] = useState<boolean>(false);
  const [analyzing, setAnalyzing] = useState<boolean>(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

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

  useEffect(() => {
    // Load style guides when Analysis tab is active
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
    if (activeTab === 'analysis') {
      loadGuides();
    }
  }, [activeTab, selectedGuideId]);

  const runAnalysis = async () => {
    setAnalysisError(null);
    if (!selectedFile || !selectedGuideId) {
      setAnalysisError('Select a file and a style guide.');
      return;
    }
    setAnalyzing(true);
    try {
      const fileId = (selectedFile as any).id ?? (selectedFile as any).file_id;
      const result = await analyzeCode(fileId, selectedGuideId, useRag);
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

      {/* Tabs + Analysis Controls */}
      <div className="bg-gray-800 border-b border-gray-700 px-6">
        <div className="flex items-center justify-between gap-4">
          {/* Tabs */}
          <div className="flex space-x-4">
            <button
              onClick={() => setActiveTab('analysis')}
              className={`px-4 py-2 font-medium border-b-2 transition-colors ${
                activeTab === 'analysis'
                  ? 'border-blue-500 text-blue-500'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
            >
              Code Analysis
            </button>
            <button
              onClick={() => setActiveTab('rag')}
              className={`px-4 py-2 font-medium border-b-2 transition-colors ${
                activeTab === 'rag'
                  ? 'border-blue-500 text-blue-500'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
            >
              RAG Management
            </button>
          </div>

          {/* Analysis controls (only on Analysis tab) */}
          {activeTab === 'analysis' && (
            <div className="flex items-center gap-3 py-2">
              <div className="flex items-center gap-2">
                <label className="text-sm text-gray-300">Style Guide</label>
                <select
                  className="bg-gray-900 border border-gray-700 text-gray-100 text-sm rounded px-2 py-1"
                  value={selectedGuideId ?? ''}
                  onChange={(e) => setSelectedGuideId(e.target.value || null)}
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
                </select>
              </div>

              <label className="flex items-center gap-2 text-sm text-gray-300">
                <input
                  type="checkbox"
                  className="form-checkbox rounded text-blue-500"
                  checked={useRag}
                  onChange={(e) => setUseRag(e.target.checked)}
                />
                Use RAG
              </label>

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
          )}
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden">
        {activeTab === 'analysis' ? (
          <>
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
          </>
        ) : (
          <section className="flex-1 overflow-auto">
            <RAGManager />
          </section>
        )}
      </main>
    </div>
  );
}

export default App;

