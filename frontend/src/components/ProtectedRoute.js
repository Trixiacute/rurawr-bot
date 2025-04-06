import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { isAuthenticated, hasAccess } from '../services/auth';

// Fungsi untuk memeriksa apakah pengguna memiliki akses publik
const hasPublicAccess = () => {
  return localStorage.getItem('ruri_public_access') === 'true';
};

const ProtectedRoute = ({ requireAuth = false, requireAdmin = false }) => {
  const isAuth = isAuthenticated();
  const hasAccessRights = hasAccess();
  const isPublicAccess = hasPublicAccess();
  
  // Jika rute memerlukan autentikasi (misalnya, untuk fitur admin)
  if (requireAuth) {
    // Check if user is authenticated
    if (!isAuth) {
      return <Navigate to="/" replace />;
    }
    
    // Check if user has access to the dashboard
    if (!hasAccessRights) {
      return <Navigate to="/unauthorized" replace />;
    }
  } else {
    // Untuk rute yang bisa diakses publik, izinkan jika publik atau terotentikasi
    if (!isPublicAccess && !isAuth) {
      return <Navigate to="/" replace />;
    }
  }
  
  // If user is authenticated or public access, render the child routes
  return <Outlet />;
};

export default ProtectedRoute; 