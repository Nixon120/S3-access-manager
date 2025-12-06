import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Button,
  Chip,
  Alert,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Folder as FolderIcon,
  CloudUpload as UploadIcon,
  Download as DownloadIcon,
  People as PeopleIcon,
  Security as SecurityIcon,
  FolderOpen as FolderOpenIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { permissionsAPI, s3API, auditAPI } from '../services/api';
import FileUploadDialog from '../components/FileUploadDialog';
import FileBrowser from '../components/FileBrowser';

export default function DashboardPage() {
  const { user, isAdmin } = useAuth();
  const [permissions, setPermissions] = useState([]);
  const [selectedBucket, setSelectedBucket] = useState(null);
  const [currentPath, setCurrentPath] = useState('');
  const [stats, setStats] = useState(null);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState(0); // 0 = Browse, 1 = Upload

  useEffect(() => {
    loadData();
  }, [isAdmin]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (isAdmin) {
        const statsResponse = await auditAPI.getStats();
        console.log('Stats Response:', statsResponse.data);
        console.log('Recent Activity:', statsResponse.data?.recent_activity);
        setStats(statsResponse.data);
      } else {
        const permsResponse = await permissionsAPI.getMyPermissions();
        setPermissions(permsResponse.data);
      }
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Error loading dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBucketSelect = (bucket) => {
    setSelectedBucket(bucket);
    setCurrentPath(''); // Reset path when changing buckets
    setActiveTab(0); // Reset to Browse tab
  };

  const handlePathChange = (newPath) => {
    setCurrentPath(newPath);
  };

  const handleUploadComplete = () => {
    setUploadDialogOpen(false);
    setActiveTab(0); // Switch back to Browse tab
    // Trigger refresh by updating a key or calling a refresh function
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Typography>Loading...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Welcome, {user?.full_name}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {isAdmin ? 'Administrator Dashboard' : 'Your S3 Resources'}
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {isAdmin ? (
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <PeopleIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6">Users</Typography>
                </Box>
                <Typography variant="h3">{stats?.total_users || 0}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {stats?.active_users || 0} active
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <FolderIcon sx={{ mr: 1, color: 'success.main' }} />
                  <Typography variant="h6">Buckets</Typography>
                </Box>
                <Typography variant="h3">{stats?.total_buckets || 0}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Accessible buckets
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <SecurityIcon sx={{ mr: 1, color: 'warning.main' }} />
                  <Typography variant="h6">Permissions</Typography>
                </Box>
                <Typography variant="h3">{stats?.total_permissions || 0}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Total assigned
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <UploadIcon sx={{ mr: 1, color: 'info.main' }} />
                  <Typography variant="h6">Activity</Typography>
                </Box>
                <Typography variant="h3">
                  {stats?.recent_activity?.length || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Recent actions
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              {stats?.recent_activity && stats.recent_activity.length > 0 ? (
                <List>
                  {stats.recent_activity.slice(0, 5).map((log) => (
                    <ListItem key={log.id}>
                      <ListItemText
                        primary={`${log.action} - ${log.bucket_name}/${log.object_key}`}
                        secondary={`User ID: ${log.user_id} • ${new Date(log.created_at).toLocaleString()}`}
                      />
                      <Chip
                        label={log.status}
                        color={log.status === 'success' ? 'success' : 'error'}
                        size="small"
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
                  No recent activity found.
                </Typography>
              )}
            </Paper>
          </Grid>
        </Grid>
      ) : (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Your Buckets
              </Typography>
              <List>
                {permissions.map((perm, index) => (
                  <ListItem
                    key={index}
                    button
                    selected={selectedBucket?.bucket_name === perm.bucket_name}
                    onClick={() => handleBucketSelect(perm)}
                  >
                    <ListItemIcon>
                      <FolderIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={perm.bucket_name}
                      secondary={perm.prefix || 'Root'}
                    />
                  </ListItem>
                ))}
                {permissions.length === 0 && (
                  <ListItem>
                    <ListItemText
                      primary="No access granted"
                      secondary="Contact your administrator"
                    />
                  </ListItem>
                )}
              </List>
            </Paper>
          </Grid>

          <Grid item xs={12} md={8}>
            {selectedBucket ? (
              <Paper sx={{ p: 0 }}>
                {/* Tab Headers */}
                <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                  <Tabs value={activeTab} onChange={handleTabChange}>
                    <Tab
                      icon={<FolderOpenIcon />}
                      label="Browse Files"
                      iconPosition="start"
                    />
                    <Tab
                      icon={<UploadIcon />}
                      label="Upload Files"
                      iconPosition="start"
                      disabled={!selectedBucket.can_write}
                    />
                  </Tabs>
                </Box>

                {/* Tab Content */}
                <Box sx={{ p: 2 }}>
                  {activeTab === 0 && (
                    // Browse Tab
                    <FileBrowser
                      bucketName={selectedBucket.bucket_name}
                      prefix={selectedBucket.prefix}
                      canWrite={selectedBucket.can_write}
                      canDelete={selectedBucket.can_delete}
                      onPathChange={handlePathChange}
                    />
                  )}

                  {activeTab === 1 && (
                    // Upload Tab
                    <Box>
                      <Paper
                        variant="outlined"
                        sx={{
                          p: 3,
                          mb: 3,
                          bgcolor: 'primary.50',
                          borderColor: 'primary.main',
                          borderWidth: 2
                        }}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                          <FolderOpenIcon color="primary" fontSize="large" />
                          <Box>
                            <Typography variant="h6">
                              Upload Files
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Upload to: <strong>{selectedBucket.bucket_name}/{selectedBucket.prefix}{currentPath}</strong>
                            </Typography>
                          </Box>
                        </Box>
                      </Paper>

                      <Box sx={{ textAlign: 'center', py: 4 }}>
                        <Button
                          variant="contained"
                          size="large"
                          startIcon={<UploadIcon />}
                          onClick={() => setUploadDialogOpen(true)}
                          sx={{
                            py: 2,
                            px: 6,
                            fontSize: '1.1rem'
                          }}
                        >
                          Select Files to Upload
                        </Button>
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                          ℹ️ Current location: Files will be uploaded to the path shown above.
                        </Typography>
                        <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
                          Navigate folders in the Browse tab if you need to upload to a different location.
                        </Typography>
                      </Box>
                    </Box>
                  )}
                </Box>
              </Paper>
            ) : (
              <Paper sx={{ p: 4, textAlign: 'center' }}>
                <FolderIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary">
                  Select a bucket to browse files
                </Typography>
              </Paper>
            )}
          </Grid>
        </Grid>
      )}

      {uploadDialogOpen && selectedBucket && (
        <FileUploadDialog
          open={uploadDialogOpen}
          onClose={() => setUploadDialogOpen(false)}
          bucketName={selectedBucket.bucket_name}
          prefix={selectedBucket.prefix}
          currentPath={currentPath}
          onUploadComplete={handleUploadComplete}
        />
      )}
    </Container>
  );
}
