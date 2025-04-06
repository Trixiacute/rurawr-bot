import React, { useState, useEffect } from 'react';
import { Box, Typography, Grid, Card, CircularProgress, Alert, Divider, Avatar, Chip } from '@mui/material';
import { styled } from '@mui/material/styles';
import { motion } from 'framer-motion';
import GroupIcon from '@mui/icons-material/Group';
import CommandIcon from '@mui/icons-material/Code';
import StorageIcon from '@mui/icons-material/Storage';
import LanguageIcon from '@mui/icons-material/Language';
import { getServers } from '../services/api';

const ServerCard = styled(motion(Card))(({ theme }) => ({
  padding: theme.spacing(3),
  borderRadius: 16,
  background: `linear-gradient(135deg, ${theme.palette.background.paper} 0%, rgba(34,34,58,0.9) 100%)`,
  backdropFilter: 'blur(10px)',
  position: 'relative',
  overflow: 'hidden',
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
  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
  '&:hover': {
    transform: 'translateY(-5px)',
    boxShadow: '0 10px 20px rgba(0,0,0,0.1)',
  },
}));

const StatItem = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1.5),
  marginBottom: theme.spacing(2),
}));

const StatIcon = styled(Box)(({ theme, bgcolor }) => ({
  width: 36,
  height: 36,
  borderRadius: '50%',
  backgroundColor: bgcolor || 'rgba(255, 77, 77, 0.1)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: bgcolor ? theme.palette.getContrastText(bgcolor) : '#FF4D4D',
}));

const Servers = () => {
  const [serversData, setServersData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const result = await getServers();
        setServersData(result || []);
      } catch (err) {
        console.error('Error fetching servers data:', err);
        setError('Gagal memuat data server. Silakan coba lagi nanti.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <Box>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h4" sx={{ mb: 4, fontWeight: 700 }}>
          Server Discord
        </Typography>
      </motion.div>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : (
        <Grid container spacing={3}>
          {serversData.map((server, index) => (
            <Grid item xs={12} md={6} key={server.id}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <ServerCard>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                      {server.name.charAt(0)}
                    </Avatar>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {server.name}
                    </Typography>
                  </Box>

                  <Divider sx={{ my: 2 }} />

                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <StatItem>
                        <StatIcon>
                          <GroupIcon fontSize="small" />
                        </StatIcon>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Jumlah Member
                          </Typography>
                          <Typography variant="body1" sx={{ fontWeight: 600 }}>
                            {server.member_count}
                          </Typography>
                        </Box>
                      </StatItem>
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <StatItem>
                        <StatIcon bgcolor="#4DCFFF">
                          <CommandIcon fontSize="small" />
                        </StatIcon>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Perintah Digunakan
                          </Typography>
                          <Typography variant="body1" sx={{ fontWeight: 600 }}>
                            {server.commands_used}
                          </Typography>
                        </Box>
                      </StatItem>
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <StatItem>
                        <StatIcon bgcolor="#FF9800">
                          <StorageIcon fontSize="small" />
                        </StatIcon>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Perintah Populer
                          </Typography>
                          <Typography variant="body1" sx={{ fontWeight: 600 }}>
                            {server.most_used_command}
                          </Typography>
                        </Box>
                      </StatItem>
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <StatItem>
                        <StatIcon bgcolor="#673AB7">
                          <LanguageIcon fontSize="small" />
                        </StatIcon>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Bahasa dan Region
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                            <Chip 
                              label={server.language.toUpperCase()} 
                              size="small" 
                              sx={{ backgroundColor: 'rgba(255, 77, 77, 0.1)' }}
                            />
                            <Chip 
                              label={server.region} 
                              size="small"
                              sx={{ backgroundColor: 'rgba(77, 207, 255, 0.1)' }}
                            />
                          </Box>
                        </Box>
                      </StatItem>
                    </Grid>
                  </Grid>
                </ServerCard>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default Servers; 