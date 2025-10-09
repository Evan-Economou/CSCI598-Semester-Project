/**
 * CodeViewer Component - Display code with syntax highlighting using Monaco Editor
 */
import React, { useEffect, useState, useRef } from 'react';
import Editor from '@monaco-editor/react';
import { UploadedFile, AnalysisResult, ViolationSeverity } from '../types';
import * as api from '../services/api';
import type { editor } from 'monaco-editor';

interface CodeViewerProps {
  file: UploadedFile | null;
  analysisResult: AnalysisResult | null;
}

const CodeViewer: React.FC<CodeViewerProps> = ({ file, analysisResult }) => {
  const [code, setCode] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);

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

  // Apply violation highlighting when analysis results change
  useEffect(() => {
    if (!editorRef.current || !analysisResult || !analysisResult.violations) {
      return;
    }

    const editor = editorRef.current;
    const decorations: editor.IModelDeltaDecoration[] = [];

    // Group violations by line number for better handling
    const violationsByLine = new Map<number, typeof analysisResult.violations>();
    analysisResult.violations.forEach(violation => {
      const line = violation.line_number;
      if (!violationsByLine.has(line)) {
        violationsByLine.set(line, []);
      }
      violationsByLine.get(line)!.push(violation);
    });

    // Create decorations for each line with violations
    violationsByLine.forEach((violations, lineNumber) => {
      // Find the highest severity for this line
      const severities = violations.map(v => v.severity);
      let severity: ViolationSeverity;

      if (severities.includes(ViolationSeverity.CRITICAL)) {
        severity = ViolationSeverity.CRITICAL;
      } else if (severities.includes(ViolationSeverity.WARNING)) {
        severity = ViolationSeverity.WARNING;
      } else {
        severity = ViolationSeverity.MINOR;
      }

      // Get color based on severity
      const getBackgroundColor = (sev: ViolationSeverity): string => {
        switch (sev) {
          case ViolationSeverity.CRITICAL:
            return 'rgba(239, 68, 68, 0.15)'; // red with transparency
          case ViolationSeverity.WARNING:
            return 'rgba(245, 158, 11, 0.15)'; // amber with transparency
          case ViolationSeverity.MINOR:
            return 'rgba(59, 130, 246, 0.15)'; // blue with transparency
          default:
            return 'rgba(156, 163, 175, 0.15)'; // gray fallback
        }
      };

      const getBorderColor = (sev: ViolationSeverity): string => {
        switch (sev) {
          case ViolationSeverity.CRITICAL:
            return 'rgba(239, 68, 68, 0.6)'; // red
          case ViolationSeverity.WARNING:
            return 'rgba(245, 158, 11, 0.6)'; // amber
          case ViolationSeverity.MINOR:
            return 'rgba(59, 130, 246, 0.6)'; // blue
          default:
            return 'rgba(156, 163, 175, 0.6)'; // gray fallback
        }
      };

      // Add line highlight decoration
      decorations.push({
        range: {
          startLineNumber: lineNumber,
          startColumn: 1,
          endLineNumber: lineNumber,
          endColumn: Number.MAX_VALUE,
        },
        options: {
          isWholeLine: true,
          className: 'violation-line',
          glyphMarginClassName: 'violation-glyph',
          glyphMarginHoverMessage: {
            value: violations.map(v =>
              `**${v.severity}**: ${v.description}`
            ).join('\n\n'),
          },
          inlineClassName: 'violation-inline',
          overviewRuler: {
            color: getBorderColor(severity),
            position: 4, // OverviewRulerLane.Full
          },
          minimap: {
            color: getBorderColor(severity),
            position: 2, // MinimapPosition.Inline
          },
        },
      });

      // Add background decoration
      decorations.push({
        range: {
          startLineNumber: lineNumber,
          startColumn: 1,
          endLineNumber: lineNumber,
          endColumn: Number.MAX_VALUE,
        },
        options: {
          isWholeLine: true,
          className: '',
          inlineClassName: '',
          linesDecorationsClassName: `violation-decoration-${severity.toLowerCase()}`,
        },
      });
    });

    // Apply all decorations
    const decorationIds = editor.deltaDecorations([], decorations);

    // Store decoration IDs for cleanup
    return () => {
      if (editor && decorationIds) {
        editor.deltaDecorations(decorationIds, []);
      }
    };
  }, [analysisResult]);

  const handleEditorDidMount = (editor: editor.IStandaloneCodeEditor) => {
    editorRef.current = editor;

    // Add custom CSS for violation highlighting
    const style = document.createElement('style');
    style.innerHTML = `
      .violation-line {
        background: rgba(239, 68, 68, 0.1);
      }
      .violation-decoration-critical {
        background: rgba(239, 68, 68, 0.15) !important;
        border-left: 3px solid rgba(239, 68, 68, 0.8) !important;
      }
      .violation-decoration-warning {
        background: rgba(245, 158, 11, 0.15) !important;
        border-left: 3px solid rgba(245, 158, 11, 0.8) !important;
      }
      .violation-decoration-minor {
        background: rgba(59, 130, 246, 0.15) !important;
        border-left: 3px solid rgba(59, 130, 246, 0.8) !important;
      }
    `;

    // Only add style once
    if (!document.getElementById('violation-styles')) {
      style.id = 'violation-styles';
      document.head.appendChild(style);
    }
  };

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
            glyphMargin: true, // Enable glyph margin for hover messages
            overviewRulerLanes: 3, // Show overview ruler for violations
          }}
          onMount={handleEditorDidMount}
        />
      </div>
    </div>
  );
};

export default CodeViewer;
