import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { styled } from '@mui/material/styles';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import AuthCallback from './pages/AuthCallback';
import Unauthorized from './pages/Unauthorized';
import Stats from './pages/Stats';
import Servers from './pages/Servers';
import ApiExplorer from './pages/ApiExplorer';
import ProtectedRoute from './components/ProtectedRoute';
import Sidebar from './components/Sidebar';
import { Box, CircularProgress, Button } from '@mui/material';
import { isAuthenticated, hasAccess, hasPublicAccess } from './services/auth';

// Custom theme with dragon-inspired colors
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#FF4D4D', // Dragon red
      light: '#FF7373',
      dark: '#CC3D3D',
    },
    secondary: {
      main: '#4DCFFF', // Dragon blue
      light: '#73D8FF',
      dark: '#3DA6CC',
    },
    background: {
      default: '#1A1A2E', // Dark navy
      paper: '#22223A',
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#B3B3CC',
    },
  },
  typography: {
    fontFamily: "'Poppins', sans-serif",
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          backgroundImage: 'linear-gradient(135deg, rgba(255,77,77,0.1) 0%, rgba(77,207,255,0.1) 100%)',
        },
      },
    },
  },
});

const MainContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  minHeight: '100vh',
  background: `linear-gradient(135deg, ${theme.palette.background.default} 0%, #2A2A4A 100%)`,
  backgroundAttachment: 'fixed',
  position: 'relative',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'url("/dragon-scales.svg")',
    opacity: 0.05,
    pointerEvents: 'none',
  },
}));

const ContentContainer = styled(Box)(({ theme }) => ({
  flexGrow: 1,
  padding: theme.spacing(3),
  marginLeft: 240, // Width of sidebar
  [theme.breakpoints.down('md')]: {
    marginLeft: 0,
    padding: theme.spacing(2),
  },
}));

// Komponen Debug untuk troubleshooting
const DebugPage = () => {
  const [backendInfo, setBackendInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
        
        // Fetch system info
        const systemResponse = await fetch(`${apiUrl}/system/info`);
        const systemData = await systemResponse.json();
        
        // Fetch auth debug info
        const authResponse = await fetch(`${apiUrl}/auth/debug`);
        const authData = await authResponse.json();
        
        setBackendInfo({
          system: systemData,
          auth: authData
        });
      } catch (err) {
        console.error('Debug data fetch error:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);
  
  return (
    <Box sx={{ p: 3 }}>
      <h1>Debug Page</h1>
      
      <h2>Local Storage Data</h2>
      <pre style={{ background: '#222', padding: 16, borderRadius: 8, overflow: 'auto' }}>
        {JSON.stringify({ 
          localStorage: Object.entries(localStorage).reduce((acc, [key, value]) => {
            acc[key] = value;
            return acc;
          }, {}),
          sessionStorage: Object.entries(sessionStorage).reduce((acc, [key, value]) => {
            acc[key] = value;
            return acc;
          }, {})
        }, null, 2)}
      </pre>
      
      <h2>Auth Status</h2>
      <pre style={{ background: '#222', padding: 16, borderRadius: 8, overflow: 'auto' }}>
        {JSON.stringify({ 
          isAuthenticated: isAuthenticated(),
          hasAccess: hasAccess(),
          hasPublicAccess: hasPublicAccess(),
        }, null, 2)}
      </pre>
      
      <h2>Backend Status</h2>
      {loading ? (
        <CircularProgress />
      ) : error ? (
        <div style={{ color: 'red' }}>Error: {error}</div>
      ) : (
        <pre style={{ background: '#222', padding: 16, borderRadius: 8, overflow: 'auto' }}>
          {JSON.stringify(backendInfo, null, 2)}
        </pre>
      )}
      
      <h2>Actions</h2>
      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', my: 2 }}>
        <Button 
          variant="contained" 
          color="error" 
          onClick={() => {
            localStorage.clear();
            sessionStorage.clear();
            window.location.reload();
          }}
        >
          Clear Storage & Reload
        </Button>
        <Button 
          variant="contained" 
          onClick={() => {
            window.location.href = '/';
          }}
        >
          Go to Login
        </Button>
        <Button 
          variant="contained" 
          color="secondary"
          onClick={() => {
            window.location.href = '/dashboard';
          }}
        >
          Go to Dashboard
        </Button>
      </Box>
    </Box>
  );
};

function App() {
  const [checking, setChecking] = useState(true);
  
  useEffect(() => {
    // Check authentication status when app loads
    const checkAuth = async () => {
      await new Promise(resolve => setTimeout(resolve, 500)); // Simulated delay for UX
      setChecking(false);
    };
    
    checkAuth();
  }, []);
  
  if (checking) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box 
          sx={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            height: '100vh',
            background: theme.palette.background.default
          }}
        >
          <CircularProgress color="primary" />
        </Box>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={
            (isAuthenticated() || hasPublicAccess()) ? 
            <Navigate to="/dashboard" /> : 
            <Login />
          } />
          <Route path="/auth/callback" element={<AuthCallback />} />
          <Route path="/unauthorized" element={<Unauthorized />} />
          
          {/* Public Dashboard Route */}
          <Route path="/dashboard" element={<ProtectedRoute />}>
            <Route path="" element={
              <MainContainer>
                <Sidebar />
                <ContentContainer>
                  <Dashboard />
                </ContentContainer>
              </MainContainer>
            } />
          </Route>
          
          {/* Stats Route */}
          <Route path="/stats" element={<ProtectedRoute />}>
            <Route path="" element={
              <MainContainer>
                <Sidebar />
                <ContentContainer>
                  <Stats />
                </ContentContainer>
              </MainContainer>
            } />
          </Route>
          
          {/* Servers Route */}
          <Route path="/servers" element={<ProtectedRoute />}>
            <Route path="" element={
              <MainContainer>
                <Sidebar />
                <ContentContainer>
                  <Servers />
                </ContentContainer>
              </MainContainer>
            } />
          </Route>
          
          {/* API Explorer Route */}
          <Route path="/api-explorer" element={<ProtectedRoute />}>
            <Route path="" element={
              <MainContainer>
                <Sidebar />
                <ContentContainer>
                  <ApiExplorer />
                </ContentContainer>
              </MainContainer>
            } />
          </Route>
          
          {/* Protected Admin Routes */}
          <Route path="/admin" element={<ProtectedRoute requireAuth={true} />}>
            <Route path="" element={
              <MainContainer>
                <Sidebar />
                <ContentContainer>
                  <Dashboard isAdmin={true} />
                </ContentContainer>
              </MainContainer>
            } />
            {/* Add more admin routes here */}
          </Route>
          
          {/* Debug Route */}
          <Route path="/debug" element={
            <MainContainer>
              <Sidebar />
              <ContentContainer>
                <DebugPage />
              </ContentContainer>
            </MainContainer>
          } />
          
          {/* Fallback route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App; 