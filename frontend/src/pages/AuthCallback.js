import React, { useEffect, useState } from 'react';
import { Box, Typography, CircularProgress, Button } from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { authenticateWithDiscord } from '../services/auth';

const AuthCallback = () => {
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const authenticateUser = async () => {
      // Mendapatkan kode dari URL parameters
      const urlParams = new URLSearchParams(location.search);
      const code = urlParams.get('code');
      
      if (!code) {
        setError('Tidak ada kode otorisasi ditemukan.');
        return;
      }
      
      try {
        // Dapatkan redirect_uri yang sama dengan yang digunakan untuk login
        const redirectUri = window.location.origin + '/auth/callback';
        
        // Panggil fungsi autentikasi dengan code dan redirect_uri
        const result = await authenticateWithDiscord(code, redirectUri);
        
        if (result && result.has_access) {
          navigate('/dashboard');
        } else {
          navigate('/unauthorized');
        }
      } catch (err) {
        console.error('Authentication error:', err);
        setError(err.message || 'Terjadi kesalahan saat autentikasi dengan Discord.');
      }
    };

    authenticateUser();
  }, [location, navigate]);

  const handleRetry = () => {
    navigate('/');
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)'
      }}
    >
      {error ? (
        <Box sx={{ textAlign: 'center', p: 3 }}>
          <Typography variant="h5" color="error" sx={{ mb: 2 }}>
            Error Autentikasi
          </Typography>
          <Typography variant="body1" sx={{ mb: 3 }}>{error}</Typography>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={handleRetry}
            sx={{ borderRadius: 2 }}
          >
            Kembali ke Login
          </Button>
        </Box>
      ) : (
        <>
          <CircularProgress size={60} sx={{ mb: 4, color: '#7289DA' }} />
          <Typography variant="h6" sx={{ mb: 2 }}>
            Proses autentikasi...
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Menghubungkan dengan Discord
          </Typography>
        </>
      )}
    </Box>
  );
};

export default AuthCallback; 