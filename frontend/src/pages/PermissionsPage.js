import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Button,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  FormControlLabel,
  Checkbox,
  IconButton,
  Chip,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { DataGrid } from '@mui/x-data-grid';
import { permissionsAPI, usersAPI, s3ConnectionsAPI } from '../services/api';

export default function PermissionsPage() {
  const [permissions, setPermissions] = useState([]);
  const [users, setUsers] = useState([]);
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingPermission, setEditingPermission] = useState(null);
  const [formData, setFormData] = useState({
    user_id: '',
    s3_connection_id: '',
    bucket_name: '',
    prefix: '',
    can_read: true,
    can_write: false,
    can_delete: false,
    can_list: true,
    description: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [permsResponse, usersResponse, connsResponse] = await Promise.all([
        permissionsAPI.list(),
        usersAPI.list(),
        s3ConnectionsAPI.list(),
      ]);
      setPermissions(permsResponse.data);
      setUsers(usersResponse.data);
      setConnections(connsResponse.data);
    } catch (err) {
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleAddPermission = () => {
    setEditingPermission(null);
    setFormData({
      user_id: '',
      s3_connection_id: '',
      bucket_name: '',
      prefix: '',
      can_read: true,
      can_write: false,
      can_delete: false,
      can_list: true,
      description: '',
    });
    setDialogOpen(true);
  };

  const handleEditPermission = (permission) => {
    setEditingPermission(permission);
    setFormData({
      user_id: permission.user_id,
      s3_connection_id: permission.s3_connection_id || '',
      bucket_name: permission.bucket_name,
      prefix: permission.prefix,
      can_read: permission.can_read,
      can_write: permission.can_write,
      can_delete: permission.can_delete,
      can_list: permission.can_list,
      description: permission.description || '',
    });
    setDialogOpen(true);
  };

  const handleDeletePermission = async (permissionId) => {
    if (!window.confirm('Are you sure you want to delete this permission?')) {
      return;
    }

    try {
      await permissionsAPI.delete(permissionId);
      setSuccess('Permission deleted successfully');
      loadData();
    } catch (err) {
      setError('Failed to delete permission');
    }
  };

  const handleSubmit = async () => {
    setError('');
    try {
      if (editingPermission) {
        await permissionsAPI.update(editingPermission.id, formData);
        setSuccess('Permission updated successfully');
      } else {
        await permissionsAPI.create(formData);
        setSuccess('Permission created successfully');
      }
      setDialogOpen(false);
      loadData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save permission');
    }
  };

  const getUserEmail = (userId) => {
    const user = users.find(u => u.id === userId);
    return user?.email || 'Unknown';
  };

  const getPermissionChips = (row) => {
    const chips = [];
    if (row.can_read) chips.push('Read');
    if (row.can_write) chips.push('Write');
    if (row.can_delete) chips.push('Delete');
    if (row.can_list) chips.push('List');
    return chips.join(', ');
  };

  const columns = [
    { field: 'id', headerName: 'ID', width: 70 },
    {
      field: 'user_id',
      headerName: 'User',
      width: 200,
      valueGetter: (params) => getUserEmail(params.row.user_id),
    },
    {
      field: 's3_connection_id',
      headerName: 'Connection',
      width: 150,
      valueGetter: (params) => {
        const conn = connections.find(c => c.id === params.row.s3_connection_id);
        return conn ? conn.name : 'Default';
      },
    },
    { field: 'bucket_name', headerName: 'Bucket', width: 200 },
    { field: 'prefix', headerName: 'Prefix', width: 150 },
    {
      field: 'permissions',
      headerName: 'Permissions',
      width: 200,
      renderCell: (params) => (
        <Typography variant="body2">
          {getPermissionChips(params.row)}
        </Typography>
      ),
    },
    { field: 'description', headerName: 'Description', width: 200 },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 150,
      renderCell: (params) => (
        <Box>
          <IconButton
            size="small"
            onClick={() => handleEditPermission(params.row)}
          >
            <EditIcon />
          </IconButton>
          <IconButton
            size="small"
            onClick={() => handleDeletePermission(params.row.id)}
          >
            <DeleteIcon />
          </IconButton>
        </Box>
      ),
    },
  ];

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Permissions</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddPermission}
        >
          Add Permission
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      <Paper sx={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={permissions}
          columns={columns}
          pageSize={10}
          rowsPerPageOptions={[10, 25, 50]}
          loading={loading}
          disableSelectionOnClick
        />
      </Paper>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingPermission ? 'Edit Permission' : 'Add Permission'}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            select
            label="User"
            value={formData.user_id}
            onChange={(e) => setFormData({ ...formData, user_id: e.target.value })}
            margin="normal"
            required
            disabled={!!editingPermission}
          >
            {users.map((user) => (
              <MenuItem key={user.id} value={user.id}>
                {user.email} - {user.full_name}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            fullWidth
            select
            label="S3 Connection"
            value={formData.s3_connection_id}
            onChange={(e) => setFormData({ ...formData, s3_connection_id: e.target.value })}
            margin="normal"
            helperText="Select connection or leave empty for default"
          >
            <MenuItem value="">
              <em>Default (Environment Variables)</em>
            </MenuItem>
            {connections.map((conn) => (
              <MenuItem key={conn.id} value={conn.id}>
                {conn.name} ({conn.account_id})
              </MenuItem>
            ))}
          </TextField>

          <TextField
            fullWidth
            label="Bucket Name"
            value={formData.bucket_name}
            onChange={(e) => setFormData({ ...formData, bucket_name: e.target.value })}
            margin="normal"
            required
            placeholder="my-bucket-name"
          />

          <TextField
            fullWidth
            label="Prefix (optional)"
            value={formData.prefix}
            onChange={(e) => setFormData({ ...formData, prefix: e.target.value })}
            margin="normal"
            placeholder="folder/subfolder/"
            helperText="Leave empty for root access"
          />

          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Permissions
            </Typography>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.can_read}
                  onChange={(e) => setFormData({ ...formData, can_read: e.target.checked })}
                />
              }
              label="Read (Download files)"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.can_write}
                  onChange={(e) => setFormData({ ...formData, can_write: e.target.checked })}
                />
              }
              label="Write (Upload files)"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.can_delete}
                  onChange={(e) => setFormData({ ...formData, can_delete: e.target.checked })}
                />
              }
              label="Delete"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.can_list}
                  onChange={(e) => setFormData({ ...formData, can_list: e.target.checked })}
                />
              }
              label="List (Browse files)"
            />
          </Box>

          <TextField
            fullWidth
            label="Description (optional)"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            margin="normal"
            multiline
            rows={2}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingPermission ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
