import React, { useState } from 'react';
import { 
  Box, 
  Drawer, 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText, 
  Typography, 
  IconButton,
  Divider,
  Button,
  useMediaQuery,
  Menu,
  MenuItem
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { styled } from '@mui/material/styles';
import { useNavigate, useLocation } from 'react-router-dom';
import DashboardIcon from '@mui/icons-material/Dashboard';
import SettingsIcon from '@mui/icons-material/Settings';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import GroupIcon from '@mui/icons-material/Group';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';
import LogoutIcon from '@mui/icons-material/Logout';
import LoginIcon from '@mui/icons-material/Login';
import PeopleIcon from '@mui/icons-material/People';
import PersonIcon from '@mui/icons-material/Person';
import RefreshIcon from '@mui/icons-material/Refresh';
import BugReportIcon from '@mui/icons-material/BugReport';
import ApiIcon from '@mui/icons-material/Api';
import { isAuthenticated, getCurrentUser, logout, logoutLocally } from '../services/auth';
import RuriLogo from './RuriLogo';
import ErrorBoundary from './ErrorBoundary';
import LogoutDialog from './LogoutDialog';

const drawerWidth = 240;

const LogoContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  marginBottom: theme.spacing(2),
}));

const SidebarHeader = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1, 2),
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
}));

const NavItem = styled(ListItem)(({ theme, active }) => ({
  borderRadius: theme.spacing(1),
  marginBottom: theme.spacing(0.5),
  '&:hover': {
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
  },
  ...(active && {
    backgroundColor: 'rgba(255, 77, 77, 0.15)',
    '&:before': {
      content: '""',
      position: 'absolute',
      left: 0,
      top: '50%',
      transform: 'translateY(-50%)',
      height: '60%',
      width: 4,
      backgroundColor: theme.palette.primary.main,
      borderRadius: '0 4px 4px 0',
    },
  }),
}));

const UserPanel = styled(Box)(({ theme }) => ({
  marginTop: 'auto',
  padding: theme.spacing(2),
  backgroundColor: 'rgba(34, 34, 58, 0.7)',
  borderRadius: theme.spacing(1),
  margin: theme.spacing(2),
}));

const Sidebar = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [open, setOpen] = useState(false);
  const [userMenuAnchor, setUserMenuAnchor] = useState(null);
  const [openLogoutDialog, setOpenLogoutDialog] = useState(false);
  
  const userMenuOpen = Boolean(userMenuAnchor);
  const isAuth = isAuthenticated();
  const hasPublicAccess = localStorage.getItem('ruri_public_access') === 'true';
  const currentUser = getCurrentUser();
  
  const toggleDrawer = () => {
    setOpen(!open);
  };

  const handleNavigation = (path) => {
    navigate(path);
    if (isMobile) {
      setOpen(false);
    }
  };
  
  const handleUserClick = (event) => {
    setUserMenuAnchor(event.currentTarget);
  };
  
  const handleCloseUserMenu = () => {
    setUserMenuAnchor(null);
  };
  
  const handleLogin = () => {
    navigate('/');
  };
  
  const handleLogoutClick = () => {
    handleCloseUserMenu();
    setOpenLogoutDialog(true);
  };
  
  const handleCloseLogoutDialog = () => {
    setOpenLogoutDialog(false);
  };
  
  const handleConfirmLogout = async () => {
    setOpenLogoutDialog(false);
    try {
      // Mencoba logout melalui backend
      await logout();
    } catch (error) {
      console.error('Error during logout, falling back to local logout:', error);
      // Fallback ke logout lokal jika backend gagal
      logoutLocally();
    }
  };
  
  const handleResetSession = () => {
    handleCloseUserMenu();
    console.log('Resetting session locally');
    // Hapus token dan user data dari storage
    localStorage.removeItem('ruri_token');
    localStorage.removeItem('ruri_user');
    localStorage.removeItem('ruri_public_access');
    sessionStorage.removeItem('ruri_token');
    // Redirect ke halaman login
    window.location.href = '/';
  };

  const navItems = [
    { 
      title: 'Dashboard', 
      icon: <DashboardIcon />, 
      path: '/dashboard',
      publicAccess: true
    },
    { 
      title: 'Statistik Server', 
      icon: <ShowChartIcon />, 
      path: '/stats',
      publicAccess: true
    },
    { 
      title: 'Server Discord', 
      icon: <GroupIcon />, 
      path: '/servers',
      publicAccess: true
    },
    { 
      title: 'API Explorer', 
      icon: <ApiIcon />, 
      path: '/api-explorer',
      publicAccess: true
    },
    { 
      title: 'Admin Panel', 
      icon: <SettingsIcon />, 
      path: '/admin',
      publicAccess: false
    },
    { 
      title: 'Debug', 
      icon: <BugReportIcon />, 
      path: '/debug',
      publicAccess: true
    },
  ];

  const drawer = (
    <>
      <SidebarHeader>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Ruri Dragon
          </Typography>
        {isMobile && (
          <IconButton edge="end" color="inherit" onClick={toggleDrawer}>
            <CloseIcon />
          </IconButton>
        )}
      </SidebarHeader>
      <LogoContainer>
        <ErrorBoundary size={100}>
          <RuriLogo size={100} />
        </ErrorBoundary>
      </LogoContainer>
      <Divider sx={{ mx: 2, backgroundColor: 'rgba(255,255,255,0.1)' }} />
      <List sx={{ px: 2, py: 1 }}>
        {navItems.map((item) => (
          // Hanya tampilkan menu admin jika pengguna login
          (item.publicAccess || isAuth) && (
            <NavItem
              key={item.title}
            button
            active={location.pathname === item.path ? 1 : 0}
              onClick={() => handleNavigation(item.path)}
          >
              <ListItemIcon sx={{ minWidth: 40 }}>
              {item.icon}
            </ListItemIcon>
              <ListItemText primary={item.title} />
            </NavItem>
          )
        ))}
      </List>
      
      <UserPanel>
        {isAuth ? (
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Box
              sx={{ 
                width: 40,
                height: 40,
                borderRadius: '50%',
                backgroundColor: 'primary.main',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mr: 2,
              }}
            >
              {currentUser?.avatar ? (
                <Box
                  component="img"
                  src={`https://cdn.discordapp.com/avatars/${currentUser.id}/${currentUser.avatar}.png`}
                  alt={currentUser.username}
                  sx={{ width: 40, height: 40, borderRadius: '50%' }}
                  onError={(e) => {
                    e.target.src = '/favicon.ico';
                  }}
                />
              ) : (
                <ErrorBoundary size={40}>
                  <RuriLogo size={40} withBorder={false} />
                </ErrorBoundary>
              )}
            </Box>
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                {currentUser?.username || 'User'}
              </Typography>
        <Typography variant="caption" color="text.secondary">
                Discord User
        </Typography>
      </Box>
            <IconButton 
              size="small" 
              onClick={handleUserClick}
              aria-controls={userMenuOpen ? 'user-menu' : undefined}
              aria-haspopup="true"
              aria-expanded={userMenuOpen ? 'true' : undefined}
            >
              <LogoutIcon fontSize="small" />
            </IconButton>
            <Menu
              id="user-menu"
              anchorEl={userMenuAnchor}
              open={userMenuOpen}
              onClose={handleCloseUserMenu}
              MenuListProps={{
                'aria-labelledby': 'user-button',
              }}
            >
              <MenuItem onClick={handleLogoutClick}>
                <LogoutIcon fontSize="small" sx={{ mr: 1 }} />
                Logout dari Discord
              </MenuItem>
              <MenuItem onClick={handleResetSession}>
                <RefreshIcon fontSize="small" sx={{ mr: 1 }} />
                Reset Sesi
              </MenuItem>
            </Menu>
          </Box>
        ) : hasPublicAccess ? (
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="body2" sx={{ mb: 1 }}>
              Akses Publik
            </Typography>
            <Button
              variant="outlined"
              size="small"
              startIcon={<LoginIcon />}
              onClick={handleLogin}
              fullWidth
              sx={{ mb: 1 }}
            >
              Login Discord
            </Button>
            <Button
              variant="outlined"
              size="small"
              color="error"
              startIcon={<RefreshIcon />}
              onClick={handleResetSession}
              fullWidth
            >
              Reset Sesi
            </Button>
          </Box>
        ) : (
          <Box>
            <Typography variant="body2" sx={{ mb: 1 }}>
              Not logged in
            </Typography>
            <Button
              variant="outlined"
              size="small"
              startIcon={<LoginIcon />}
              onClick={handleLogin}
              fullWidth
            >
              Login Discord
            </Button>
          </Box>
        )}
      </UserPanel>
    </>
  );

  return (
    <>
      {isMobile && (
        <IconButton
          color="inherit"
          aria-label="open drawer"
          edge="start"
          onClick={toggleDrawer}
          sx={{
            position: 'fixed',
            top: 10,
            left: 10,
            zIndex: 1200,
            backgroundColor: 'rgba(34, 34, 58, 0.8)',
            '&:hover': {
              backgroundColor: 'rgba(34, 34, 58, 0.9)',
            },
          }}
        >
          <MenuIcon />
        </IconButton>
      )}
      
      <Drawer
        variant={isMobile ? 'temporary' : 'permanent'}
        open={isMobile ? open : true}
        onClose={toggleDrawer}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile.
        }}
        sx={{
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            backgroundColor: theme.palette.background.paper,
            backgroundImage: 'linear-gradient(rgba(22, 25, 37, 0.7), rgba(22, 28, 36, 0.7))',
            backdropFilter: 'blur(8px)',
            border: 'none',
          },
        }}
      >
        {drawer}
      </Drawer>
      
      {/* Dialog konfirmasi logout */}
      <LogoutDialog 
        open={openLogoutDialog}
        onClose={handleCloseLogoutDialog}
        onConfirm={handleConfirmLogout}
      />
    </>
  );
};

export default Sidebar; 