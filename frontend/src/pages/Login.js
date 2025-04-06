import React, { useState } from 'react';
import { Box, Typography, Button, Card, Divider, Tooltip, IconButton } from '@mui/material';
import { styled } from '@mui/material/styles';
import { motion } from 'framer-motion';
import SvgIcon from '@mui/material/SvgIcon';
import { getDiscordLoginUrl, setPublicAccess } from '../services/auth';
import { useNavigate } from 'react-router-dom';
import RuriLogo from '../components/RuriLogo';
import ErrorBoundary from '../components/ErrorBoundary';
import BugReportIcon from '@mui/icons-material/BugReport';

// Discord Icon SVG
const DiscordIcon = (props) => (
  <SvgIcon {...props}>
    <path d="M19.27 5.33C17.94 4.71 16.5 4.26 15 4a.09.09 0 0 0-.07.03c-.18.33-.39.76-.53 1.09a16.09 16.09 0 0 0-4.8 0c-.14-.34-.35-.76-.54-1.09-.01-.02-.04-.03-.07-.03-1.5.26-2.93.71-4.27 1.33-.01 0-.02.01-.03.02-2.72 4.07-3.47 8.03-3.1 11.95 0 .02.01.04.03.05 1.8 1.32 3.53 2.12 5.24 2.65.03.01.06 0 .07-.02.4-.55.76-1.13 1.07-1.74.02-.04 0-.08-.04-.09-.57-.22-1.11-.48-1.64-.78-.04-.02-.04-.08-.01-.11.11-.08.22-.17.33-.25.02-.02.05-.02.07-.01 3.44 1.57 7.15 1.57 10.55 0 .02-.01.05-.01.07.01.11.09.22.17.33.26.04.03.04.09-.01.11-.52.31-1.07.56-1.64.78-.04.01-.05.06-.04.09.32.61.68 1.19 1.07 1.74.03.02.06.03.09.02 1.72-.53 3.45-1.33 5.25-2.65.02-.01.03-.03.03-.05.44-4.53-.73-8.46-3.1-11.95-.01-.01-.02-.02-.04-.02zM8.52 14.91c-1.03 0-1.89-.95-1.89-2.12s.84-2.12 1.89-2.12c1.06 0 1.9.96 1.89 2.12 0 1.17-.84 2.12-1.89 2.12zm6.97 0c-1.03 0-1.89-.95-1.89-2.12s.84-2.12 1.89-2.12c1.06 0 1.9.96 1.89 2.12 0 1.17-.83 2.12-1.89 2.12z" />
  </SvgIcon>
);

const GradientBorderCard = styled(motion(Card))(({ theme }) => ({
  padding: theme.spacing(5),
  borderRadius: 16,
  background: `linear-gradient(135deg, ${theme.palette.background.paper} 0%, rgba(34,34,58,0.9) 100%)`,
  backdropFilter: 'blur(10px)',
  position: 'relative',
  overflow: 'hidden',
  maxWidth: 500,
  margin: '0 auto',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    borderRadius: 16,
    padding: '2px',
    background: 'linear-gradient(135deg, #FF4D4D, #4DCFFF)',
    mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
    maskComposite: 'exclude',
    pointerEvents: 'none',
  },
}));

const DiscordButton = styled(Button)(({ theme }) => ({
  backgroundColor: '#7289DA',
  color: 'white',
  padding: '12px 24px',
  borderRadius: 8,
  fontSize: '1rem',
  fontWeight: 'bold',
  textTransform: 'none',
  '&:hover': {
    backgroundColor: '#5f73bc',
  },
  marginTop: theme.spacing(3),
}));

const PublicAccessButton = styled(Button)(({ theme }) => ({
  backgroundColor: 'transparent',
  color: '#4DCFFF',
  padding: '12px 24px',
  borderRadius: 8,
  fontSize: '1rem',
  fontWeight: 'bold',
  textTransform: 'none',
  border: '1px solid #4DCFFF',
  '&:hover': {
    backgroundColor: 'rgba(77, 207, 255, 0.1)',
  },
  marginTop: theme.spacing(2),
}));

const Login = () => {
  const navigate = useNavigate();
  const [showDebug, setShowDebug] = useState(false);
  
  const handleLogin = () => {
    window.location.href = getDiscordLoginUrl();
  };
  
  const handlePublicAccess = () => {
    // Set public access flag in localStorage
    setPublicAccess(true);
    // Navigate to dashboard
    navigate('/dashboard');
  };
  
  const toggleDebugMode = () => {
    setShowDebug(!showDebug);
  };

  return (
    <Box 
      sx={{ 
        minHeight: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)'
      }}
    >
      <GradientBorderCard
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Box sx={{ textAlign: 'center' }}>
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
          >
            <Box sx={{ mb: 3 }}>
              <ErrorBoundary size={120}>
                <RuriLogo size={120} />
              </ErrorBoundary>
            </Box>
          </motion.div>
          
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
            Ruri Dragon Dashboard
          </Typography>
          
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            Dashboard statistik bot Discord Ruri Dragon
          </Typography>
          
          <DiscordButton 
            variant="contained" 
            startIcon={<DiscordIcon />}
            onClick={handleLogin}
            fullWidth
          >
            Login dengan Discord
          </DiscordButton>
          
          <Box sx={{ my: 3, position: 'relative' }}>
            <Divider sx={{ my: 2 }}>
              <Typography variant="caption" color="text.secondary">
                ATAU
              </Typography>
            </Divider>
          </Box>
          
          <PublicAccessButton
            variant="outlined"
            onClick={handlePublicAccess}
            fullWidth
          >
            Akses Publik
          </PublicAccessButton>
          
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 3 }}>
            Login Discord diperlukan untuk akses fitur tambahan
          </Typography>
          
          {showDebug && (
            <Box sx={{ mt: 3, p: 2, bgcolor: 'rgba(77, 207, 255, 0.1)', borderRadius: 1 }}>
              <Typography variant="body2" sx={{ mb: 1 }}>Debug Mode</Typography>
              <Button
                variant="contained"
                size="small"
                color="secondary"
                fullWidth
                sx={{ mb: 1 }}
                onClick={() => {
                  // Buka endpoint debug di tab baru
                  window.open('http://localhost:8000/auth/debug', '_blank');
                }}
              >
                Lihat Status Backend
              </Button>
              <Button
                variant="contained"
                size="small"
                color="error"
                fullWidth
                onClick={() => {
                  // Hapus semua data local storage
                  localStorage.clear();
                  sessionStorage.clear();
                  window.location.reload();
                }}
              >
                Reset Semua Data
              </Button>
            </Box>
          )}
        </Box>
        
        <Tooltip title="Debug Mode">
          <IconButton 
            sx={{ position: 'absolute', bottom: 10, right: 10 }}
            onClick={toggleDebugMode}
          >
            <BugReportIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </GradientBorderCard>
    </Box>
  );
};

export default Login; 