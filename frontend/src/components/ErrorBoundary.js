import React, { Component } from 'react';
import { Box, Typography } from '@mui/material';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    // Update state sehingga render berikutnya akan menampilkan fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Error logging bisa ditambahkan di sini
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      // Fallback UI
      return (
        <Box 
          sx={{ 
            width: this.props.size || 100, 
            height: this.props.size || 100,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: '#22223A',
            borderRadius: '50%',
            border: '2px solid #FF4D4D',
            color: 'white'
          }}
        >
          <Typography variant="caption">Ruri</Typography>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary; 