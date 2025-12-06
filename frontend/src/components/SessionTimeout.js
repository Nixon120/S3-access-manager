import React, { useState, useEffect } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogContentText,
    DialogActions,
    Button,
    LinearProgress,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function SessionTimeout() {
    const { logout } = useAuth();
    const navigate = useNavigate();
    const [open, setOpen] = useState(false);
    const [timeLeft, setTimeLeft] = useState(0);

    // Helper to parse JWT
    const parseJwt = (token) => {
        try {
            return JSON.parse(atob(token.split('.')[1]));
        } catch (e) {
            return null;
        }
    };

    useEffect(() => {
        const checkToken = () => {
            const token = localStorage.getItem('token');
            if (!token) return;

            const decoded = parseJwt(token);
            if (!decoded || !decoded.exp) return;

            const currentTime = Date.now() / 1000;
            const timeRemaining = decoded.exp - currentTime;

            // If expired
            if (timeRemaining <= 0) {
                handleLogout();
                return;
            }

            // If less than 2 minutes (120 seconds) remaining
            if (timeRemaining < 120) {
                setTimeLeft(Math.floor(timeRemaining));
                setOpen(true);
            } else {
                setOpen(false);
            }
        };

        // Check every 10 seconds
        const interval = setInterval(checkToken, 10000);

        // Initial check
        checkToken();

        return () => clearInterval(interval);
    }, []);

    // Update countdown timer when dialog is open
    useEffect(() => {
        let timer;
        if (open && timeLeft > 0) {
            timer = setInterval(() => {
                setTimeLeft((prev) => {
                    if (prev <= 1) {
                        handleLogout();
                        return 0;
                    }
                    return prev - 1;
                });
            }, 1000);
        }
        return () => clearInterval(timer);
    }, [open, timeLeft]);

    const handleLogout = () => {
        setOpen(false);
        logout();
        navigate('/login');
    };

    if (!open) return null;

    return (
        <Dialog open={open} onClose={() => { }}>
            <DialogTitle>Session Expiring</DialogTitle>
            <DialogContent>
                <DialogContentText>
                    Your session will expire in {timeLeft} seconds.
                    Please save your work. You will be automatically logged out.
                </DialogContentText>
                <LinearProgress
                    variant="determinate"
                    value={(timeLeft / 120) * 100}
                    sx={{ mt: 2 }}
                />
            </DialogContent>
            <DialogActions>
                <Button onClick={handleLogout} color="primary">
                    Logout Now
                </Button>
            </DialogActions>
        </Dialog>
    );
}
