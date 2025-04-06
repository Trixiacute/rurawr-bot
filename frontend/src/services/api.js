import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getStats = async () => {
  try {
    const response = await api.get('/api/stats');
    return response.data;
  } catch (error) {
    console.error('Error fetching stats:', error);
    return null;
  }
};

export const getActivity = async () => {
  try {
    const response = await api.get('/api/activity');
    return response.data;
  } catch (error) {
    console.error('Error fetching activity:', error);
    return [];
  }
};

export const getLifetimeStats = async () => {
  try {
    const response = await api.get('/api/lifetime-stats');
    return response.data;
  } catch (error) {
    console.error('Error fetching lifetime stats:', error);
    return null;
  }
};

export const getTopCommands = async () => {
  try {
    const response = await api.get('/api/top-commands');
    return response.data;
  } catch (error) {
    console.error('Error fetching top commands:', error);
    return [];
  }
};

export const getLanguageStats = async () => {
  try {
    const response = await api.get('/api/language-stats');
    return response.data;
  } catch (error) {
    console.error('Error fetching language stats:', error);
    return { language_usage: {} };
  }
};

export const getBotPerformance = async () => {
  try {
    const response = await api.get('/api/bot-performance');
    return response.data;
  } catch (error) {
    console.error('Error fetching bot performance:', error);
    return null;
  }
};

export const getServers = async () => {
  try {
    const response = await api.get('/api/servers');
    return response.data;
  } catch (error) {
    console.error('Error fetching servers:', error);
    return [];
  }
}; 