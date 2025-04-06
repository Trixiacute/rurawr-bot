import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { styled } from '@mui/material/styles';
import { motion } from 'framer-motion';
import { logout } from '../services/auth';

const ErrorBox = styled(motion.div)(({ theme }) => ({
  padding: theme.spacing(5),
  maxWidth: 600,
  margin: '0 auto',
  textAlign: 'center',
}));

const Unauthorized = () => {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
      }}
    >
      <ErrorBox
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Box
          component="img"
          src="/unauthorized.png"
          alt="Unauthorized"
          sx={{
            width: 150,
            height: 150,
            marginBottom: 3,
          }}
          onError={(e) => {
            e.target.src = 'https://via.placeholder.com/150?text=Unauthorized';
          }}
        />

        <Typography variant="h4" color="error" sx={{ mb: 2, fontWeight: 700 }}>
          Akses Ditolak
        </Typography>

        <Typography variant="body1" sx={{ mb: 4, color: 'text.secondary' }}>
          Anda tidak memiliki akses ke dashboard Ruri Dragon. Untuk mengakses dashboard, Anda harus berada di server Discord yang berisi bot Ruri Dragon.
        </Typography>

        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
          <Button
            variant="contained"
            color="primary"
            onClick={() => window.open('https://discord.gg/YOUR_INVITE_LINK', '_blank')}
            sx={{ borderRadius: 2 }}
          >
            Join Server Discord
          </Button>
          
          <Button
            variant="outlined"
            color="error"
            onClick={logout}
            sx={{ borderRadius: 2 }}
          >
            Logout
          </Button>
        </Box>
      </ErrorBox>
    </Box>
  );
};

export default Unauthorized; 