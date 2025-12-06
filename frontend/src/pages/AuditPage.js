import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Paper,
  TextField,
  MenuItem,
  Grid,
  Chip,
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { auditAPI } from '../services/api';

export default function AuditPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    action: '',
    status: '',
  });

  useEffect(() => {
    loadLogs();
  }, [filters]);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const activeFilters = {};
      if (filters.action) activeFilters.action = filters.action;
      if (filters.status) activeFilters.status = filters.status;

      console.log('Fetching logs with filters:', activeFilters);
      const response = await auditAPI.getLogs(activeFilters, 0, 100);
      console.log('Logs response:', response.data);
      console.log('Number of logs:', response.data?.length);
      setLogs(response.data);
    } catch (err) {
      console.error('Failed to load logs:', err);
      console.error('Error details:', err.response?.data);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'user_id', headerName: 'User ID', width: 90 },
    {
      field: 'action',
      headerName: 'Action',
      width: 150,
      renderCell: (params) => (
        <Chip label={params.value} size="small" />
      ),
    },
    { field: 'bucket_name', headerName: 'Bucket', width: 200 },
    { field: 'object_key', headerName: 'Object Key', width: 250 },
    {
      field: 'status',
      headerName: 'Status',
      width: 100,
      renderCell: (params) => (
        <Chip
          label={params.value}
          color={params.value === 'success' ? 'success' : 'error'}
          size="small"
        />
      ),
    },
    { field: 'ip_address', headerName: 'IP Address', width: 130 },
    {
      field: 'created_at',
      headerName: 'Timestamp',
      width: 180,
      valueFormatter: (params) => new Date(params.value).toLocaleString(),
    },
    {
      field: 'error_message',
      headerName: 'Error',
      width: 200,
      renderCell: (params) => params.value || '-',
    },
  ];

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Audit Logs
      </Typography>

      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              select
              label="Action"
              value={filters.action}
              onChange={(e) => setFilters({ ...filters, action: e.target.value })}
            >
              <MenuItem value="">All Actions</MenuItem>
              <MenuItem value="upload">Upload</MenuItem>
              <MenuItem value="download">Download</MenuItem>
              <MenuItem value="delete">Delete</MenuItem>
              <MenuItem value="list">List</MenuItem>
            </TextField>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              select
              label="Status"
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            >
              <MenuItem value="">All Statuses</MenuItem>
              <MenuItem value="success">Success</MenuItem>
              <MenuItem value="failure">Failure</MenuItem>
            </TextField>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={logs}
          columns={columns}
          pageSize={25}
          rowsPerPageOptions={[25, 50, 100]}
          loading={loading}
          disableSelectionOnClick
        />
      </Paper>
    </Container>
  );
}
