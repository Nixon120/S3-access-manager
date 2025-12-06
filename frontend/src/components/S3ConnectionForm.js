import React, { useState, useEffect } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Grid,
    Alert,
    CircularProgress,
    Typography,
    Box
} from '@mui/material';
import { s3ConnectionsAPI } from '../services/api';

const AUTH_METHODS = [
    { value: 'access_key', label: 'Access Keys' },
    { value: 'iam_role', label: 'IAM Role' },
    // { value: 'iam_roles_anywhere', label: 'IAM Roles Anywhere' } // Future support
];

const REGIONS = [
    'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
    'eu-west-1', 'eu-central-1', 'ap-southeast-1', 'ap-northeast-1'
];

const initialFormState = {
    name: '',
    account_id: '',
    region: 'us-east-1',
    auth_method: 'access_key',
    access_key_id: '',
    secret_access_key: '',
    role_arn: '',
    external_id: '',
    is_active: true
};

function S3ConnectionForm({ open, onClose, connection = null, onSuccess }) {
    const [formData, setFormData] = useState(initialFormState);
    const [loading, setLoading] = useState(false);
    const [testing, setTesting] = useState(false);
    const [error, setError] = useState(null);
    const [testResult, setTestResult] = useState(null);

    useEffect(() => {
        if (connection) {
            setFormData({
                ...initialFormState,
                ...connection,
                access_key_id: '', // Don't populate sensitive fields
                secret_access_key: ''
            });
        } else {
            setFormData(initialFormState);
        }
        setError(null);
        setTestResult(null);
    }, [connection, open]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleTest = async () => {
        setTesting(true);
        setError(null);
        setTestResult(null);
        try {
            const response = await s3ConnectionsAPI.test(formData);
            setTestResult(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Connection test failed');
        } finally {
            setTesting(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            if (connection) {
                await s3ConnectionsAPI.update(connection.id, formData);
            } else {
                await s3ConnectionsAPI.create(formData);
            }
            onSuccess();
            onClose();
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to save connection');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle>
                {connection ? 'Edit S3 Connection' : 'Add S3 Connection'}
            </DialogTitle>
            <form onSubmit={handleSubmit}>
                <DialogContent>
                    {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

                    <Grid container spacing={2}>
                        <Grid item xs={12} md={6}>
                            <TextField
                                fullWidth
                                label="Connection Name"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                required
                                helperText="e.g., Production Account, Partner A"
                            />
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <TextField
                                fullWidth
                                label="AWS Account ID"
                                name="account_id"
                                value={formData.account_id}
                                onChange={handleChange}
                                required
                                inputProps={{ pattern: "\\d{12}", maxLength: 12 }}
                                helperText="12-digit AWS Account ID"
                            />
                        </Grid>

                        <Grid item xs={12} md={6}>
                            <FormControl fullWidth>
                                <InputLabel>Region</InputLabel>
                                <Select
                                    name="region"
                                    value={formData.region}
                                    label="Region"
                                    onChange={handleChange}
                                >
                                    {REGIONS.map(region => (
                                        <MenuItem key={region} value={region}>{region}</MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                        </Grid>

                        <Grid item xs={12} md={6}>
                            <FormControl fullWidth>
                                <InputLabel>Authentication Method</InputLabel>
                                <Select
                                    name="auth_method"
                                    value={formData.auth_method}
                                    label="Authentication Method"
                                    onChange={handleChange}
                                >
                                    {AUTH_METHODS.map(method => (
                                        <MenuItem key={method.value} value={method.value}>
                                            {method.label}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                        </Grid>

                        {formData.auth_method === 'access_key' && (
                            <>
                                <Grid item xs={12} md={6}>
                                    <TextField
                                        fullWidth
                                        label="Access Key ID"
                                        name="access_key_id"
                                        value={formData.access_key_id}
                                        onChange={handleChange}
                                        required={!connection}
                                        helperText={connection ? "Leave blank to keep unchanged" : ""}
                                    />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <TextField
                                        fullWidth
                                        label="Secret Access Key"
                                        name="secret_access_key"
                                        value={formData.secret_access_key}
                                        onChange={handleChange}
                                        type="password"
                                        required={!connection}
                                        helperText={connection ? "Leave blank to keep unchanged" : ""}
                                    />
                                </Grid>
                            </>
                        )}

                        {formData.auth_method === 'iam_role' && (
                            <>
                                <Grid item xs={12}>
                                    <TextField
                                        fullWidth
                                        label="Role ARN"
                                        name="role_arn"
                                        value={formData.role_arn}
                                        onChange={handleChange}
                                        required
                                        placeholder="arn:aws:iam::123456789012:role/RoleName"
                                    />
                                </Grid>
                                <Grid item xs={12}>
                                    <TextField
                                        fullWidth
                                        label="External ID (Optional)"
                                        name="external_id"
                                        value={formData.external_id}
                                        onChange={handleChange}
                                    />
                                </Grid>
                            </>
                        )}
                    </Grid>

                    {testResult && (
                        <Alert severity="success" sx={{ mt: 2 }}>
                            {testResult.message}
                        </Alert>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button
                        onClick={handleTest}
                        disabled={loading || testing}
                        color="info"
                    >
                        {testing ? <CircularProgress size={24} /> : 'Test Connection'}
                    </Button>
                    <Box sx={{ flex: '1 1 auto' }} />
                    <Button onClick={onClose} disabled={loading}>
                        Cancel
                    </Button>
                    <Button
                        type="submit"
                        variant="contained"
                        disabled={loading || testing}
                    >
                        {loading ? <CircularProgress size={24} /> : (connection ? 'Update' : 'Create')}
                    </Button>
                </DialogActions>
            </form>
        </Dialog>
    );
}

export default S3ConnectionForm;
