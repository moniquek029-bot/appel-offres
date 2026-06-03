// src/context/AuthContext.jsx
import React, { createContext, useState, useEffect, useContext } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = () => {
      const token = localStorage.getItem('access_token');
      const refreshToken = localStorage.getItem('refresh_token');
      const userStr = localStorage.getItem('user');
      
      if (token && userStr) {
        try {
          const userData = JSON.parse(userStr);
          setUser({
            token,
            refreshToken,
            role: userData.role,
            email: userData.email,
            nom: userData.nom || `${userData.first_name || ''} ${userData.last_name || ''}`,
            id: userData.id
          });
        } catch (e) {
          console.error('Erreur parsing user:', e);
        }
      }
      setLoading(false);
    };
    initAuth();
  }, []);

  const login = async (email, password) => {
    try {
      const { data } = await api.post('/auth/login/', { email, password });
      
      const accessToken = data.access;
      const refreshToken = data.refresh;
      const userData = data.user;
      
      if (accessToken && userData) {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
        localStorage.setItem('user', JSON.stringify(userData));
        
        setUser({
          token: accessToken,
          refreshToken,
          role: userData.role,
          email: userData.email,
          nom: userData.nom || `${userData.first_name || ''} ${userData.last_name || ''}`,
          id: userData.id
        });
        
        return { success: true, data };
      }
      
      return { success: false, error: 'Données de réponse invalides' };
      
    } catch (err) {
      console.error('Erreur login:', err.response?.data || err.message);
      return { 
        success: false, 
        error: err.response?.data?.detail || 'Email ou mot de passe incorrect' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const refreshToken = async () => {
    const refresh = localStorage.getItem('refresh_token');
    if (!refresh) return null;
    
    try {
      const { data } = await api.post('/auth/token/refresh/', { refresh });
      if (data.access) {
        localStorage.setItem('access_token', data.access);
        setUser(prev => prev ? { ...prev, token: data.access } : null);
        return data.access;
      }
      return null;
    } catch (err) {
      logout();
      return null;
    }
  };

  const value = {
    user,
    loading,
    login,
    logout,
    refreshToken,
    isAuthenticated: !!user?.token,
    role: user?.role,
    email: user?.email,
    nom: user?.nom
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};