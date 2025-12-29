import { useState } from 'react'
import './App.css'
import { api } from './services/api'
import { Upload, X, FileText, Loader2, CheckCircle, AlertCircle, BarChart3, Sparkles, Download, Eye, TrendingUp, AlertTriangle } from 'lucide-react'
import ChartDisplay from './components/ChartDisplay'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

function App() {
  const [backendStatus, setBackendStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [userPrompt, setUserPrompt] = useState<string>('');
  const [processing, setProcessing] = useState(false);
  const [processingStage, setProcessingStage] = useState<string>('');
  const [processingResults, setProcessingResults] = useState<any>(null);

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
    setProcessingResults(null);
    setUserPrompt('');
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
      const result = await api.uploadFile(selectedFile, userPrompt);
      setUploadResult(result);
      setProcessingResults(null);
    } catch (err: any) {
      console.error('Upload error:', err);
      alert('Upload failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  // Process uploaded file with animation
  const handleProcess = async () => {
    if (!uploadResult?.job_id) return;

    try {
      setProcessing(true);

      setProcessingStage('Parsing file...');
      await new Promise(resolve => setTimeout(resolve, 800));

      setProcessingStage('Cleaning data...');
      await new Promise(resolve => setTimeout(resolve, 800));

      setProcessingStage('Analyzing statistics...');
      await new Promise(resolve => setTimeout(resolve, 800));

      setProcessingStage('Detecting patterns...');
      await new Promise(resolve => setTimeout(resolve, 800));

      setProcessingStage('Generating visualizations...');
      await new Promise(resolve => setTimeout(resolve, 800));

      setProcessingStage('AI analyzing patterns...');

      const result = await api.processFile(uploadResult.job_id);
      setProcessingResults(result.results);
      setProcessingStage('');
    } catch (err: any) {
      console.error('Processing error:', err);
      alert('Processing failed: ' + (err.response?.data?.detail || err.message));
      setProcessingStage('');
    } finally {
      setProcessing(false);
    }
  };

  // Export functions
  const handleExportCSV = async () => {
    if (!uploadResult?.job_id) return;

    try {
      const blob = await api.exportCSV(uploadResult.job_id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `cleaned_data_${uploadResult.job_id}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      console.error('Export CSV error:', err);
      alert('Export failed');
    }
  };

  const handleExportJSON = async () => {
    if (!uploadResult?.job_id) return;

    try {
      const blob = await api.exportJSON(uploadResult.job_id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `results_${uploadResult.job_id}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      console.error('Export JSON error:', err);
      alert('Export failed');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-800 to-gray-900 p-4">
      <div className="max-w-6xl mx-auto py-8">
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

              {!uploadResult && (
                <>
                  <div className="bg-slate-700/30 border border-slate-600 rounded-xl p-4">
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      💬 Processing Instructions (Optional)
                    </label>
                    <textarea
                      value={userPrompt}
                      onChange={(e) => setUserPrompt(e.target.value)}
                      placeholder="e.g., Focus on revenue trends, Analyze customer segments, Look for anomalies in sales data..."
                      className="w-full px-4 py-3 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                      rows={3}
                    />
                    <p className="text-xs text-gray-500 mt-2">
                      💡 Provide specific instructions to guide the AI analysis
                    </p>
                  </div>

                  <button
                    onClick={handleUpload}
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-6 py-4 rounded-lg font-semibold text-lg hover:shadow-lg hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                  >
                    {loading ? (
                      <span className="flex items-center justify-center gap-2">
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Uploading...
                      </span>
                    ) : (
                      '📤 Upload & Analyze'
                    )}
                  </button>
                </>
              )}
            </div>
          )}

          {uploadResult && !processingResults && (
            <div className="mt-6 space-y-4">
              <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-4">
                <div className="flex items-center gap-2 text-green-400 font-semibold">
                  <CheckCircle className="w-5 h-5" />
                  Upload Successful!
                </div>
                <p className="text-sm text-green-300/70 mt-1">
                  Job ID: {uploadResult.job_id}
                </p>
                {userPrompt && (
                  <p className="text-sm text-gray-400 mt-2">
                    📝 Instructions: {userPrompt}
                  </p>
                )}
              </div>

              <button
                onClick={handleProcess}
                disabled={processing}
                className="w-full bg-gradient-to-r from-green-500 to-emerald-600 text-white px-6 py-4 rounded-lg font-semibold text-lg hover:shadow-lg hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
              >
                {processing ? (
                  <div className="space-y-2">
                    <div className="flex items-center justify-center gap-2">
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Processing Data...
                    </div>
                    {processingStage && (
                      <div className="text-sm text-green-200">
                        {processingStage}
                      </div>
                    )}
                  </div>
                ) : (
                  '🚀 Process Data'
                )}
              </button>
            </div>
          )}
        </div>

        {/* Processing Results */}
        {processingResults && (
          <div className="space-y-6">
            {/* Success Banner */}
            <div className="bg-green-500/10 border border-green-500/30 rounded-2xl p-6">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-8 h-8 text-green-400" />
                <div>
                  <h3 className="text-green-400 font-bold text-xl">Processing Completed!</h3>
                  <p className="text-green-300/70 text-sm">Your data has been structured and analyzed</p>
                </div>
              </div>
            </div>

            {/* Data Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                <div className="text-gray-400 text-sm mb-2">Total Rows</div>
                <div className="text-3xl font-bold text-white">
                  {processingResults.statistics?.summary?.total_rows || 0}
                </div>
              </div>

              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                <div className="text-gray-400 text-sm mb-2">Total Columns</div>
                <div className="text-3xl font-bold text-white">
                  {processingResults.statistics?.summary?.total_columns || 0}
                </div>
              </div>

              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                <div className="text-gray-400 text-sm mb-2">Rows Cleaned</div>
                <div className="text-3xl font-bold text-white">
                  {processingResults.cleaning_report?.rows_removed || 0}
                </div>
              </div>

              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                <div className="text-gray-400 text-sm mb-2">Outliers Found</div>
                <div className="text-3xl font-bold text-white">
                  {Object.keys(processingResults.advanced_analytics?.outliers || {}).length}
                </div>
              </div>
            </div>

            {/* Data Preview */}
            {processingResults.data_preview && (
              <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
                <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                  <Eye className="w-5 h-5 text-indigo-400" />
                  Data Preview (First 10 Rows)
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left">
                    <thead className="text-xs text-gray-400 uppercase bg-slate-700/50">
                      <tr>
                        {processingResults.data_preview.columns.map((col: string, idx: number) => (
                          <th key={idx} className="px-4 py-3 whitespace-nowrap">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {processingResults.data_preview.data.map((row: any, rowIdx: number) => (
                        <tr key={rowIdx} className="border-b border-slate-700 hover:bg-slate-700/30">
                          {processingResults.data_preview.columns.map((col: string, colIdx: number) => (
                            <td key={colIdx} className="px-4 py-3 text-gray-300 whitespace-nowrap">
                              {row[col] || '-'}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Export Buttons */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Download className="w-5 h-5 text-indigo-400" />
                Export Results
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button
                  onClick={handleExportCSV}
                  className="bg-gradient-to-r from-blue-500 to-cyan-600 text-white px-6 py-3 rounded-lg font-semibold hover:shadow-lg hover:scale-105 transition-all flex items-center justify-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  Download Cleaned CSV
                </button>
                <button
                  onClick={handleExportJSON}
                  className="bg-gradient-to-r from-purple-500 to-pink-600 text-white px-6 py-3 rounded-lg font-semibold hover:shadow-lg hover:scale-105 transition-all flex items-center justify-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  Download Full JSON
                </button>
              </div>
            </div>

            {/* Advanced Analytics */}
            {processingResults.advanced_analytics && (
              <div className="space-y-6">

                {/* Anomalies */}
                {processingResults.advanced_analytics.anomalies && (
                  <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
                    <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5 text-yellow-400" />
                      Data Quality Issues
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="bg-slate-700/50 rounded-lg p-4">
                        <div className="text-sm text-gray-400 mb-1">Duplicate Rows</div>
                        <div className="text-2xl font-bold text-white">
                          {processingResults.advanced_analytics.anomalies.duplicate_rows}
                        </div>
                      </div>
                      <div className="bg-slate-700/50 rounded-lg p-4">
                        <div className="text-sm text-gray-400 mb-1">Single-Value Columns</div>
                        <div className="text-2xl font-bold text-white">
                          {processingResults.advanced_analytics.anomalies.columns_with_single_value.length}
                        </div>
                      </div>
                      <div className="bg-slate-700/50 rounded-lg p-4">
                        <div className="text-sm text-gray-400 mb-1">High Null Columns</div>
                        <div className="text-2xl font-bold text-white">
                          {processingResults.advanced_analytics.anomalies.columns_with_high_null_rate.length}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Trends */}
                {processingResults.advanced_analytics.trends && Object.keys(processingResults.advanced_analytics.trends).length > 0 && (
                  <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
                    <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                      <TrendingUp className="w-5 h-5 text-green-400" />
                      Detected Trends
                    </h3>
                    <div className="space-y-3">
                      {Object.entries(processingResults.advanced_analytics.trends).map(([col, trend]: [string, any]) => (
                        <div key={col} className="bg-slate-700/50 rounded-lg p-4">
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="font-semibold text-white">{col}</div>
                              <div className="text-sm text-gray-400">
                                {trend.direction === 'increasing' ? '📈' : '📉'} {trend.direction} by {Math.abs(trend.change_percent)}%
                              </div>
                            </div>
                            <div className={`px-3 py-1 rounded-full text-sm font-semibold ${
                              trend.direction === 'increasing' 
                                ? 'bg-green-500/20 text-green-400' 
                                : 'bg-red-500/20 text-red-400'
                            }`}>
                              {trend.change_percent > 0 ? '+' : ''}{trend.change_percent}%
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Outliers */}
                {processingResults.advanced_analytics.outliers && Object.keys(processingResults.advanced_analytics.outliers).length > 0 && (
                  <details className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
                    <summary className="cursor-pointer text-xl font-semibold text-white">
                      🔍 Outlier Detection Report
                    </summary>
                    <div className="mt-4 space-y-4">
                      {Object.entries(processingResults.advanced_analytics.outliers).map(([col, data]: [string, any]) => (
                        <div key={col} className="bg-slate-700/50 rounded-lg p-4">
                          <div className="font-semibold text-white mb-2">{col}</div>
                          <div className="grid grid-cols-2 gap-3 text-sm">
                            <div>
                              <span className="text-gray-400">Count:</span>
                              <span className="text-white ml-2">{data.count}</span>
                            </div>
                            <div>
                              <span className="text-gray-400">Percentage:</span>
                              <span className="text-white ml-2">{data.percentage}%</span>
                            </div>
                            <div>
                              <span className="text-gray-400">Lower Bound:</span>
                              <span className="text-white ml-2">{data.lower_bound.toFixed(2)}</span>
                            </div>
                            <div>
                              <span className="text-gray-400">Upper Bound:</span>
                              <span className="text-white ml-2">{data.upper_bound.toFixed(2)}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </details>
                )}

                {/* Correlation Matrix */}
                {processingResults.advanced_analytics.correlation_matrix && (
                  <details className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
                    <summary className="cursor-pointer text-xl font-semibold text-white">
                      📊 Correlation Analysis
                    </summary>
                    <div className="mt-4">
                      {processingResults.advanced_analytics.correlation_matrix.pairs.length > 0 ? (
                        <div className="space-y-3">
                          <p className="text-gray-400 text-sm mb-4">Strong correlations found (|r| {'>'} 0.7):</p>
                          {processingResults.advanced_analytics.correlation_matrix.pairs.map((pair: any, idx: number) => (
                            <div key={idx} className="bg-slate-700/50 rounded-lg p-4">
                              <div className="flex items-center justify-between">
                                <div>
                                  <span className="text-white font-semibold">{pair.col1}</span>
                                  <span className="text-gray-400 mx-2">↔</span>
                                  <span className="text-white font-semibold">{pair.col2}</span>
                                </div>
                                <div className={`px-3 py-1 rounded-full text-sm font-semibold ${
                                  pair.correlation > 0 
                                    ? 'bg-green-500/20 text-green-400' 
                                    : 'bg-red-500/20 text-red-400'
                                }`}>
                                  r = {pair.correlation.toFixed(3)}
                                </div>
                              </div>
                              <div className="text-sm text-gray-400 mt-2">{pair.strength}</div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-gray-400">No strong correlations detected</p>
                      )}
                    </div>
                  </details>
                )}
              </div>
            )}

            {/* AI Insights Section */}
            {processingResults.insights && (
              <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-8">
                <div className="flex items-center gap-3 mb-6">
                  <div className="bg-gradient-to-br from-purple-500 to-pink-500 p-3 rounded-xl">
                    <Sparkles className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-white">AI-Powered Insights</h3>
                    <p className="text-sm text-gray-400">Generated by Gemini AI</p>
                  </div>
                </div>

                <div className="space-y-6">
                  {processingResults.insights.split('\n\n').map((section: string, idx: number) => {
                    if (!section.trim()) return null;

                    if (section.startsWith('##')) {
                      const title = section.replace(/^##\s*/, '').replace(/\*\*/g, '');
                      return (
                        <h4 key={idx} className="text-xl font-bold text-purple-400 mt-6 first:mt-0">
                          {title}
                        </h4>
                      );
                    }

                    if (section.match(/^\*\*\d+\./)) {
                      return (
                        <div key={idx} className="bg-slate-700/50 rounded-lg p-4 border-l-4 border-purple-500">
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            className="text-white font-semibold"
                          >
                            {section}
                          </ReactMarkdown>
                        </div>
                      );
                    }

                    return (
                      <div key={idx} className="text-gray-300 leading-relaxed pl-4">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            ul: ({node, ...props}) => <ul className="list-disc list-inside space-y-2 ml-2" {...props} />,
                            ol: ({node, ...props}) => <ol className="list-decimal list-inside space-y-2 ml-2" {...props} />,
                            li: ({node, ...props}) => <li className="text-gray-300" {...props} />,
                            strong: ({node, ...props}) => <strong className="text-white font-semibold" {...props} />,
                            p: ({node, ...props}) => <p className="my-2" {...props} />,
                          }}
                        >
                          {section}
                        </ReactMarkdown>
                      </div>
                    );
                  })}
                </div>

                <div className="mt-6 pt-6 border-t border-slate-700">
                  <p className="text-xs text-gray-500 text-center">
                    💡 These insights are AI-generated. Always validate findings with domain expertise.
                  </p>
                </div>
              </div>
            )}

            {/* Charts Section */}
            {processingResults.charts && processingResults.charts.length > 0 && (
              <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
                <h3 className="text-2xl font-semibold text-white mb-6 flex items-center gap-2">
                  <BarChart3 className="w-6 h-6 text-indigo-400" />
                  Data Visualizations
                </h3>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {processingResults.charts.map((chart: any, index: number) => (
                    <ChartDisplay key={index} chartConfig={chart} />
                  ))}
                </div>
              </div>
            )}

            {/* Cleaning Report */}
            {processingResults.cleaning_report && processingResults.cleaning_report.operations.length > 0 && (
              <details className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
                <summary className="cursor-pointer text-xl font-semibold text-white flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-blue-400" />
                  Data Cleaning Report
                </summary>
                <div className="mt-4 space-y-3">
                  {processingResults.cleaning_report.operations.map((op: any, idx: number) => (
                    <div key={idx} className="bg-slate-700/50 rounded-lg p-4">
                      <div className="font-semibold text-white capitalize mb-1">
                        {op.step.replace(/_/g, ' ')}
                      </div>
                      <div className="text-sm text-gray-400">
                        {op.detail || JSON.stringify(op)}
                      </div>
                    </div>
                  ))}
                </div>
              </details>
            )}

            {/* Statistics */}
            {processingResults.statistics && (
              <details className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
                <summary className="cursor-pointer text-xl font-semibold text-white">
                  📊 Statistical Analysis
                </summary>

                <div className="mt-4">
                  {Object.keys(processingResults.statistics.numeric_stats || {}).length > 0 && (
                    <div className="mb-6">
                      <h4 className="text-lg font-medium text-gray-300 mb-3">Numeric Columns</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {Object.entries(processingResults.statistics.numeric_stats).map(([col, stats]: [string, any]) => (
                          <div key={col} className="bg-slate-700/50 rounded-lg p-4">
                            <div className="font-semibold text-white mb-2">{col}</div>
                            <div className="grid grid-cols-2 gap-2 text-sm">
                              <div>
                                <span className="text-gray-400">Mean:</span>
                                <span className="text-white ml-2">{stats.mean.toFixed(2)}</span>
                              </div>
                              <div>
                                <span className="text-gray-400">Median:</span>
                                <span className="text-white ml-2">{stats.median.toFixed(2)}</span>
                              </div>
                              <div>
                                <span className="text-gray-400">Min:</span>
                                <span className="text-white ml-2">{stats.min.toFixed(2)}</span>
                              </div>
                              <div>
                                <span className="text-gray-400">Max:</span>
                                <span className="text-white ml-2">{stats.max.toFixed(2)}</span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {Object.keys(processingResults.statistics.categorical_stats || {}).length > 0 && (
                    <div>
                      <h4 className="text-lg font-medium text-gray-300 mb-3">Categorical Columns</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {Object.entries(processingResults.statistics.categorical_stats).map(([col, stats]: [string, any]) => (
                          <div key={col} className="bg-slate-700/50 rounded-lg p-4">
                            <div className="font-semibold text-white mb-2">{col}</div>
                            <div className="text-sm text-gray-400 mb-2">
                              Unique values: {stats.unique_values}
                            </div>
                            <div className="text-xs text-gray-500">
                              Top values: {Object.keys(stats.most_common).slice(0, 3).join(', ')}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </details>
            )}

            {/* Raw JSON */}
            <details className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
              <summary className="cursor-pointer text-gray-400 hover:text-white font-semibold">
                📄 View Raw Results (JSON)
              </summary>
              <div className="mt-4 bg-slate-900/80 rounded-lg p-4 overflow-auto max-h-96">
                <pre className="text-xs text-gray-300">
                  {JSON.stringify(processingResults, null, 2)}
                </pre>
              </div>
            </details>
          </div>
        )}

        {/* Backend Test */}
        <details className="bg-slate-800/30 rounded-xl border border-slate-700 p-6 mt-8">
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