import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  Typography,
  Box
} from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';

const LogoutDialog = ({ open, onClose, onConfirm }) => {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      aria-labelledby="logout-dialog-title"
      aria-describedby="logout-dialog-description"
      PaperProps={{
        sx: {
          borderRadius: 2,
          padding: 1,
          backgroundColor: '#1A1A2E'
        }
      }}
    >
      <DialogTitle id="logout-dialog-title" sx={{ display: 'flex', alignItems: 'center' }}>
        <LogoutIcon sx={{ mr: 2, color: '#FF4D4D' }} />
        <Typography variant="h6">Konfirmasi Logout</Typography>
      </DialogTitle>
      <DialogContent>
        <DialogContentText id="logout-dialog-description">
          Anda akan keluar dari akun Discord. Ini akan menghapus sesi login Anda dan Anda perlu login ulang untuk mengakses fitur admin.
        </DialogContentText>
        <Box sx={{ mt: 2, p: 2, bgcolor: 'rgba(255, 77, 77, 0.1)', borderRadius: 1 }}>
          <Typography variant="body2" sx={{ color: '#FF4D4D' }}>
            Catatan: Anda masih dapat mengakses fitur dasar dashboard tanpa login dengan memilih "Akses Publik" pada halaman login.
          </Typography>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="inherit">
          Batal
        </Button>
        <Button 
          onClick={onConfirm} 
          variant="contained" 
          color="error"
          startIcon={<LogoutIcon />}
        >
          Logout
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default LogoutDialog; 