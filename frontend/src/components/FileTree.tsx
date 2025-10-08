/**
 * FileTree Component - Display files in a hierarchical tree structure
 */
import React, { useState } from 'react';
import { ChevronRight, ChevronDown, Folder, File, X } from 'lucide-react';
import { FileTreeNode, UploadedFile } from '../types';

interface FileTreeProps {
  tree: FileTreeNode[];
  selectedFile: UploadedFile | null;
  onFileSelect: (node: FileTreeNode) => void;
  onFileDelete: (fileId: string, event: React.MouseEvent) => void;
}

const FileTree: React.FC<FileTreeProps> = ({
  tree,
  selectedFile,
  onFileSelect,
  onFileDelete,
}) => {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());

  const toggleFolder = (path: string) => {
    setExpandedFolders(prev => {
      const newSet = new Set(prev);
      if (newSet.has(path)) {
        newSet.delete(path);
      } else {
        newSet.add(path);
      }
      return newSet;
    });
  };

  const renderNode = (node: FileTreeNode, depth: number = 0): React.ReactNode => {
    const isExpanded = expandedFolders.has(node.path);
    const isSelected = node.type === 'file' && node.file_id === selectedFile?.file_id;
    const paddingLeft = depth * 16 + 8;

    if (node.type === 'folder') {
      return (
        <div key={node.path}>
          {/* Folder Node */}
          <div
            onClick={() => toggleFolder(node.path)}
            className="flex items-center gap-2 p-2 cursor-pointer hover:bg-gray-700 transition-colors"
            style={{ paddingLeft: `${paddingLeft}px` }}
          >
            {isExpanded ? (
              <ChevronDown size={16} className="flex-shrink-0" />
            ) : (
              <ChevronRight size={16} className="flex-shrink-0" />
            )}
            <Folder size={16} className="flex-shrink-0 text-yellow-500" />
            <span className="text-sm truncate">{node.name}</span>
          </div>

          {/* Children (if expanded) */}
          {isExpanded && node.children && (
            <div>
              {node.children.map(child => renderNode(child, depth + 1))}
            </div>
          )}
        </div>
      );
    } else {
      // File Node
      return (
        <div
          key={node.path}
          onClick={() => onFileSelect(node)}
          className={`flex items-center justify-between p-2 cursor-pointer transition-colors ${
            isSelected ? 'bg-blue-600' : 'hover:bg-gray-700'
          }`}
          style={{ paddingLeft: `${paddingLeft}px` }}
        >
          <div className="flex items-center gap-2 flex-1 min-w-0">
            <div style={{ width: '16px' }} /> {/* Spacer for alignment */}
            <File size={16} className="flex-shrink-0 text-blue-400" />
            <span className="text-sm truncate">{node.name}</span>
          </div>
          {node.file_id && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onFileDelete(node.file_id!, e);
              }}
              className="p-1 hover:bg-red-600 rounded transition-colors ml-2"
            >
              <X size={14} />
            </button>
          )}
        </div>
      );
    }
  };

  return (
    <div className="space-y-0.5">
      {tree.length === 0 ? (
        <div className="text-center text-gray-500 mt-8 px-4">
          <p>No files uploaded</p>
          <p className="text-sm mt-1">Upload .cpp, .hpp, or .h files</p>
        </div>
      ) : (
        tree.map(node => renderNode(node, 0))
      )}
    </div>
  );
};

export default FileTree;
