import { useState } from 'react'
import './App.css'
import { api } from './services/api'
import { Upload, X, FileText } from 'lucide-react'

function App() {
  const [backendStatus, setBackendStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadResult, setUploadResult] = useState<any>(null);

  // Backend connection test
  const testBackend = async () => {
    try {
      const health = await api.healthCheck();
      setBackendStatus(health);
    } catch (err) {
      console.error('Backend error:', err);
    }
  };

  // File drag & drop handlers
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
    setUploadResult(null);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  // Upload file
  const handleUpload = async () => {
    if (!selectedFile) return;

    try {
      setLoading(true);
      const result = await api.uploadFile(selectedFile);
      setUploadResult(result);
    } catch (err: any) {
      console.error('Upload error:', err);
      alert('Upload failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-800 to-gray-900 p-4">
      <div className="max-w-4xl mx-auto py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 bg-clip-text text-transparent">
            UnstructIQ
          </h1>
          <p className="text-gray-400 text-xl">
            AI-powered Data Structuring & Visualization Platform
          </p>
        </div>

        {/* Upload Section */}
        <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl border border-slate-700 p-8 shadow-2xl mb-8">
          <h2 className="text-2xl font-semibold text-white mb-6">Upload Your Data</h2>

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
            <div className="space-y-4">
              <div className="bg-slate-700/50 border border-slate-600 rounded-xl p-6">
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
                    className="p-2 hover:bg-slate-600 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5 text-gray-400" />
                  </button>
                </div>
              </div>

              <button
                onClick={handleUpload}
                disabled={loading}
                className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-6 py-4 rounded-lg font-semibold text-lg hover:shadow-lg hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
              >
                {loading ? 'Uploading...' : 'Upload & Process'}
              </button>
            </div>
          )}

          {/* Upload Result */}
          {uploadResult && (
            <div className="mt-6 bg-green-500/10 border border-green-500/30 rounded-xl p-6">
              <h3 className="text-green-400 font-bold text-lg mb-2">✅ Upload Successful!</h3>
              <div className="bg-slate-900/80 rounded-lg p-4 font-mono text-sm">
                <pre className="text-gray-300">
                  {JSON.stringify(uploadResult, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>

        {/* Backend Test Section (Collapsible) */}
        <details className="bg-slate-800/30 rounded-xl border border-slate-700 p-6">
          <summary className="cursor-pointer text-gray-400 hover:text-white font-semibold">
            🔧 Backend Connection Test
          </summary>
          <div className="mt-4">
            <button
              onClick={testBackend}
              className="bg-slate-700 text-white px-4 py-2 rounded-lg hover:bg-slate-600 transition-colors mb-4"
            >
              Test Connection
            </button>
            {backendStatus && (
              <div className="bg-slate-900/50 rounded-lg p-4 font-mono text-sm">
                <pre className="text-gray-300">
                  {JSON.stringify(backendStatus, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </details>
      </div>
    </div>
  )
}

export default App