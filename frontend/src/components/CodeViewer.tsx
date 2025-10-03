/**
 * CodeViewer Component - Display code with syntax highlighting using Monaco Editor
 */
import React, { useEffect, useState } from 'react';
import Editor from '@monaco-editor/react';
import { UploadedFile, AnalysisResult } from '../types';
import * as api from '../services/api';

interface CodeViewerProps {
  file: UploadedFile | null;
  analysisResult: AnalysisResult | null;
}

const CodeViewer: React.FC<CodeViewerProps> = ({ file, analysisResult }) => {
  const [code, setCode] = useState<string>('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadFileContent = async () => {
      if (!file) {
        setCode('');
        return;
      }

      if (file.content) {
        setCode(file.content);
        return;
      }

      // Fetch file content from backend
      setLoading(true);
      try {
        const fileData = await api.getFile(file.file_id);
        setCode(fileData.content || '');
      } catch (error) {
        console.error('Error loading file content:', error);
        setCode('// Error loading file content');
      } finally {
        setLoading(false);
      }
    };

    loadFileContent();
  }, [file]);

  if (!file) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-900 text-gray-500">
        <div className="text-center">
          <p className="text-xl mb-2">No file selected</p>
          <p className="text-sm">Upload and select a C++ file to view</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-900 text-gray-500">
        Loading...
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* File Name Header */}
      <div className="px-4 py-2 bg-gray-800 border-b border-gray-700">
        <h3 className="text-sm font-medium text-gray-300">{file.file_name}</h3>
      </div>

      {/* Monaco Editor */}
      <div className="flex-1">
        <Editor
          language="cpp"
          value={code}
          theme="vs-dark"
          options={{
            readOnly: true,
            minimap: { enabled: true },
            fontSize: 14,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
          }}
        />
      </div>
    </div>
  );
};

export default CodeViewer;
