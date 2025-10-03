/**
 * ViolationPanel Component - Display violation details and statistics
 */
import React from 'react';
import { AlertCircle, AlertTriangle, Info } from 'lucide-react';
import { AnalysisResult, Violation, ViolationSeverity } from '../types';

interface ViolationPanelProps {
  analysisResult: AnalysisResult | null;
}

const ViolationPanel: React.FC<ViolationPanelProps> = ({ analysisResult }) => {
  const getSeverityIcon = (severity: ViolationSeverity) => {
    switch (severity) {
      case ViolationSeverity.CRITICAL:
        return <AlertCircle size={16} className="text-critical" />;
      case ViolationSeverity.WARNING:
        return <AlertTriangle size={16} className="text-warning" />;
      case ViolationSeverity.MINOR:
        return <Info size={16} className="text-minor" />;
    }
  };

  const getSeverityColor = (severity: ViolationSeverity) => {
    switch (severity) {
      case ViolationSeverity.CRITICAL:
        return 'text-critical border-critical';
      case ViolationSeverity.WARNING:
        return 'text-warning border-warning';
      case ViolationSeverity.MINOR:
        return 'text-minor border-minor';
    }
  };

  if (!analysisResult) {
    return (
      <div className="p-6 text-gray-500">
        <h2 className="text-lg font-semibold mb-4">Violations</h2>
        <p className="text-sm">No analysis results available</p>
        <p className="text-sm mt-2">Upload a file and run analysis to see violations</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header with Statistics */}
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-lg font-semibold mb-3">Analysis Results</h2>

        {/* Summary Stats */}
        <div className="bg-gray-700 rounded p-3 mb-3">
          <div className="text-sm text-gray-400 mb-1">Total Violations</div>
          <div className="text-2xl font-bold">{analysisResult.total_violations}</div>
        </div>

        {/* Severity Breakdown */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <AlertCircle size={14} className="text-critical" />
              <span>Critical</span>
            </div>
            <span className="font-semibold">
              {analysisResult.violations_by_severity[ViolationSeverity.CRITICAL] || 0}
            </span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <AlertTriangle size={14} className="text-warning" />
              <span>Warning</span>
            </div>
            <span className="font-semibold">
              {analysisResult.violations_by_severity[ViolationSeverity.WARNING] || 0}
            </span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <Info size={14} className="text-minor" />
              <span>Minor</span>
            </div>
            <span className="font-semibold">
              {analysisResult.violations_by_severity[ViolationSeverity.MINOR] || 0}
            </span>
          </div>
        </div>
      </div>

      {/* Violation List */}
      <div className="flex-1 overflow-y-auto p-4">
        {analysisResult.violations.length === 0 ? (
          <div className="text-center text-green-500 mt-8">
            <p className="text-lg font-semibold">No violations found!</p>
            <p className="text-sm mt-1">Code follows the style guide</p>
          </div>
        ) : (
          <div className="space-y-3">
            {analysisResult.violations.map((violation, index) => (
              <div
                key={index}
                className={`border-l-4 ${getSeverityColor(
                  violation.severity
                )} bg-gray-700 p-3 rounded-r`}
              >
                <div className="flex items-start gap-2 mb-2">
                  {getSeverityIcon(violation.severity)}
                  <div className="flex-1">
                    <div className="font-medium text-sm">{violation.type}</div>
                    <div className="text-xs text-gray-400">
                      Line {violation.line_number}
                      {violation.column && `, Column ${violation.column}`}
                    </div>
                  </div>
                </div>
                <p className="text-sm text-gray-300 mb-2">{violation.description}</p>
                {violation.style_guide_reference && (
                  <div className="text-xs text-gray-500 italic">
                    Ref: {violation.style_guide_reference}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ViolationPanel;
