import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import UsersPage from './pages/UsersPage';
import PermissionsPage from './pages/PermissionsPage';
import S3ConnectionsPage from './pages/S3ConnectionsPage';
import AuditPage from './pages/AuditPage';
import { CircularProgress, Box } from '@mui/material';
import SessionTimeout from './components/SessionTimeout';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function PrivateRoute({ children, adminOnly = false }) {
  const { user, loading, isAdmin } = useAuth();

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (adminOnly && !isAdmin) {
    return <Navigate to="/" replace />;
  }

  return (
    <Layout>
      <SessionTimeout />
      {children}
    </Layout>
  );
}

function PublicRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (user) {
    return <Navigate to="/" replace />;
  }

  return children;
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route
              path="/login"
              element={
                <PublicRoute>
                  <LoginPage />
                </PublicRoute>
              }
            />
            <Route
              path="/"
              element={
                <PrivateRoute>
                  <DashboardPage />
                </PrivateRoute>
              }
            />
            <Route
              path="/users"
              element={
                <PrivateRoute adminOnly>
                  <UsersPage />
                </PrivateRoute>
              }
            />
            <Route
              path="/permissions"
              element={
                <PrivateRoute adminOnly>
                  <PermissionsPage />
                </PrivateRoute>
              }
            />
            <Route
              path="/s3-connections"
              element={
                <PrivateRoute adminOnly>
                  <S3ConnectionsPage />
                </PrivateRoute>
              }
            />
            <Route
              path="/audit"
              element={
                <PrivateRoute adminOnly>
                  <AuditPage />
                </PrivateRoute>
              }
            />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
