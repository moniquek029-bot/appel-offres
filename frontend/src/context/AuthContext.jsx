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

  // ✅ Initialisation au chargement : restaure la session depuis localStorage
  useEffect(() => {
    const initAuth = () => {
      const token = localStorage.getItem('access_token');
      const refreshToken = localStorage.getItem('refresh_token');
      const role = localStorage.getItem('user_role');
      const email = localStorage.getItem('user_email');
      const nom = localStorage.getItem('user_nom');
      
      if (token && role) {
        setUser({ token, refreshToken, role, email, nom });
      }
      setLoading(false);
    };
    initAuth();
  }, []);

  // ✅ Login : stocke les DEUX tokens + infos utilisateur
  const login = async (email, password) => {
    try {
      const { data } = await api.post('/auth/login/', { email, password });
      
      // Stockage sécurisé des tokens
      const accessToken = data.access || data.tokens?.access;
      const refreshToken = data.refresh || data.tokens?.refresh;
      
      if (accessToken) {
        localStorage.setItem('access_token', accessToken);
      }
      if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken);
      }
      
      // Stockage des infos utilisateur (pour l'UI)
      if (data.user) {
        localStorage.setItem('user_role', data.user.role || '');
        localStorage.setItem('user_email', data.user.email || '');
        localStorage.setItem('user_nom', data.user.nom || '');
        
        setUser({
          token: accessToken,
          refreshToken,
          role: data.user.role,
          email: data.user.email,
          nom: data.user.nom
        });
      } else {
        setUser({ token: accessToken, refreshToken });
      }
      
      console.log(' Login réussi');
      return { success: true, data };
      
    } catch (err) {
      console.error(' Erreur login:', err.response?.data || err.message);
      return { 
        success: false, 
        error: err.response?.data?.detail || 'Identifiants invalides' 
      };
    }
  };

  // ✅ Logout : nettoyage complet
  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_nom');
    setUser(null);
    console.log(' Déconnexion effectuée');
  };

  // ✅ Refresh token : avec gestion d'erreur
  const refreshToken = async () => {
    const refresh = localStorage.getItem('refresh_token');
    if (!refresh) {
      console.warn(' Aucun refresh token disponible');
      return null;
    }
    
    try {
      const { data } = await api.post('/auth/token/refresh/', { refresh });
      const newAccess = data.access;
      
      if (newAccess) {
        localStorage.setItem('access_token', newAccess);
        // Met à jour l'état user avec le nouveau token
        setUser(prev => prev ? { ...prev, token: newAccess } : null);
        console.log(' Token rafraîchi avec succès');
        return newAccess;
      }
      return null;
    } catch (err) {
      console.error(' Échec du refresh token:', err.response?.data || err.message);
      // Token refresh invalide → déconnexion forcée
      logout();
      return null;
    }
  };

  // ✅ Valeurs exposées au contexte
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