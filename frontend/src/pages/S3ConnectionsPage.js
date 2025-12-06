import React, { useState, useEffect } from 'react';
import {
    Container,
    Typography,
    Button,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    IconButton,
    Chip,
    Box,
    CircularProgress,
    Alert
} from '@mui/material';
import {
    Add as AddIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    CheckCircle as CheckCircleIcon,
    Cancel as CancelIcon
} from '@mui/icons-material';
import { s3ConnectionsAPI } from '../services/api';
import S3ConnectionForm from '../components/S3ConnectionForm';

function S3ConnectionsPage() {
    const [connections, setConnections] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [openForm, setOpenForm] = useState(false);
    const [selectedConnection, setSelectedConnection] = useState(null);

    const fetchConnections = async () => {
        try {
            setLoading(true);
            const response = await s3ConnectionsAPI.list();
            setConnections(response.data);
            setError(null);
        } catch (err) {
            setError('Failed to load S3 connections');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchConnections();
    }, []);

    const handleAdd = () => {
        setSelectedConnection(null);
        setOpenForm(true);
    };

    const handleEdit = (connection) => {
        setSelectedConnection(connection);
        setOpenForm(true);
    };

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this connection?')) {
            try {
                await s3ConnectionsAPI.delete(id);
                fetchConnections();
            } catch (err) {
                setError(err.response?.data?.detail || 'Failed to delete connection');
            }
        }
    };

    const handleFormSuccess = () => {
        fetchConnections();
    };

    if (loading && connections.length === 0) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="h4" component="h1">
                    S3 Connections
                </Typography>
                <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={handleAdd}
                >
                    Add Connection
                </Button>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                </Alert>
            )}

            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Name</TableCell>
                            <TableCell>Account ID</TableCell>
                            <TableCell>Region</TableCell>
                            <TableCell>Auth Method</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell align="right">Actions</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {connections.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={6} align="center">
                                    No connections found. Create one to get started.
                                </TableCell>
                            </TableRow>
                        ) : (
                            connections.map((conn) => (
                                <TableRow key={conn.id}>
                                    <TableCell>{conn.name}</TableCell>
                                    <TableCell>{conn.account_id}</TableCell>
                                    <TableCell>{conn.region}</TableCell>
                                    <TableCell>
                                        <Chip
                                            label={conn.auth_method.replace('_', ' ').toUpperCase()}
                                            size="small"
                                            variant="outlined"
                                        />
                                    </TableCell>
                                    <TableCell>
                                        {conn.is_active ? (
                                            <Chip icon={<CheckCircleIcon />} label="Active" color="success" size="small" />
                                        ) : (
                                            <Chip icon={<CancelIcon />} label="Inactive" color="default" size="small" />
                                        )}
                                    </TableCell>
                                    <TableCell align="right">
                                        <IconButton onClick={() => handleEdit(conn)} color="primary">
                                            <EditIcon />
                                        </IconButton>
                                        <IconButton onClick={() => handleDelete(conn.id)} color="error">
                                            <DeleteIcon />
                                        </IconButton>
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </TableContainer>

            <S3ConnectionForm
                open={openForm}
                onClose={() => setOpenForm(false)}
                connection={selectedConnection}
                onSuccess={handleFormSuccess}
            />
        </Container>
    );
}

export default S3ConnectionsPage;
