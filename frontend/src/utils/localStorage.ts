/**
 * Utility functions for persisting data to sessionStorage
 * SessionStorage persists across page refreshes but is cleared when the browser tab/window is closed
 */

import { UploadedFile, AnalysisResult } from '../types';

const KEYS = {
  UPLOADED_FILES: 'code-grader-uploaded-files',
  ANALYSIS_RESULTS: 'code-grader-analysis-results',
  SELECTED_FILE_ID: 'code-grader-selected-file-id',
};

/**
 * Save uploaded files to sessionStorage
 */
export const saveUploadedFiles = (files: UploadedFile[]): void => {
  try {
    sessionStorage.setItem(KEYS.UPLOADED_FILES, JSON.stringify(files));
  } catch (error) {
    console.error('Error saving uploaded files:', error);
  }
};

/**
 * Load uploaded files from sessionStorage
 */
export const loadUploadedFiles = (): UploadedFile[] => {
  try {
    const data = sessionStorage.getItem(KEYS.UPLOADED_FILES);
    if (!data) return [];
    return JSON.parse(data);
  } catch (error) {
    console.error('Error loading uploaded files:', error);
    return [];
  }
};

/**
 * Save analysis results mapped by file ID
 */
export const saveAnalysisResults = (results: Record<string, AnalysisResult>): void => {
  try {
    sessionStorage.setItem(KEYS.ANALYSIS_RESULTS, JSON.stringify(results));
  } catch (error) {
    console.error('Error saving analysis results:', error);
  }
};

/**
 * Load all analysis results
 */
export const loadAnalysisResults = (): Record<string, AnalysisResult> => {
  try {
    const data = sessionStorage.getItem(KEYS.ANALYSIS_RESULTS);
    if (!data) return {};
    return JSON.parse(data);
  } catch (error) {
    console.error('Error loading analysis results:', error);
    return {};
  }
};

/**
 * Save analysis result for a specific file
 */
export const saveAnalysisResult = (fileId: string, result: AnalysisResult): void => {
  try {
    const allResults = loadAnalysisResults();
    allResults[fileId] = result;
    saveAnalysisResults(allResults);
  } catch (error) {
    console.error('Error saving analysis result:', error);
  }
};

/**
 * Get analysis result for a specific file
 */
export const getAnalysisResult = (fileId: string): AnalysisResult | null => {
  try {
    const allResults = loadAnalysisResults();
    return allResults[fileId] || null;
  } catch (error) {
    console.error('Error getting analysis result:', error);
    return null;
  }
};

/**
 * Delete analysis result for a specific file
 */
export const deleteAnalysisResult = (fileId: string): void => {
  try {
    const allResults = loadAnalysisResults();
    delete allResults[fileId];
    saveAnalysisResults(allResults);
  } catch (error) {
    console.error('Error deleting analysis result:', error);
  }
};

/**
 * Save selected file ID
 */
export const saveSelectedFileId = (fileId: string | null): void => {
  try {
    if (fileId) {
      sessionStorage.setItem(KEYS.SELECTED_FILE_ID, fileId);
    } else {
      sessionStorage.removeItem(KEYS.SELECTED_FILE_ID);
    }
  } catch (error) {
    console.error('Error saving selected file ID:', error);
  }
};

/**
 * Load selected file ID
 */
export const loadSelectedFileId = (): string | null => {
  try {
    return sessionStorage.getItem(KEYS.SELECTED_FILE_ID);
  } catch (error) {
    console.error('Error loading selected file ID:', error);
    return null;
  }
};

/**
 * Clear all persisted data
 */
export const clearAllPersistedData = (): void => {
  try {
    sessionStorage.removeItem(KEYS.UPLOADED_FILES);
    sessionStorage.removeItem(KEYS.ANALYSIS_RESULTS);
    sessionStorage.removeItem(KEYS.SELECTED_FILE_ID);
  } catch (error) {
    console.error('Error clearing persisted data:', error);
  }
};
