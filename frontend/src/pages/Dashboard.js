import React, { useEffect, useState, useRef } from 'react';
import { Box, Grid, Card, Typography, IconButton, Avatar, Fade, keyframes, Divider, Chip, LinearProgress, CardContent, Button, Alert, Paper, Container, Tooltip } from '@mui/material';
import { styled } from '@mui/material/styles';
import { motion, AnimatePresence } from 'framer-motion';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  Filler,
  ArcElement,
  BarElement,
} from 'chart.js';
import AutoStoriesIcon from '@mui/icons-material/AutoStories';
import GroupIcon from '@mui/icons-material/Group';
import MessageIcon from '@mui/icons-material/Message';
import SchoolIcon from '@mui/icons-material/School';
import PeopleAltIcon from '@mui/icons-material/PeopleAlt';
import CodeIcon from '@mui/icons-material/Code';
import StorageIcon from '@mui/icons-material/Storage';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import LanguageIcon from '@mui/icons-material/Language';
import SpeedIcon from '@mui/icons-material/Speed';
import MemoryIcon from '@mui/icons-material/Memory';
import ForumIcon from '@mui/icons-material/Forum';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import MusicNoteIcon from '@mui/icons-material/MusicNote';
import RefreshIcon from '@mui/icons-material/Refresh';
import { getStats, getActivity, getLifetimeStats, getTopCommands, getLanguageStats, getBotPerformance } from '../services/api';
import { isAuthenticated, hasAccess } from '../services/auth';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend,
  Filler,
  ArcElement,
  BarElement
);

const StyledCard = styled(motion(Card))(({ theme }) => ({
  padding: theme.spacing(3),
  borderRadius: 16,
  background: `linear-gradient(135deg, ${theme.palette.background.paper} 0%, rgba(34,34,58,0.9) 100%)`,
  backdropFilter: 'blur(10px)',
  border: '1px solid rgba(255,255,255,0.1)',
}));

const StatCard = styled(motion(Card))(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: 16,
  background: `linear-gradient(135deg, rgba(255,77,77,0.1) 0%, rgba(77,207,255,0.1) 100%)`,
  backdropFilter: 'blur(10px)',
  border: '1px solid rgba(255,255,255,0.1)',
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(2),
  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
  '&:hover': {
    transform: 'translateY(-5px)',
    boxShadow: '0 10px 20px rgba(0,0,0,0.2)',
  },
}));

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

const StyledAvatar = styled(Avatar)(({ theme, bgcolor }) => ({
  background: bgcolor || `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
  padding: theme.spacing(1),
  boxShadow: '0 4px 8px rgba(0,0,0,0.15)',
}));

const AnimatedValue = ({ value, color = 'inherit' }) => {
  const prevValue = useRef(value);
  const hasChanged = prevValue.current !== value;
  const [highlight, setHighlight] = useState(false);
  
  useEffect(() => {
    // Jika nilai berubah, aktifkan highlight
    if (prevValue.current !== value) {
      setHighlight(true);
      
      // Matikan highlight setelah 2 detik
      const timer = setTimeout(() => {
        setHighlight(false);
      }, 2000);
      
      prevValue.current = value;
      
      return () => clearTimeout(timer);
    }
  }, [value]);
  
  return (
    <Box sx={{ position: 'relative', display: 'inline-block' }}>
      <AnimatePresence mode="wait">
        <motion.div
          key={value}
          initial={hasChanged ? { opacity: 0, y: -10 } : false}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10, position: 'absolute', top: 0, left: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Typography 
            variant="h6" 
            sx={{ 
              fontWeight: 600, 
              color: highlight ? color : 'inherit',
              transition: 'color 0.5s ease',
              textShadow: highlight ? `0 0 8px ${color}40` : 'none',
              fontSize: { xs: '1rem', sm: '1.1rem', md: '1.25rem' },
            }}
          >
            {value}
          </Typography>
        </motion.div>
      </AnimatePresence>
    </Box>
  );
};

// Komponen counter animasi untuk total value
const AnimatedCounter = ({ value, duration = 1.5 }) => {
  const [displayValue, setDisplayValue] = useState(value);
  const previousValue = useRef(value);
  
  useEffect(() => {
    let startValue = previousValue.current;
    const endValue = value;
    const difference = endValue - startValue;
    
    if (difference === 0) return;
    
    let startTime;
    const step = timestamp => {
      if (!startTime) startTime = timestamp;
      
      const progress = Math.min((timestamp - startTime) / (duration * 1000), 1);
      const currentValue = Math.floor(startValue + difference * progress);
      
      setDisplayValue(currentValue.toLocaleString());
      
      if (progress < 1) {
        window.requestAnimationFrame(step);
      } else {
        previousValue.current = endValue;
      }
    };
    
    window.requestAnimationFrame(step);
  }, [value, duration]);
  
  return (
    <Typography variant="h5" sx={{ fontWeight: 700 }}>
      {displayValue}
    </Typography>
  );
};

// Define pulse animation keyframes
const pulseAnimation = keyframes`
  0% {
    box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.7);
  }
  70% {
    box-shadow: 0 0 0 6px rgba(76, 175, 80, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(76, 175, 80, 0);
  }
`;

const Dashboard = () => {
  const [stats, setStats] = useState({
    total_commands: 0,
    active_servers: 0,
    messages_today: 0,
    school_searches: 0,
    lifetime_commands: 0,
    lifetime_messages: 0,
    lifetime_school_searches: 0,
    average_commands_per_day: 0,
    bot_uptime_days: 0,
    users_reached: 0,
    response_time_ms: 0
  });
  const [activityData, setActivityData] = useState([]);
  const [topCommands, setTopCommands] = useState([]);
  const [languageData, setLanguageData] = useState({ language_usage: {} });
  const [performanceData, setPerformanceData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  const fetchDashboardData = async () => {
      try {
      const [statsData, activityData, lifetimeData, topCommandsData, languageData, performanceData] = await Promise.all([
          getStats(),
        getActivity(),
        getLifetimeStats(),
        getTopCommands(),
        getLanguageStats(),
        getBotPerformance()
        ]);
        
        if (statsData) {
          setStats(statsData);
        }
        
        if (activityData) {
          setActivityData(activityData);
        }
      
      if (topCommandsData) {
        setTopCommands(topCommandsData);
      }
      
      if (languageData) {
        setLanguageData(languageData);
      }
      
      if (performanceData) {
        setPerformanceData(performanceData);
      }
      
      // Update last update timestamp
      setLastUpdate(new Date());
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

  useEffect(() => {
    // Fetch data immediately on component mount
    fetchDashboardData();
    
    // Set up polling interval (every 5 seconds)
    const intervalId = setInterval(() => {
      fetchDashboardData();
    }, 5000);
    
    // Clean up the interval when component unmounts
    return () => clearInterval(intervalId);
  }, []);

  const chartData = {
    labels: activityData.map(item => new Date(item.timestamp).toLocaleDateString()),
    datasets: [
      {
        label: 'Total Commands',
        data: activityData.map(item => item.commands),
        fill: true,
        backgroundColor: 'rgba(255,77,77,0.1)',
        borderColor: '#FF4D4D',
        tension: 0.4,
      },
      {
        label: 'Active Servers',
        data: activityData.map(item => item.active_users),
        fill: true,
        backgroundColor: 'rgba(77,207,255,0.1)',
        borderColor: '#4DCFFF',
        tension: 0.4,
      },
      {
        label: 'Messages Today',
        data: activityData.map(item => item.messages),
        fill: true,
        backgroundColor: 'rgba(146,96,255,0.1)',
        borderColor: '#9260FF',
        tension: 0.4,
      },
      {
        label: 'School Searches',
        data: activityData.map(item => item.school_searches),
        fill: true,
        backgroundColor: 'rgba(255,189,89,0.1)',
        borderColor: '#FFBD59',
        tension: 0.4,
      }
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          boxWidth: 10,
          usePointStyle: true,
          pointStyle: 'circle'
        },
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(17, 25, 40, 0.8)',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        titleFont: {
          size: 14,
          weight: 'bold',
        },
        bodyFont: {
          size: 12,
        },
        padding: 10,
        cornerRadius: 8,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(255,255,255,0.1)',
        },
        ticks: {
          precision: 0,
          font: {
            size: 11
          }
        }
      },
      x: {
        grid: {
          color: 'rgba(255,255,255,0.1)',
        },
        ticks: {
          font: {
            size: 11
          }
        }
      },
    },
    elements: {
      point: {
        radius: 3,
        hoverRadius: 5,
      },
      line: {
        borderWidth: 2,
      }
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false
    },
  };

  const statCards = [
    { 
      title: 'Total Commands', 
      value: stats.total_commands.toLocaleString(), 
      icon: <AutoStoriesIcon />, 
      color: '#FF4D4D',
      description: 'Perintah yang dijalankan hari ini'
    },
    { 
      title: 'Active Servers', 
      value: stats.active_servers.toLocaleString(), 
      icon: <StorageIcon />, 
      color: '#4DCFFF',
      description: 'Server Discord yang aktif'
    },
    { 
      title: 'Messages Today', 
      value: stats.messages_today.toLocaleString(), 
      icon: <MessageIcon />, 
      color: '#9260FF',
      description: 'Pesan yang diproses hari ini'
    },
    { 
      title: 'School Searches', 
      value: stats.school_searches.toLocaleString(), 
      icon: <SchoolIcon />, 
      color: '#FFBD59',
      description: 'Pencarian sekolah hari ini'
    },
  ];

  // Buat komponen untuk statistik lifetime
  const lifetimeStats = [
    { 
      title: 'Lifetime Commands', 
      value: stats.lifetime_commands.toLocaleString(), 
      icon: <CodeIcon />, 
      color: '#FF4D4D',
      description: 'Total perintah sejak bot aktif',
      borderColor: 'linear-gradient(135deg, #FF4D4D, #FF8C8C)'
    },
    { 
      title: 'Lifetime Messages', 
      value: stats.lifetime_messages.toLocaleString(), 
      icon: <MessageIcon />, 
      color: '#9260FF',
      description: 'Total pesan sejak bot aktif',
      borderColor: 'linear-gradient(135deg, #9260FF, #B28AFF)'
    },
    { 
      title: 'Lifetime School Searches', 
      value: stats.lifetime_school_searches.toLocaleString(), 
      icon: <SchoolIcon />, 
      color: '#FFBD59',
      description: 'Total pencarian sekolah',
      borderColor: 'linear-gradient(135deg, #FFBD59, #FFDB9E)'
    },
    { 
      title: 'Average Commands/Day', 
      value: stats.average_commands_per_day.toLocaleString(), 
      icon: <AccessTimeIcon />, 
      color: '#4DCFFF',
      description: 'Rata-rata perintah per hari',
      borderColor: 'linear-gradient(135deg, #4DCFFF, #9FEAFF)'
    },
    { 
      title: 'Bot Uptime', 
      value: `${stats.bot_uptime_days} hari`, 
      icon: <LanguageIcon />, 
      color: '#50C878',
      description: 'Lama bot beroperasi',
      borderColor: 'linear-gradient(135deg, #50C878, #8FECAC)'
    }
  ];

  // Doughnut chart data untuk lifetime stats
  const lifetimeChartData = {
    labels: ['Lifetime Commands', 'Lifetime Messages', 'Lifetime School Searches'],
    datasets: [
      {
        data: [stats.lifetime_commands, stats.lifetime_messages, stats.lifetime_school_searches],
        backgroundColor: ['#FF4D4D', '#9260FF', '#FFBD59'],
        borderColor: ['#FF4D4D', '#9260FF', '#FFBD59'],
        borderWidth: 1,
        hoverOffset: 20,
      },
    ],
  };
  
  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '70%',
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          boxWidth: 10,
          padding: 20,
          usePointStyle: true,
          pointStyle: 'circle'
        }
      },
      tooltip: {
        backgroundColor: 'rgba(17, 25, 40, 0.8)',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        padding: 10,
        cornerRadius: 8,
        callbacks: {
          label: function(context) {
            let label = context.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed !== null) {
              label += context.parsed.toLocaleString();
            }
            return label;
          }
        }
      }
    },
  };

  // Top commands chart data
  const topCommandsChartData = {
    labels: topCommands.map(cmd => cmd.command_name),
    datasets: [
      {
        label: 'Command Usage',
        data: topCommands.map(cmd => cmd.usage_count),
        backgroundColor: [
          '#FF4D4D',
          '#4DCFFF',
          '#9260FF',
          '#FFBD59',
          '#50C878',
        ],
        borderColor: [
          '#FF4D4D',
          '#4DCFFF',
          '#9260FF',
          '#FFBD59',
          '#50C878',
        ],
        borderWidth: 1,
      },
    ],
  };
  
  const topCommandsOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `${context.label}: ${context.raw.toLocaleString()} uses (${topCommands[context.dataIndex]?.percentage}%)`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          display: false,
        }
      },
      x: {
        grid: {
          display: false,
        }
      }
    }
  };
  
  // Language usage chart data
  const languageChartData = {
    labels: Object.keys(languageData.language_usage).map(lang => {
      const langMap = {
        'id': 'Indonesia 🇮🇩',
        'en': 'English 🇬🇧',
        'jp': 'Japanese 🇯🇵',
      };
      return langMap[lang] || lang;
    }),
    datasets: [
      {
        label: 'Language Usage',
        data: Object.values(languageData.language_usage),
        backgroundColor: [
          '#FF4D4D',
          '#4DCFFF',
          '#9260FF',
        ],
        borderWidth: 0,
      },
    ],
  };
  
  const languageOptions = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '70%',
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          boxWidth: 10,
          padding: 15,
          usePointStyle: true,
          pointStyle: 'circle'
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `${context.label}: ${context.raw.toFixed(1)}%`;
          }
        }
      }
    },
  };

  // Add performance cards
  const performanceCards = performanceData ? [
    {
      title: 'Response Time',
      value: `${performanceData.response_time_ms} ms`,
      icon: <SpeedIcon />,
      color: '#FF4D4D',
      description: 'Average response time',
    },
    {
      title: 'CPU Usage',
      value: `${performanceData.cpu_usage.toFixed(1)}%`,
      icon: <MemoryIcon />,
      color: '#4DCFFF',
      description: 'Current CPU usage',
      progress: performanceData.cpu_usage / 100,
    },
    {
      title: 'Memory',
      value: `${performanceData.memory_usage.toFixed(1)} MB`,
      icon: <StorageIcon />,
      color: '#9260FF',
      description: 'Current memory usage',
      progress: performanceData.memory_usage / 500, // Assuming 500MB is max
    },
    {
      title: 'Uptime',
      value: `${performanceData.uptime_percentage.toFixed(1)}%`,
      icon: <AccessTimeIcon />,
      color: '#50C878',
      description: 'Server uptime',
      progress: performanceData.uptime_percentage / 100,
    },
  ] : [];

  if (loading) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography>Loading dashboard data...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Typography variant="h4" sx={{ fontWeight: 600 }}>
          Welcome to Ruri Dragon Dashboard
        </Typography>
          
          {lastUpdate && (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Box
                sx={{ 
                  width: 10, 
                  height: 10, 
                  bgcolor: '#4caf50', 
                  borderRadius: '50%', 
                  mr: 1,
                  animation: `${pulseAnimation} 2s infinite`,
                  position: 'relative'
                }}
              />
              <Typography variant="caption" color="text.secondary">
                Realtime - updated {lastUpdate.toLocaleTimeString()}
              </Typography>
            </Box>
          )}
        </Box>
      </motion.div>

      <Grid container spacing={3}>
        {statCards.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={stat.title}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ scale: 1.03 }}
            >
              <StatCard>
                <StyledAvatar sx={{ bgcolor: stat.color }}>
                  {stat.icon}
                </StyledAvatar>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    {stat.title}
                  </Typography>
                  <AnimatedValue value={stat.value} color={stat.color} />
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                    {stat.description}
                  </Typography>
                </Box>
              </StatCard>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <StyledCard>
              <Typography variant="h6" sx={{ mb: 3 }}>
                Activity Overview
              </Typography>
              <Box sx={{ height: 400 }}>
                <Line data={chartData} options={chartOptions} />
              </Box>
            </StyledCard>
          </motion.div>
        </Grid>
      </Grid>

      {/* Section Statistik Lifetime */}
      <Grid container sx={{ mt: 4 }}>
        <Grid item xs={12}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
              Statistik Lifetime Bot
            </Typography>
          </motion.div>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Lifetime stats cards */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={3}>
            {lifetimeStats.map((stat, index) => (
              <Grid item xs={12} sm={6} key={stat.title}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  whileHover={{ scale: 1.03 }}
                >
                  <GradientBorderCard borderColor={stat.color}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <StyledAvatar sx={{ bgcolor: stat.color, mr: 2 }}>
                        {stat.icon}
                      </StyledAvatar>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {stat.title}
                      </Typography>
                    </Box>
                    <Box sx={{ height: '3.5rem' }}>
                      <AnimatedValue 
                        value={stat.value} 
                        color={stat.color} 
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {stat.description}
                    </Typography>
                  </GradientBorderCard>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </Grid>
        
        {/* Lifetime stats chart */}
        <Grid item xs={12} md={4}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            whileHover={{ scale: 1.02 }}
          >
            <GradientBorderCard sx={{ height: '100%', display: 'flex', flexDirection: 'column' }} borderColor="#50C878">
              <Typography variant="h6" sx={{ mb: 2 }}>
                Distribusi Aktivitas
              </Typography>
              <Box sx={{ flexGrow: 1, height: 300, position: 'relative' }}>
                <Doughnut data={lifetimeChartData} options={doughnutOptions} />
                <Box
                  sx={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    textAlign: 'center'
                  }}
                >
                  <Typography variant="body2" color="text.secondary">
                    Total
                  </Typography>
                  <AnimatedCounter 
                    value={stats.lifetime_commands + stats.lifetime_messages + stats.lifetime_school_searches} 
                  />
                </Box>
              </Box>
            </GradientBorderCard>
          </motion.div>
        </Grid>
      </Grid>

      {/* Language & Command Stats Section */}
      <Grid container sx={{ mt: 4 }}>
        <Grid item xs={12}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
              Bot Usage Analytics
            </Typography>
          </motion.div>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Top Commands */}
        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            whileHover={{ scale: 1.02 }}
          >
            <GradientBorderCard borderColor="#FF4D4D">
              <Typography variant="h6" sx={{ mb: 2 }}>
                Top Commands
              </Typography>
              <Box sx={{ height: 300 }}>
                <Bar data={topCommandsChartData} options={topCommandsOptions} />
              </Box>
            </GradientBorderCard>
          </motion.div>
        </Grid>

        {/* Language Distribution */}
        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            whileHover={{ scale: 1.02 }}
          >
            <GradientBorderCard borderColor="#4DCFFF">
              <Typography variant="h6" sx={{ mb: 2 }}>
                Language Distribution
              </Typography>
              <Box sx={{ height: 300, position: 'relative' }}>
                <Doughnut data={languageChartData} options={languageOptions} />
              </Box>
            </GradientBorderCard>
          </motion.div>
        </Grid>
      </Grid>
      
      {/* Bot Performance Section */}
      <Grid container sx={{ mt: 4 }}>
        <Grid item xs={12}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
              Bot Performance
            </Typography>
          </motion.div>
        </Grid>
      </Grid>

      {performanceData && (
        <Grid container spacing={3}>
          {performanceCards.map((card, index) => (
            <Grid item xs={12} sm={6} md={3} key={card.title}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ scale: 1.03 }}
              >
                <GradientBorderCard borderColor={card.color}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <StyledAvatar sx={{ bgcolor: card.color, mr: 2 }}>
                      {card.icon}
                    </StyledAvatar>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {card.title}
                    </Typography>
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <AnimatedValue 
                      value={card.value} 
                      color={card.color} 
                    />
                  </Box>
                  {card.progress !== undefined && (
                    <Box sx={{ mb: 1, width: '100%' }}>
                      <LinearProgress 
                        variant="determinate" 
                        value={card.progress * 100} 
                        sx={{ 
                          height: 8, 
                          borderRadius: 5,
                          backgroundColor: 'rgba(255,255,255,0.1)',
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: card.color,
                            borderRadius: 5,
                          }
                        }} 
                      />
                    </Box>
                  )}
                  <Typography variant="body2" color="text.secondary">
                    {card.description}
                  </Typography>
                </GradientBorderCard>
              </motion.div>
            </Grid>
          ))}
          
          {/* API Calls Card */}
          {performanceData && (
            <Grid item xs={12}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.4 }}
                whileHover={{ scale: 1.01 }}
              >
                <GradientBorderCard borderColor="#FFBD59">
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    API Throughput
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Typography variant="h3" sx={{ fontWeight: 700, color: '#FFBD59' }}>
                      {performanceData.api_calls_per_minute}
                    </Typography>
                    <Typography variant="body1" color="text.secondary" sx={{ ml: 1 }}>
                      requests/minute
                    </Typography>
                  </Box>
                  <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center', gap: 2 }}>
                    <Chip label="API Healthy" color="success" size="small" />
                    <Chip label="No Throttling" color="primary" size="small" />
                  </Box>
                </GradientBorderCard>
              </motion.div>
            </Grid>
          )}
        </Grid>
      )}
    </Box>
  );
};

export default Dashboard; 