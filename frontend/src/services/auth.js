import axios from 'axios';
import { api } from './api';

// Discord OAuth2 Constants
const DISCORD_CLIENT_ID = process.env.REACT_APP_DISCORD_CLIENT_ID || '1231886560606158859'; // Gunakan ID default untuk development
const REDIRECT_URI = `${window.location.origin}/auth/callback`;

// Discord Auth URL
const DISCORD_AUTH_URL = `https://discord.com/api/oauth2/authorize?client_id=${DISCORD_CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&response_type=code&scope=identify%20guilds`;

// Local storage keys
const TOKEN_KEY = 'ruri_discord_token';
const USER_KEY = 'ruri_user_data';

/**
 * Mendapatkan URL login Discord OAuth2
 */
export const getDiscordLoginUrl = () => {
  const clientId = process.env.REACT_APP_DISCORD_CLIENT_ID || '1231886560606158859';
  const redirectUri = encodeURIComponent(window.location.origin + '/auth/callback');
  const scope = 'identify guilds';
  
  return `https://discord.com/api/oauth2/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scope}`;
};

/**
 * Authenticate with Discord using auth code
 */
export const authenticateWithDiscord = async (code, redirectUri) => {
  try {
    const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    
    // Menambahkan redirectUri ke request body
    const response = await fetch(`${apiUrl}/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        code,
        redirect_uri: redirectUri
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Authentication failed');
    }

    const data = await response.json();
    
    // Save token and user data to localStorage
    localStorage.setItem(TOKEN_KEY, data.access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(data.user));
    
    return data;
  } catch (error) {
    console.error('Error authenticating with Discord:', error);
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('Response error data:', error.response.data);
      console.error('Response error status:', error.response.status);
      
      if (error.response.data && error.response.data.detail) {
        throw new Error(`Error dari server: ${error.response.data.detail}`);
      }
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received:', error.request);
      throw new Error('Tidak ada respon dari server. Periksa koneksi internet Anda dan coba lagi.');
    }
    throw error;
  }
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = () => {
  try {
    const tokenData = JSON.parse(localStorage.getItem(TOKEN_KEY));
    const userData = JSON.parse(localStorage.getItem(USER_KEY));
    
    if (!tokenData || !userData) {
      return false;
    }
    
    // Check if token is expired (1 day)
    const now = Date.now();
    const tokenAge = now - tokenData.timestamp;
    const tokenMaxAge = 24 * 60 * 60 * 1000; // 1 day in milliseconds
    
    if (tokenAge > tokenMaxAge) {
      // Token expired
      logout();
      return false;
    }
    
    return true;
  } catch (error) {
    return false;
  }
};

/**
 * Get current user data
 */
export const getCurrentUser = () => {
  try {
    const userData = JSON.parse(localStorage.getItem(USER_KEY));
    return userData || null;
  } catch (error) {
    return null;
  }
};

/**
 * Logout user
 */
export const logout = async () => {
  try {
    // Gunakan metode GET untuk logout
    const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/auth/logout`, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    console.log('Logout status:', response.status);
    
    if (response.ok) {
      const data = await response.json();
      console.log('Logout response:', data);
    }
  } catch (error) {
    console.error('Error during logout:', error);
  } finally {
    // Hapus token dan user data dari storage dengan key yang benar
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem('ruri_public_access');
    sessionStorage.removeItem(TOKEN_KEY);

    // Redirect ke halaman login
    window.location.href = '/';
  }
};

/**
 * Logout user tanpa memanggil backend (fallback)
 */
export const logoutLocally = () => {
  // Hapus token dan user data dari storage dengan key yang benar
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem('ruri_public_access');
  sessionStorage.removeItem(TOKEN_KEY);

  // Redirect ke halaman login
  window.location.href = '/';
};

/**
 * Check if user has access to the dashboard (is in an allowed server)
 */
export const hasAccess = () => {
  try {
    const userData = getCurrentUser();
    
    if (!userData) {
      return false;
    }
    
    // Check if access flag is true (set by backend)
    return userData.has_access === true;
  } catch (error) {
    return false;
  }
};

// Fungsi untuk mengecek apakah user memiliki akses publik
export const hasPublicAccess = () => {
  return localStorage.getItem('ruri_public_access') === 'true';
};

// Fungsi untuk memberikan akses publik
export const setPublicAccess = (value = true) => {
  if (value) {
    localStorage.setItem('ruri_public_access', 'true');
  } else {
    localStorage.removeItem('ruri_public_access');
  }
}; 