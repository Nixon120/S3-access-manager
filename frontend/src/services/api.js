import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || '/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (email, password) =>
    api.post('/auth/login', { email, password }),

  getMe: () =>
    api.get('/auth/me'),

  changePassword: (currentPassword, newPassword) =>
    api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    }),
};

// Users API
export const usersAPI = {
  list: (skip = 0, limit = 100) =>
    api.get('/users', { params: { skip, limit } }),

  get: (userId) =>
    api.get(`/users/${userId}`),

  create: (userData) =>
    api.post('/users', userData),

  update: (userId, userData) =>
    api.put(`/users/${userId}`, userData),

  delete: (userId) =>
    api.delete(`/users/${userId}`),
};

// Permissions API
export const permissionsAPI = {
  list: (userId = null) =>
    api.get('/permissions', { params: { user_id: userId } }),

  getMyPermissions: () =>
    api.get('/permissions/my-permissions'),

  create: (permissionData) =>
    api.post('/permissions', permissionData),

  update: (permissionId, permissionData) =>
    api.put(`/permissions/${permissionId}`, permissionData),

  delete: (permissionId) =>
    api.delete(`/permissions/${permissionId}`),
};

// S3 API
export const s3API = {
  getPresignedUrl: (bucketName, objectKey, operation) =>
    api.post('/s3/presigned-url', {
      bucket_name: bucketName,
      object_key: objectKey,
      operation: operation,
    }),

  notifyUploadComplete: (bucketName, objectKey, status, errorMessage = null) =>
    api.post('/s3/upload-complete', {
      bucket_name: bucketName,
      object_key: objectKey,
      status: status,
      error_message: errorMessage,
    }),

  listObjects: (bucketName, prefix = '') =>
    api.get(`/s3/list/${bucketName}`, { params: { prefix } }),

  listBuckets: () =>
    api.get('/s3/buckets'),

  deleteObject: (bucketName, objectKey) =>
    api.delete(`/s3/object/${bucketName}/${objectKey}`),
};

// Audit API
export const auditAPI = {
  getLogs: (filters = {}, skip = 0, limit = 100) =>
    api.get('/audit/logs', { params: { ...filters, skip, limit } }),

  getMyActivity: (limit = 50) =>
    api.get('/audit/my-activity', { params: { limit } }),

  getStats: () =>
    api.get('/audit/stats'),

  getUserStats: (userId, days = 30) =>
    api.get(`/audit/user-stats/${userId}`, { params: { days } }),
};

// S3 Connections API
export const s3ConnectionsAPI = {
  list: () =>
    api.get('/s3-connections'),

  get: (connectionId) =>
    api.get(`/s3-connections/${connectionId}`),

  create: (connectionData) =>
    api.post('/s3-connections', connectionData),

  update: (connectionId, connectionData) =>
    api.put(`/s3-connections/${connectionId}`, connectionData),

  delete: (connectionId) =>
    api.delete(`/s3-connections/${connectionId}`),

  test: (connectionData) =>
    api.post('/s3-connections/test', connectionData),
};

export default api;
