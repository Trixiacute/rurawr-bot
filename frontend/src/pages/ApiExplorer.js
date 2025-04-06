import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Accordion, 
  AccordionSummary, 
  AccordionDetails,
  Select, 
  MenuItem, 
  TextField, 
  Button, 
  CircularProgress,
  Alert,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Divider,
  InputLabel,
  FormControl,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { motion } from 'framer-motion';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CodeIcon from '@mui/icons-material/Code';
import ApiIcon from '@mui/icons-material/Api';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import SendIcon from '@mui/icons-material/Send';
import RefreshIcon from '@mui/icons-material/Refresh';
import InfoIcon from '@mui/icons-material/Info';

// Styled components untuk UI
const StyledAccordion = styled(Accordion)(({ theme }) => ({
  backgroundColor: 'rgba(34, 34, 58, 0.7)',
  borderRadius: '16px !important',
  marginBottom: theme.spacing(2),
  border: '1px solid rgba(255, 255, 255, 0.1)',
  overflow: 'hidden',
  '&:before': {
    display: 'none',
  },
  '&.Mui-expanded': {
    margin: theme.spacing(0, 0, 2, 0),
  }
}));

const StyledAccordionSummary = styled(AccordionSummary)(({ theme }) => ({
  borderRadius: '16px',
  background: 'linear-gradient(135deg, rgba(255,77,77,0.05) 0%, rgba(77,207,255,0.05) 100%)',
  '&.Mui-expanded': {
    borderBottomLeftRadius: 0,
    borderBottomRightRadius: 0,
  }
}));

const ApiTitle = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1.5),
}));

const ApiChip = styled(Chip)(({ theme, color }) => ({
  backgroundColor: color || 'rgba(77, 207, 255, 0.2)',
  color: theme.palette.text.primary,
  fontWeight: 600,
  fontSize: '0.7rem',
}));

const ResultCard = styled(Card)(({ theme }) => ({
  backgroundColor: 'rgba(34, 34, 58, 0.7)',
  borderRadius: 16,
  marginBottom: theme.spacing(2),
  border: '1px solid rgba(255, 255, 255, 0.1)',
  transition: 'transform 0.3s ease',
  '&:hover': {
    transform: 'translateY(-5px)',
  }
}));

const CodeBlock = styled(Box)(({ theme }) => ({
  backgroundColor: 'rgba(0, 0, 0, 0.3)',
  borderRadius: 8,
  padding: theme.spacing(2),
  fontFamily: 'monospace',
  fontSize: '0.9rem',
  overflowX: 'auto',
  '&::-webkit-scrollbar': {
    height: 6,
  },
  '&::-webkit-scrollbar-track': {
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 3,
  },
  '&::-webkit-scrollbar-thumb': {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderRadius: 3,
  }
}));

// Definisi kategori dan endpoint API
const API_CATEGORIES = [
  {
    name: 'Anime',
    endpoints: [
      { name: 'Kusonime Info', path: '/anime/kusonime', params: ['url'], description: 'Mendapatkan info anime dari Kusonime', method: 'GET' },
      { name: 'Anime Random', path: '/anime/random', params: [], description: 'Mendapatkan anime random', method: 'GET' },
      { name: 'Manga Info', path: '/anime/manga', params: ['query'], description: 'Mencari info manga', method: 'GET' },
    ]
  },
  {
    name: 'Downloader',
    endpoints: [
      { name: 'TikTok Downloader', path: '/downloader/tiktok', params: ['url'], description: 'Download video TikTok tanpa watermark', method: 'GET' },
      { name: 'Instagram Downloader', path: '/downloader/instagram', params: ['url'], description: 'Download media dari Instagram', method: 'GET' },
      { name: 'YouTube Downloader', path: '/downloader/youtube', params: ['url'], description: 'Download video dari YouTube', method: 'GET' },
    ]
  },
  {
    name: 'Pendidikan',
    endpoints: [
      { name: 'Cari KBBI', path: '/pendidikan/kbbi', params: ['kata'], description: 'Mencari kata di KBBI', method: 'GET' },
      { name: 'Brainly', path: '/pendidikan/brainly', params: ['query'], description: 'Mencari jawaban di Brainly', method: 'GET' },
    ]
  },
  {
    name: 'Random',
    endpoints: [
      { name: 'Fakta Menarik', path: '/randomtext/faktamenarik', params: [], description: 'Mendapatkan fakta menarik acak', method: 'GET' },
      { name: 'Quotes', path: '/randomtext/quotes', params: [], description: 'Mendapatkan quotes acak', method: 'GET' },
    ]
  }
];

const ApiExplorer = () => {
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedEndpoint, setSelectedEndpoint] = useState(null);
  const [params, setParams] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedPanel, setExpandedPanel] = useState(false);

  // Reset params when endpoint changes
  useEffect(() => {
    if (selectedEndpoint) {
      const initialParams = {};
      selectedEndpoint.params.forEach(param => {
        initialParams[param] = '';
      });
      setParams(initialParams);
    }
  }, [selectedEndpoint]);

  // Handle category change
  const handleCategoryChange = (event) => {
    setSelectedCategory(event.target.value);
    setSelectedEndpoint(null);
    setResult(null);
    setError(null);
  };

  // Handle endpoint selection
  const handleEndpointSelect = (endpoint) => {
    setSelectedEndpoint(endpoint);
    setResult(null);
    setError(null);
  };

  // Handle param change
  const handleParamChange = (param, value) => {
    setParams(prev => ({
      ...prev,
      [param]: value
    }));
  };

  // Format JSON for display
  const formatJSON = (json) => {
    return JSON.stringify(json, null, 2);
  };

  // Copy to clipboard
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  // Execute API call
  const executeApiCall = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Build URL with query parameters
      let url = `https://api.akuari.my.id${selectedEndpoint.path}`;
      const queryParams = new URLSearchParams();
      
      // Add parameters
      for (const [key, value] of Object.entries(params)) {
        if (value) {
          queryParams.append(key, value);
        }
      }
      
      // Append query parameters to URL
      if (queryParams.toString()) {
        url += `?${queryParams.toString()}`;
      }

      // Make API call
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error('API call error:', err);
      setError(err.message || 'Error fetching data');
    } finally {
      setLoading(false);
    }
  };

  // Render API result based on the type
  const renderApiResult = (result) => {
    if (!result) return null;

    // Handle image result
    if (result.result && typeof result.result === 'string' && (result.result.endsWith('.jpg') || result.result.endsWith('.png') || result.result.endsWith('.gif') || result.result.includes('image'))) {
      return (
        <Box sx={{ textAlign: 'center', my: 2 }}>
          <img 
            src={result.result} 
            alt="API Result" 
            style={{ maxWidth: '100%', maxHeight: '400px', borderRadius: 8 }} 
          />
        </Box>
      );
    }

    // Handle video result
    if (result.result && typeof result.result === 'string' && (result.result.endsWith('.mp4') || result.result.includes('video'))) {
      return (
        <Box sx={{ textAlign: 'center', my: 2 }}>
          <video 
            controls 
            src={result.result} 
            style={{ maxWidth: '100%', maxHeight: '400px', borderRadius: 8 }} 
          />
        </Box>
      );
    }

    // Handle complex result with multiple media items
    if (result.result && Array.isArray(result.result)) {
      return (
        <Grid container spacing={2} sx={{ mt: 1 }}>
          {result.result.map((item, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <ResultCard>
                <CardContent>
                  {typeof item === 'object' ? (
                    Object.entries(item).map(([key, value]) => (
                      <Box key={key} sx={{ mb: 1 }}>
                        {typeof value === 'string' && (value.endsWith('.jpg') || value.endsWith('.png') || value.includes('image')) ? (
                          <CardMedia
                            component="img"
                            height="180"
                            image={value}
                            alt={key}
                            sx={{ borderRadius: 2, mb: 1 }}
                          />
                        ) : typeof value === 'string' && (value.endsWith('.mp4') || value.includes('video')) ? (
                          <Box sx={{ mb: 1 }}>
                            <video controls src={value} style={{ width: '100%', borderRadius: 8 }} />
                          </Box>
                        ) : (
                          <Typography variant="body2">
                            <strong>{key}:</strong> {String(value)}
                          </Typography>
                        )}
                      </Box>
                    ))
                  ) : (
                    <Typography>{String(item)}</Typography>
                  )}
                </CardContent>
              </ResultCard>
            </Grid>
          ))}
        </Grid>
      );
    }

    // Default: display as JSON
    return (
      <Box sx={{ position: 'relative' }}>
        <CodeBlock>
          <pre>{formatJSON(result)}</pre>
        </CodeBlock>
        <Tooltip title="Copy JSON">
          <IconButton 
            sx={{ position: 'absolute', top: 8, right: 8 }}
            onClick={() => copyToClipboard(formatJSON(result))}
          >
            <ContentCopyIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
    );
  };

  return (
    <Box>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
          <ApiIcon fontSize="large" sx={{ color: 'primary.main' }} />
          <Typography variant="h4" sx={{ fontWeight: 700 }}>
            API Explorer
          </Typography>
        </Box>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <Paper
          sx={{
            p: 3,
            borderRadius: 4,
            mb: 4,
            backgroundColor: 'rgba(34, 34, 58, 0.7)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          }}
        >
          <Typography variant="h6" sx={{ mb: 2 }}>Pilih Kategori API</Typography>
          
          <FormControl fullWidth variant="outlined" sx={{ mb: 3 }}>
            <InputLabel id="category-select-label">Kategori</InputLabel>
            <Select
              labelId="category-select-label"
              value={selectedCategory}
              onChange={handleCategoryChange}
              label="Kategori"
              sx={{
                borderRadius: 2,
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                },
                '&:hover .MuiOutlinedInput-notchedOutline': {
                  borderColor: 'rgba(255, 255, 255, 0.3)',
                },
                '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                  borderColor: 'primary.main',
                },
              }}
            >
              {API_CATEGORIES.map((category) => (
                <MenuItem key={category.name} value={category.name}>
                  {category.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {selectedCategory && (
            <>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Endpoints {selectedCategory}
              </Typography>
              
              {API_CATEGORIES.find(cat => cat.name === selectedCategory)?.endpoints.map((endpoint) => (
                <StyledAccordion 
                  key={endpoint.path}
                  expanded={selectedEndpoint?.path === endpoint.path}
                  onChange={() => handleEndpointSelect(endpoint)}
                  TransitionProps={{ unmountOnExit: true }}
                >
                  <StyledAccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <ApiTitle>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {endpoint.name}
                      </Typography>
                      <ApiChip 
                        label={endpoint.method} 
                        color={endpoint.method === 'GET' ? 'rgba(77, 207, 255, 0.2)' : 'rgba(255, 77, 77, 0.2)'} 
                        size="small" 
                      />
                    </ApiTitle>
                  </StyledAccordionSummary>
                  
                  <AccordionDetails>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        {endpoint.description}
                      </Typography>
                      <Typography variant="caption" sx={{ display: 'block', mt: 1 }}>
                        <code>{`https://api.akuari.my.id${endpoint.path}`}</code>
                      </Typography>
                    </Box>
                    
                    {endpoint.params.length > 0 && (
                      <Box sx={{ mb: 3 }}>
                        <Typography variant="subtitle2" sx={{ mb: 1 }}>
                          Parameter
                        </Typography>
                        <Grid container spacing={2}>
                          {endpoint.params.map((param) => (
                            <Grid item xs={12} md={6} key={param}>
                              <TextField
                                fullWidth
                                label={param}
                                variant="outlined"
                                value={params[param] || ''}
                                onChange={(e) => handleParamChange(param, e.target.value)}
                                size="small"
                                sx={{
                                  '& .MuiOutlinedInput-root': {
                                    borderRadius: 2,
                                  }
                                }}
                              />
                            </Grid>
                          ))}
                        </Grid>
                      </Box>
                    )}
                    
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={executeApiCall}
                      disabled={loading}
                      endIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
                      sx={{ borderRadius: 2 }}
                    >
                      {loading ? 'Loading...' : 'Jalankan API'}
                    </Button>
                  </AccordionDetails>
                </StyledAccordion>
              ))}
            </>
          )}
        </Paper>
      </motion.div>

      {(result || error || loading) && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Paper
            sx={{
              p: 3,
              borderRadius: 4,
              backgroundColor: 'rgba(34, 34, 58, 0.7)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                <CodeIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Hasil API
              </Typography>
              
              {result && (
                <Tooltip title="Jalankan Ulang">
                  <IconButton onClick={executeApiCall} disabled={loading}>
                    <RefreshIcon />
                  </IconButton>
                </Tooltip>
              )}
            </Box>
            
            <Divider sx={{ mb: 2 }} />
            
            {loading && (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            )}
            
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}
            
            {result && renderApiResult(result)}
          </Paper>
        </motion.div>
      )}
    </Box>
  );
};

export default ApiExplorer; 