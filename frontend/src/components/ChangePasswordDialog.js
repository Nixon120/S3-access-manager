import React, { useState } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    Button,
    Alert,
} from '@mui/material';
import { authAPI } from '../services/api';

export default function ChangePasswordDialog({ open, onClose, forced = false }) {
    const [currentPassword, setCurrentPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        if (newPassword !== confirmPassword) {
            setError("New passwords don't match");
            return;
        }

        if (newPassword.length < 8) {
            setError('Password must be at least 8 characters long');
            return;
        }

        setLoading(true);
        try {
            await authAPI.changePassword(currentPassword, newPassword);
            setSuccess('Password updated successfully');
            setTimeout(() => {
                // If forced, we might want to reload the page or update user context
                // But for now, just closing is fine as the backend updated the flag
                // and the parent component will re-evaluate user state if it fetches it
                // Actually, we need to ensure the parent knows the user state changed.
                // Since we don't have a way to refresh user here easily without context,
                // we rely on the fact that the next navigation or refresh will show correct state.
                // But ideally, we should call a refreshUser function.
                // For now, let's just close. The Layout effect might re-open it if user state isn't updated.
                // To fix this, we should reload the page to get fresh user data.
                window.location.reload();
            }, 1500);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to update password');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Dialog open={open} onClose={forced ? undefined : onClose} maxWidth="sm" fullWidth>
            <DialogTitle>
                {forced ? 'Change Password Required' : 'Change Password'}
            </DialogTitle>
            <form onSubmit={handleSubmit}>
                <DialogContent>
                    {forced && (
                        <Alert severity="warning" sx={{ mb: 2 }}>
                            You must change your password before continuing.
                        </Alert>
                    )}
                    {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
                    {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

                    <TextField
                        fullWidth
                        label="Current Password"
                        type="password"
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        margin="normal"
                        required
                    />
                    <TextField
                        fullWidth
                        label="New Password"
                        type="password"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        margin="normal"
                        required
                        helperText="Must be at least 8 characters"
                    />
                    <TextField
                        fullWidth
                        label="Confirm New Password"
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        margin="normal"
                        required
                    />
                </DialogContent>
                <DialogActions>
                    {!forced && <Button onClick={onClose}>Cancel</Button>}
                    <Button
                        type="submit"
                        variant="contained"
                        disabled={loading}
                    >
                        {loading ? 'Updating...' : 'Update Password'}
                    </Button>
                </DialogActions>
            </form>
        </Dialog>
    );
}
