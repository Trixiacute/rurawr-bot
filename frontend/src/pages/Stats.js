import React, { useState, useEffect } from 'react';
import { Box, Typography, Grid, Card, CircularProgress, Alert } from '@mui/material';
import { styled } from '@mui/material/styles';
import { motion } from 'framer-motion';
import { Bar, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { getActivity, getServers } from '../services/api';

// Registrasi komponen Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const GradientBorderCard = styled(motion(Card))(({ theme, borderColor }) => ({
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
    background: `linear-gradient(135deg, ${borderColor || '#FF4D4D'}, ${borderColor || '#4DCFFF'})`,
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

const ServerCard = styled(motion(Card))(({ theme }) => ({
  padding: theme.spacing(3),
  borderRadius: 16,
  background: `linear-gradient(135deg, rgba(255,77,77,0.1) 0%, rgba(77,207,255,0.1) 100%)`,
  backdropFilter: 'blur(10px)',
  border: '1px solid rgba(255,255,255,0.1)',
  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
  '&:hover': {
    transform: 'translateY(-5px)',
    boxShadow: '0 10px 20px rgba(0,0,0,0.2)',
  },
}));

const Stats = () => {
  const [activityData, setActivityData] = useState([]);
  const [serversData, setServersData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [activityResult, serversResult] = await Promise.all([
          getActivity(),
          getServers()
        ]);
        
        setActivityData(activityResult || []);
        setServersData(serversResult || []);
      } catch (err) {
        console.error('Error fetching stats data:', err);
        setError('Gagal memuat data statistik. Silakan coba lagi nanti.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Data untuk grafik aktivitas
  const activityChartData = {
    labels: activityData.map(item => item.timestamp),
    datasets: [
      {
        label: 'Commands',
        data: activityData.map(item => item.commands),
        borderColor: '#FF4D4D',
        backgroundColor: 'rgba(255, 77, 77, 0.2)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Messages',
        data: activityData.map(item => item.messages),
        borderColor: '#4DCFFF',
        backgroundColor: 'rgba(77, 207, 255, 0.2)',
        fill: true,
        tension: 0.4
      }
    ]
  };

  // Opsi untuk grafik aktivitas
  const activityChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Aktivitas 7 Hari Terakhir'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      },
      x: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      }
    }
  };

  return (
    <Box>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h4" sx={{ mb: 4, fontWeight: 700 }}>
          Statistik Server
        </Typography>
      </motion.div>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : (
        <>
          {/* Grafik Aktivitas */}
          <Grid container spacing={4}>
            <Grid item xs={12}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 }}
              >
                <GradientBorderCard>
                  <Typography variant="h6" sx={{ mb: 3 }}>Aktivitas Bot</Typography>
                  <Box sx={{ height: 400 }}>
                    <Line data={activityChartData} options={activityChartOptions} />
                  </Box>
                </GradientBorderCard>
              </motion.div>
            </Grid>

            {/* Statistik Server */}
            <Grid item xs={12}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                <Typography variant="h5" sx={{ my: 3, fontWeight: 600 }}>
                  Daftar Server
                </Typography>
              </motion.div>
              
              <Grid container spacing={3}>
                {serversData.map((server, index) => (
                  <Grid item xs={12} md={6} lg={4} key={server.id}>
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.5, delay: 0.3 + (index * 0.1) }}
                    >
                      <ServerCard>
                        <Typography variant="h6" sx={{ mb: 2 }}>
                          {server.name}
                        </Typography>
                        
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="body2" color="text.secondary">
                            Member: {server.member_count}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Commands: {server.commands_used}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Perintah Populer: {server.most_used_command}
                          </Typography>
                        </Box>
                        
                        <Box 
                          sx={{ 
                            display: 'inline-block',
                            px: 1.5, 
                            py: 0.5, 
                            bgcolor: 'rgba(77, 207, 255, 0.1)',
                            borderRadius: 1,
                            fontSize: '0.75rem'
                          }}
                        >
                          {server.region}
                        </Box>
                      </ServerCard>
                    </motion.div>
                  </Grid>
                ))}
              </Grid>
            </Grid>
          </Grid>
        </>
      )}
    </Box>
  );
};

export default Stats; 