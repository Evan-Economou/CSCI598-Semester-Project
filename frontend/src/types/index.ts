/**
 * Type definitions for Code Style Grader frontend
 */

export enum ViolationSeverity {
  CRITICAL = 'CRITICAL',
  WARNING = 'WARNING',
  MINOR = 'MINOR',
}

export interface Violation {
  type: string;
  severity: ViolationSeverity;
  line_number: number;
  column?: number;
  description: string;
  style_guide_reference?: string;
  code_snippet?: string;
}

export interface AnalysisResult {
  file_name: string;
  file_path: string;
  timestamp: string;
  violations: Violation[];
  total_violations: number;
  violations_by_severity: Record<string, number>;
  violations_by_type: Record<string, number>;
  status: string;
  error_message?: string;
}

export interface UploadedFile {
  file_id: string;
  file_name: string;
  file_path?: string;  // Full path with directory structure
  file_size: number;
  content?: string;
  status: string;
}

// Tree node for hierarchical file display
export interface FileTreeNode {
  name: string;
  path: string;
  type: 'file' | 'folder';
  file_id?: string;  // Only for files
  file_size?: number;  // Only for files
  children?: FileTreeNode[];  // Only for folders
  expanded?: boolean;  // UI state for folders
}

export interface RAGDocument {
  id: string;
  filename: string;
  type: 'style_guide' | 'reference';
  status: string;
}
