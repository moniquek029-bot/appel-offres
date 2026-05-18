// src/services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/api/',
  headers: { 'Content-Type': 'application/json' },
});

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) prom.reject(error);
    else prom.resolve(token);
  });
  failedQueue = [];
};

// Intercepteur REQUEST : Ajoute le token si présent
api.interceptors.request.use(
  async (config) => {
    const token = localStorage.getItem('access_token');
    
    // N'ajoute le token que s'il existe
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercepteur RESPONSE : Gère automatiquement 401/403
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // 🔹 Cas 1 : Token expiré (401) ET on n'a pas déjà essayé de rafraîchir
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      
      // Si on a un refresh token, on tente de rafraîchir
      if (refreshToken && !isRefreshing) {
        isRefreshing = true;
        
        try {
          const { data } = await axios.post(
            `${api.defaults.baseURL}auth/token/refresh/`,
            { refresh: refreshToken },
            { headers: { 'Content-Type': 'application/json' } }
          );
          
          // Stocke le nouveau token
          localStorage.setItem('access_token', data.access);
          
          // Met à jour l'header de la requête originale
          originalRequest.headers.Authorization = `Bearer ${data.access}`;
          
          processQueue(null, data.access);
          return api(originalRequest); // Réessaie la requête initiale
          
        } catch (refreshError) {
          // Refresh token invalide → déconnexion forcée
          console.warn(' Session expirée - Déconnexion automatique');
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          processQueue(refreshError, null);
          
          // Redirige vers login si on n'y est pas déjà
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }
          return Promise.reject(refreshError);
          
        } finally {
          isRefreshing = false;
        }
      }
      
      // Si pas de refresh token → déconnexion simple
      if (!refreshToken) {
        console.warn(' Token invalide sans refresh - Nettoyage');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
      }
    }
    
    // 🔹 Cas 2 : 403 Forbidden (permissions) → on loggue mais on ne déconnecte pas
    if (error.response?.status === 403) {
      console.warn(' Accès refusé (403) - Vérifiez les permissions');
    }
    
    return Promise.reject(error);
  }
);

// ✅ Fonction de recherche (inchangée)
export const searchOffres = async ({ keyword = '', country = '', ordering = '' } = {}) => {
  const params = new URLSearchParams();
  if (keyword && keyword.trim()) params.append('search', keyword.trim());
  if (country) params.append('pays', country);
  if (ordering) params.append('ordering', ordering);
  
  try {
    const response = await api.get(`/offres/?${params.toString()}`);
    return {
      results: response.data.results || response.data,
      count: response.data.count || (response.data.results?.length || 0),
      next: response.data.next,
      previous: response.data.previous,
    };
  } catch (error) {
    console.error(' Erreur API offres:', error);
    throw error;
  }
};

export const getOffreById = async (id) => {
  try {
    const response = await api.get(`/offres/${id}/`);
    return response.data;
  } catch (error) {
    console.error(' Erreur chargement offre:', error);
    throw error;
  }
};

export default api;