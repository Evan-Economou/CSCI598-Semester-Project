import React, { useState } from 'react';
import FileUploader from './components/FileUploader';
import CodeViewer from './components/CodeViewer';
import ViolationPanel from './components/ViolationPanel';
import RAGManager from './components/RAGManager';
import { AnalysisResult, UploadedFile } from './types';

function App() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<UploadedFile | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [activeTab, setActiveTab] = useState<'analysis' | 'rag'>('analysis');

  const handleFileUpload = (files: UploadedFile[]) => {
    setUploadedFiles(prev => [...prev, ...files]);
    if (files.length > 0 && !selectedFile) {
      setSelectedFile(files[0]);
    }
  };

  const handleFileSelect = (file: UploadedFile) => {
    setSelectedFile(file);
    // TODO: Trigger analysis for selected file
  };

  return (
    <div className="h-screen flex flex-col bg-gray-900 text-gray-100">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <h1 className="text-2xl font-bold text-white">Code Style Grader</h1>
        <p className="text-sm text-gray-400">AI-powered C++ code analysis</p>
      </header>

      {/* Tab Navigation */}
      <div className="bg-gray-800 border-b border-gray-700 px-6">
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
      </div>

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden">
        {activeTab === 'analysis' ? (
          <>
            {/* Left Sidebar - File Manager */}
            <aside className="w-64 bg-gray-800 border-r border-gray-700 overflow-y-auto">
              <FileUploader
                onFileUpload={handleFileUpload}
                uploadedFiles={uploadedFiles}
                selectedFile={selectedFile}
                onFileSelect={handleFileSelect}
              />
            </aside>

            {/* Center - Code Viewer */}
            <section className="flex-1 flex flex-col overflow-hidden">
              <CodeViewer
                file={selectedFile}
                analysisResult={analysisResult}
              />
            </section>

            {/* Right Sidebar - Violation Details */}
            <aside className="w-96 bg-gray-800 border-l border-gray-700 overflow-y-auto">
              <ViolationPanel analysisResult={analysisResult} />
            </aside>
          </>
        ) : (
          <div className="flex-1 overflow-y-auto">
            <RAGManager />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
