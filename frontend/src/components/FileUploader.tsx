/**
 * FileUploader Component - Handle file and folder uploads with hierarchical display
 */
import React, { useRef } from 'react';
import { Upload } from 'lucide-react';
import { UploadedFile, FileTreeNode } from '../types';
import * as api from '../services/api';
import FileTree from './FileTree';

interface FileUploaderProps {
  onFileUpload: (files: UploadedFile[]) => void;
  fileTree: FileTreeNode[];
  selectedFile: UploadedFile | null;
  onFileSelect: (node: FileTreeNode) => void;
  onFileDelete: (fileId: string) => void;
}

const FileUploader: React.FC<FileUploaderProps> = ({
  onFileUpload,
  fileTree,
  selectedFile,
  onFileSelect,
  onFileDelete,
}) => {
  const folderInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;

    const uploadedFilesList: UploadedFile[] = [];

    for (let i = 0; i < files.length; i++) {
      try {
        const file = files[i];
        // Get relative path from webkitRelativePath if available (folder upload)
        const relativePath = (file as any).webkitRelativePath || file.name;
        const uploadedFile = await api.uploadFile(file, relativePath);
        uploadedFilesList.push(uploadedFile);
      } catch (error) {
        console.error(`Error uploading ${files[i].name}:`, error);
      }
    }

    onFileUpload(uploadedFilesList);

    // Reset input
    event.target.value = '';
  };

  const handleDelete = async (fileId: string, event: React.MouseEvent) => {
    event.stopPropagation();
    try {
      await api.deleteFile(fileId);
      onFileDelete(fileId);
    } catch (error) {
      console.error('Error deleting file:', error);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-lg font-semibold mb-3">Files</h2>

        {/* Upload Button */}
        <button
          onClick={() => folderInputRef.current?.click()}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
        >
          <Upload size={18} />
          Upload Files/Folder
        </button>

        {/* Single input that supports both files and folders */}
        <input
          ref={folderInputRef}
          type="file"
          {...({webkitdirectory: "", directory: "", mozdirectory: ""} as any)}
          multiple
          onChange={handleFileChange}
          className="hidden"
        />
      </div>

      {/* File Tree */}
      <div className="flex-1 overflow-y-auto">
        <FileTree
          tree={fileTree}
          selectedFile={selectedFile}
          onFileSelect={onFileSelect}
          onFileDelete={handleDelete}
        />
      </div>
    </div>
  );
};

export default FileUploader;
