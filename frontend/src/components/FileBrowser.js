import React, { useState, useEffect } from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Typography,
  CircularProgress,
  Alert,
  Tooltip,
  Breadcrumbs,
  Link,
  Chip,
} from '@mui/material';
import {
  Download as DownloadIcon,
  Delete as DeleteIcon,
  InsertDriveFile as FileIcon,
  Folder as FolderIcon,
  FolderOpen as FolderOpenIcon,
  Refresh as RefreshIcon,
  Home as HomeIcon,
} from '@mui/icons-material';
import { s3API } from '../services/api';

export default function FileBrowser({ bucketName, prefix, canWrite, canDelete, onPathChange }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentPath, setCurrentPath] = useState('');

  useEffect(() => {
    setCurrentPath('');
    loadFiles('');
  }, [bucketName, prefix]);

  const loadFiles = async (subPath = '') => {
    setLoading(true);
    setError('');
    try {
      const fullPrefix = prefix + subPath;
      const response = await s3API.listObjects(bucketName, fullPrefix);

      // Process objects to separate folders and files
      const processedItems = processS3Objects(response.data.objects, fullPrefix);
      setItems(processedItems);

      // Notify parent of path change
      if (onPathChange) {
        onPathChange(subPath);
      }
    } catch (err) {
      setError('Failed to load files');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const processS3Objects = (objects, currentPrefix) => {
    const folders = new Set();
    const files = [];

    objects.forEach(obj => {
      const relativePath = obj.key.substring(currentPrefix.length);

      if (relativePath) {
        const parts = relativePath.split('/');

        if (parts.length > 1 && parts[0]) {
          // It's in a subfolder
          folders.add(parts[0]);
        } else if (parts[0]) {
          // It's a file in current directory
          files.push({
            ...obj,
            name: parts[0],
            isFolder: false
          });
        }
      }
    });

    // Convert folders to array and add metadata
    const folderItems = Array.from(folders).map(folderName => ({
      name: folderName,
      isFolder: true,
      key: currentPrefix + folderName + '/'
    }));

    // Sort: folders first, then files (both alphabetically)
    folderItems.sort((a, b) => a.name.localeCompare(b.name));
    files.sort((a, b) => a.name.localeCompare(b.name));

    return [...folderItems, ...files];
  };

  const handleFolderClick = (folderName) => {
    const newPath = currentPath ? `${currentPath}${folderName}/` : `${folderName}/`;
    setCurrentPath(newPath);
    loadFiles(newPath);
  };

  const handleBreadcrumbClick = (index) => {
    if (index === -1) {
      // Home clicked
      setCurrentPath('');
      loadFiles('');
    } else {
      const pathParts = currentPath.split('/').filter(p => p);
      const newPath = pathParts.slice(0, index + 1).join('/') + '/';
      setCurrentPath(newPath);
      loadFiles(newPath);
    }
  };

  const handleDownload = async (file) => {
    try {
      const response = await s3API.getPresignedUrl(
        bucketName,
        file.key,
        'download'
      );

      window.open(response.data.url, '_blank');
    } catch (err) {
      setError('Failed to download file');
      console.error(err);
    }
  };

  const handleDelete = async (file) => {
    if (!window.confirm(`Are you sure you want to delete ${file.name}?`)) {
      return;
    }

    try {
      await s3API.deleteObject(bucketName, file.key);
      loadFiles(currentPath);
    } catch (err) {
      setError('Failed to delete file');
      console.error(err);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getBreadcrumbs = () => {
    if (!currentPath) return [];
    return currentPath.split('/').filter(p => p);
  };

  const folderCount = items.filter(item => item.isFolder).length;
  const fileCount = items.filter(item => !item.isFolder).length;

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Breadcrumb Navigation */}
      <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Breadcrumbs>
          <Link
            component="button"
            variant="body2"
            onClick={() => handleBreadcrumbClick(-1)}
            sx={{
              display: 'flex',
              alignItems: 'center',
              textDecoration: 'none',
              cursor: 'pointer',
              '&:hover': { textDecoration: 'underline' }
            }}
          >
            <HomeIcon sx={{ mr: 0.5, fontSize: 20 }} />
            {prefix || 'Root'}
          </Link>
          {getBreadcrumbs().map((part, index) => (
            <Link
              key={index}
              component="button"
              variant="body2"
              onClick={() => handleBreadcrumbClick(index)}
              sx={{
                cursor: 'pointer',
                textDecoration: 'none',
                '&:hover': { textDecoration: 'underline' }
              }}
            >
              {part}
            </Link>
          ))}
        </Breadcrumbs>
      </Box>

      {/* Current Location & Stats */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2, alignItems: 'center' }}>
        <Box>
          <Typography variant="caption" color="text.secondary" display="block">
            Current location: {bucketName}/{prefix}{currentPath}
          </Typography>
          <Box sx={{ mt: 0.5 }}>
            <Chip
              icon={<FolderIcon />}
              label={`${folderCount} folder(s)`}
              size="small"
              sx={{ mr: 1 }}
            />
            <Chip
              icon={<FileIcon />}
              label={`${fileCount} file(s)`}
              size="small"
            />
          </Box>
        </Box>
        <IconButton size="small" onClick={() => loadFiles(currentPath)}>
          <RefreshIcon />
        </IconButton>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {items.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <FolderOpenIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
          <Typography color="text.secondary">
            No files or folders in this location
          </Typography>
        </Box>
      ) : (
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell align="right">Size</TableCell>
                <TableCell align="right">Last Modified</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {items.map((item, index) => (
                <TableRow
                  key={index}
                  hover
                  sx={{
                    cursor: item.isFolder ? 'pointer' : 'default',
                    '&:hover': item.isFolder ? { bgcolor: 'action.hover' } : {}
                  }}
                  onClick={() => item.isFolder && handleFolderClick(item.name)}
                >
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      {item.isFolder ? (
                        <FolderIcon sx={{ mr: 1, fontSize: 20, color: 'primary.main' }} />
                      ) : (
                        <FileIcon sx={{ mr: 1, fontSize: 20, color: 'text.secondary' }} />
                      )}
                      <Typography variant="body2">
                        {item.name}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    {item.isFolder ? '—' : formatFileSize(item.size)}
                  </TableCell>
                  <TableCell align="right">
                    {item.isFolder ? '—' : formatDate(item.last_modified)}
                  </TableCell>
                  <TableCell align="right">
                    {item.isFolder ? (
                      <Typography variant="caption" color="text.secondary">
                        Folder
                      </Typography>
                    ) : (
                      <>
                        <Tooltip title="Download">
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDownload(item);
                            }}
                          >
                            <DownloadIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        {canDelete && (
                          <Tooltip title="Delete">
                            <IconButton
                              size="small"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDelete(item);
                              }}
                              color="error"
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}
                      </>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}
