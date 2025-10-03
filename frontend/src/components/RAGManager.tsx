/**
 * RAGManager Component - Manage RAG knowledge base documents
 */
import React, { useState, useEffect, useRef } from 'react';
import { Upload, FileText, Trash2 } from 'lucide-react';
import { RAGDocument } from '../types';
import * as api from '../services/api';

const RAGManager: React.FC = () => {
  const [documents, setDocuments] = useState<RAGDocument[]>([]);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploadType, setUploadType] = useState<'style_guide' | 'reference'>('style_guide');

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const response = await api.listRAGDocuments();
      setDocuments(response.documents);
    } catch (error) {
      console.error('Error loading RAG documents:', error);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setLoading(true);
    try {
      for (let i = 0; i < files.length; i++) {
        await api.uploadRAGDocument(files[i], uploadType);
      }
      await loadDocuments();
    } catch (error) {
      console.error('Error uploading RAG document:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (docId: string) => {
    try {
      await api.deleteRAGDocument(docId);
      await loadDocuments();
    } catch (error) {
      console.error('Error deleting RAG document:', error);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-6">RAG Knowledge Base Management</h2>

      <div className="bg-gray-800 rounded-lg p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4">Upload Documents</h3>

        {/* Document Type Selection */}
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Document Type</label>
          <select
            value={uploadType}
            onChange={(e) => setUploadType(e.target.value as 'style_guide' | 'reference')}
            className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
          >
            <option value="style_guide">Style Guide</option>
            <option value="reference">Reference Material</option>
          </select>
        </div>

        {/* Upload Button */}
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded transition-colors"
        >
          <Upload size={18} />
          {loading ? 'Uploading...' : 'Upload Document'}
        </button>

        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".txt,.md"
          onChange={handleFileUpload}
          className="hidden"
        />

        <p className="text-sm text-gray-400 mt-2">
          Supported formats: .txt, .md
        </p>
      </div>

      {/* Document List */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Uploaded Documents</h3>

        {documents.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <FileText size={48} className="mx-auto mb-2 opacity-50" />
            <p>No documents uploaded</p>
            <p className="text-sm mt-1">Upload style guides and reference materials</p>
          </div>
        ) : (
          <div className="space-y-2">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between p-3 bg-gray-700 rounded hover:bg-gray-600 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <FileText size={20} />
                  <div>
                    <div className="font-medium">{doc.filename}</div>
                    <div className="text-xs text-gray-400 capitalize">{doc.type.replace('_', ' ')}</div>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(doc.id)}
                  className="p-2 hover:bg-red-600 rounded transition-colors"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default RAGManager;
