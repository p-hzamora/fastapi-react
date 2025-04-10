// src/components/ProtectedRoute.tsx
import React from 'react';
import useAuth  from '../hooks/useAuth';

import { Navigate, Outlet, useLocation } from 'react-router-dom';

const ProtectedRoute: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  // Show loading indicator while checking authentication
  if (isLoading) {
    return <div>Loading...</div>;
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Render the protected content
  return <Outlet />;
};

export default ProtectedRoute;