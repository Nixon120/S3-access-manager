import React, { useState, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Paper,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  InsertDriveFile as FileIcon,
  Close as CloseIcon,
  FolderOpen as FolderOpenIcon,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { s3API } from '../services/api';
import axios from 'axios';

export default function FileUploadDialog({ open, onClose, bucketName, prefix, currentPath = '', onUploadComplete }) {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState({});
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fullPath = prefix + currentPath;

  const onDrop = useCallback((acceptedFiles) => {
    setFiles((prev) => [...prev, ...acceptedFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: true,
  });

  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const uploadFiles = async () => {
    if (files.length === 0) return;

    setUploading(true);
    setError('');
    setSuccess('');

    const uploadResults = [];
    let successCount = 0;
    let failCount = 0;

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const objectKey = fullPath ? `${fullPath}${file.name}` : file.name;

        try {
          // Get presigned URL
          const urlResponse = await s3API.getPresignedUrl(
            bucketName,
            objectKey,
            'upload'
          );

          const { url, fields } = urlResponse.data;

          // Create form data for upload
          const formData = new FormData();

          // Add all fields from presigned POST
          if (fields) {
            Object.keys(fields).forEach(key => {
              formData.append(key, fields[key]);
            });
          }

          // Add file (must be last)
          formData.append('file', file);

          // Upload to S3
          const uploadResponse = await axios.post(url, formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
            onUploadProgress: (progressEvent) => {
              const percentCompleted = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
              setProgress((prev) => ({
                ...prev,
                [file.name]: percentCompleted,
              }));
            },
          });

          // Check if upload was successful
          if (uploadResponse.status === 200 || uploadResponse.status === 204) {
            successCount++;
            uploadResults.push({ file: file.name, status: 'success' });

            // Notify backend of successful upload
            try {
              await s3API.notifyUploadComplete(bucketName, objectKey, 'success');
            } catch (notifyErr) {
              console.error('Failed to notify backend:', notifyErr);
            }
          } else {
            failCount++;
            uploadResults.push({ file: file.name, status: 'failed', error: 'Unexpected response' });
          }

        } catch (fileErr) {
          failCount++;
          const errorMsg = fileErr.response?.data?.message ||
            fileErr.response?.data?.detail ||
            fileErr.message ||
            'Upload failed';

          uploadResults.push({ file: file.name, status: 'failed', error: errorMsg });

          // Notify backend of failed upload
          try {
            await s3API.notifyUploadComplete(bucketName, objectKey, 'failure', errorMsg);
          } catch (notifyErr) {
            console.error('Failed to notify backend:', notifyErr);
          }

          console.error(`Failed to upload ${file.name}:`, fileErr);
        }
      }

      // Show results
      if (failCount === 0) {
        setSuccess(`All ${successCount} file(s) uploaded successfully!`);
        setFiles([]);
        setProgress({});

        setTimeout(() => {
          onUploadComplete();
          onClose();
        }, 1500);
      } else if (successCount === 0) {
        setError(`Failed to upload all ${failCount} file(s). Please check your AWS credentials and bucket permissions.`);
      } else {
        setError(`Uploaded ${successCount} file(s), but ${failCount} failed. Check console for details.`);
      }

    } catch (err) {
      console.error('Upload error:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to upload files');
    } finally {
      setUploading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Upload Files
      </DialogTitle>
      <DialogContent>
        {/* Upload Location Display */}
        <Paper
          variant="outlined"
          sx={{
            p: 2,
            mb: 3,
            bgcolor: 'primary.50',
            borderColor: 'primary.main',
            borderWidth: 2
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FolderOpenIcon color="primary" />
            <Box>
              <Typography variant="caption" color="text.secondary" display="block">
                Upload destination:
              </Typography>
              <Typography variant="body2" fontWeight="medium">
                {bucketName}/{fullPath || '(root)'}
              </Typography>
            </Box>
          </Box>
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        <Box
          {...getRootProps()}
          sx={{
            border: '2px dashed',
            borderColor: isDragActive ? 'primary.main' : 'grey.300',
            borderRadius: 2,
            p: 4,
            textAlign: 'center',
            cursor: 'pointer',
            bgcolor: isDragActive ? 'action.hover' : 'background.paper',
            mb: 2,
            transition: 'all 0.2s',
          }}
        >
          <input {...getInputProps()} />
          <UploadIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            {isDragActive ? 'Drop files here' : 'Drag and drop files here'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            or click to browse files
          </Typography>
        </Box>

        {files.length > 0 && (
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Files to upload ({files.length})
            </Typography>
            <List>
              {files.map((file, index) => (
                <ListItem
                  key={index}
                  secondaryAction={
                    !uploading && (
                      <IconButton edge="end" onClick={() => removeFile(index)}>
                        <CloseIcon />
                      </IconButton>
                    )
                  }
                >
                  <ListItemIcon>
                    <FileIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={file.name}
                    secondary={formatFileSize(file.size)}
                  />
                  {uploading && progress[file.name] !== undefined && (
                    <Box sx={{ width: '100%', ml: 2 }}>
                      <LinearProgress
                        variant="determinate"
                        value={progress[file.name]}
                      />
                      <Typography variant="caption">
                        {progress[file.name]}%
                      </Typography>
                    </Box>
                  )}
                </ListItem>
              ))}
            </List>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={uploading}>
          Cancel
        </Button>
        <Button
          onClick={uploadFiles}
          variant="contained"
          disabled={files.length === 0 || uploading}
          startIcon={<UploadIcon />}
        >
          {uploading ? 'Uploading...' : 'Upload'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
