import { useState } from 'react';
import { Upload, X, FileText } from 'lucide-react';

interface FileUploaderProps {
  onUploadSuccess: (data: any) => void;
  onUploadError: (error: string) => void;
}

export default function FileUploader({ onUploadSuccess, onUploadError }: FileUploaderProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      setSelectedFile(files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  return (
    <div className="w-full">
      {!selectedFile ? (
        <div
          className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
            isDragging
              ? 'border-indigo-500 bg-indigo-500/10'
              : 'border-slate-600 hover:border-indigo-500 hover:bg-slate-800/50'
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => document.getElementById('file-input')?.click()}
        >
          <Upload className="w-16 h-16 mx-auto mb-4 text-slate-400" />
          <h3 className="text-xl font-semibold text-white mb-2">
            Drag & Drop your file here
          </h3>
          <p className="text-gray-400 mb-4">or click to browse</p>
          <p className="text-sm text-gray-500">
            Supported formats: CSV, JSON, Excel, TXT, PDF
          </p>
          <p className="text-xs text-gray-600 mt-2">Max file size: 50MB</p>

          <input
            id="file-input"
            type="file"
            className="hidden"
            accept=".csv,.json,.xlsx,.xls,.txt,.pdf"
            onChange={handleFileSelect}
          />
        </div>
      ) : (
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="bg-indigo-500/10 p-3 rounded-lg">
                <FileText className="w-6 h-6 text-indigo-400" />
              </div>
              <div>
                <h4 className="font-semibold text-white">{selectedFile.name}</h4>
                <p className="text-sm text-gray-400">{formatFileSize(selectedFile.size)}</p>
              </div>
            </div>
            <button
              onClick={removeFile}
              className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-400" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}