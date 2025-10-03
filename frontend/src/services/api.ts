/**
 * API service for communicating with backend
 */
import axios from 'axios';
import { AnalysisResult, UploadedFile, RAGDocument } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// File upload and management
export const uploadFile = async (file: File): Promise<UploadedFile> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/files/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const listFiles = async (): Promise<{ files: UploadedFile[] }> => {
  const response = await api.get('/files/list');
  return response.data;
};

export const getFile = async (fileId: string): Promise<UploadedFile> => {
  const response = await api.get(`/files/${fileId}`);
  return response.data;
};

export const deleteFile = async (fileId: string): Promise<void> => {
  await api.delete(`/files/${fileId}`);
};

// Code analysis
export const analyzeCode = async (
  fileId: string,
  styleGuideId?: string,
  useRag: boolean = true
): Promise<any> => {
  const response = await api.post('/analysis/analyze', {
    file_id: fileId,
    style_guide_id: styleGuideId,
    use_rag: useRag,
  });
  return response.data;
};

export const getAnalysisResults = async (analysisId: string): Promise<AnalysisResult> => {
  const response = await api.get(`/analysis/results/${analysisId}`);
  return response.data;
};

export const getAnalysisStatus = async (analysisId: string): Promise<any> => {
  const response = await api.get(`/analysis/status/${analysisId}`);
  return response.data;
};

// RAG document management
export const uploadRAGDocument = async (
  file: File,
  docType: 'style_guide' | 'reference'
): Promise<RAGDocument> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post(`/rag/upload?doc_type=${docType}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const listRAGDocuments = async (): Promise<{ documents: RAGDocument[] }> => {
  const response = await api.get('/rag/documents');
  return response.data;
};

export const deleteRAGDocument = async (docId: string): Promise<void> => {
  await api.delete(`/rag/documents/${docId}`);
};

// System setup
export const checkSystem = async (): Promise<any> => {
  const response = await api.post('/setup/check');
  return response.data;
};

export const getConfiguration = async (): Promise<any> => {
  const response = await api.get('/setup/config');
  return response.data;
};
