import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import AuthProvider from './context/AuthContext';
import Login from './pages/LogIn';
import Dashboard from './pages/Dashboard';
import ProtectedRoute from './pages/ProtectedRoute';

const App: React.FC = () => {
  return (
    <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          
          {/* Protected routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<Dashboard />} />
            {/* Add more protected routes as needed */}
          </Route>
          
          {/* Redirect to login by default */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
    </AuthProvider>
  );
};

export default App;