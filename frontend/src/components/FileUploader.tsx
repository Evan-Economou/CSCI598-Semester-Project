/**
 * FileUploader Component - Handle file uploads and display file list
 */
import React, { useRef } from 'react';
import { Upload, File, X } from 'lucide-react';
import { UploadedFile } from '../types';
import * as api from '../services/api';

interface FileUploaderProps {
  onFileUpload: (files: UploadedFile[]) => void;
  uploadedFiles: UploadedFile[];
  selectedFile: UploadedFile | null;
  onFileSelect: (file: UploadedFile) => void;
  onFileDelete: (fileId: string) => void;
}

const FileUploader: React.FC<FileUploaderProps> = ({
  onFileUpload,
  uploadedFiles,
  selectedFile,
  onFileSelect,
  onFileDelete,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;

    const uploadedFilesList: UploadedFile[] = [];

    for (let i = 0; i < files.length; i++) {
      try {
        const uploadedFile = await api.uploadFile(files[i]);
        uploadedFilesList.push(uploadedFile);
      } catch (error) {
        console.error(`Error uploading ${files[i].name}:`, error);
      }
    }

    onFileUpload(uploadedFilesList);
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
          onClick={() => fileInputRef.current?.click()}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
        >
          <Upload size={18} />
          Upload C++ Files
        </button>

        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".cpp,.hpp,.h"
          onChange={handleFileChange}
          className="hidden"
        />
      </div>

      {/* File List */}
      <div className="flex-1 overflow-y-auto p-2">
        {uploadedFiles.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <p>No files uploaded</p>
            <p className="text-sm mt-1">Upload .cpp, .hpp, or .h files</p>
          </div>
        ) : (
          <div className="space-y-1">
            {uploadedFiles.map((file) => (
              <div
                key={file.file_id}
                onClick={() => onFileSelect(file)}
                className={`flex items-center justify-between p-3 rounded cursor-pointer transition-colors ${
                  selectedFile?.file_id === file.file_id
                    ? 'bg-blue-600'
                    : 'bg-gray-700 hover:bg-gray-600'
                }`}
              >
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <File size={16} className="flex-shrink-0" />
                  <span className="text-sm truncate">{file.file_name}</span>
                </div>
                <button
                  onClick={(e) => handleDelete(file.file_id, e)}
                  className="p-1 hover:bg-red-600 rounded transition-colors"
                >
                  <X size={14} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default FileUploader;
