import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const api = {
  // Health check
  healthCheck: async () => {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  },

  // Upload file
  uploadFile: async (file, prompt = '') => {
    const formData = new FormData();
    formData.append('file', file);
    if (prompt) {
      formData.append('prompt', prompt);
    }

    const response = await axios.post(`${API_BASE_URL}/api/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Start processing
  processFile: async (jobId) => {
    const response = await axios.post(`${API_BASE_URL}/api/process/${jobId}`);
    return response.data;
  },

  // Get status
  getStatus: async (jobId) => {
    const response = await axios.get(`${API_BASE_URL}/api/status/${jobId}`);
    return response.data;
  },

  // Get results
  getResults: async (jobId) => {
    const response = await axios.get(`${API_BASE_URL}/api/results/${jobId}`);
    return response.data;
  },

  // Export cleaned CSV
  exportCSV: async (jobId) => {
    const response = await axios.get(`${API_BASE_URL}/api/export/csv/${jobId}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Export results JSON
  exportJSON: async (jobId) => {
    const response = await axios.get(`${API_BASE_URL}/api/export/json/${jobId}`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

export default axios.create({
  baseURL: API_BASE_URL,
});