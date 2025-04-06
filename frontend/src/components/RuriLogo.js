import React from 'react';
import { Box } from '@mui/material';

// Komponen logo Ruri yang terinspirasi karakter manga dengan try-catch
const RuriLogo = ({ size = 100, withBorder = true }) => {
  try {
    // Versi paling sederhana dari logo, mengurangi potensi error
    return (
      <Box
        sx={{ 
          width: size, 
          height: size, 
          borderRadius: '50%',
          border: withBorder ? '2px solid #FF4D4D' : 'none',
          padding: 1,
          background: '#22223A',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        {/* Wajah simple berbentuk lingkaran */}
        <Box 
          sx={{ 
            width: '60%',
            height: '60%',
            borderRadius: '50%',
            backgroundColor: '#f0e6e6',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative'
          }}
        >
          {/* Text "R" sebagai fallback */}
          <Box 
            component="span" 
            sx={{ 
              color: '#FF4D4D', 
              fontWeight: 'bold', 
              fontSize: size > 60 ? '1.5rem' : '1rem' 
            }}
          >
            R
          </Box>
        </Box>
      </Box>
    );
  } catch (error) {
    console.error('Error rendering RuriLogo:', error);
    // Fallback sangat sederhana jika terjadi error
    return (
      <Box
        sx={{ 
          width: size, 
          height: size, 
          borderRadius: '50%',
          border: withBorder ? '2px solid #FF4D4D' : 'none',
          padding: 1,
          background: '#22223A',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        R
      </Box>
    );
  }
};

export default RuriLogo; 