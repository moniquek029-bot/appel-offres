// src/services/api.js - Version finale avec anti-cache + pagination

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  // ✅ Désactiver le cache Axios par défaut
  cache: 'no-store',
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

// =============================================================================
// INTERCEPTEUR REQUEST - Ajout du token + anti-cache pour GET
// =============================================================================
api.interceptors.request.use(
  async (config) => {
    // ✅ Ajout du token d'authentification
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // ✅ ANTI-CACHE : Ajouter un timestamp aux requêtes GET pour forcer le re-fetch
    if (config.method === 'get' || config.method === 'GET') {
      config.params = {
        ...config.params,
        _t: Date.now()  // ← Timestamp unique à chaque requête
      };
      // Log pour debug (à retirer en production si besoin)
      // console.log(`🔄 GET ${config.url} avec anti-cache: _t=${config.params._t}`);
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// =============================================================================
// INTERCEPTEUR RESPONSE - Gestion du refresh token JWT
// =============================================================================
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      
      if (refreshToken && !isRefreshing) {
        isRefreshing = true;
        
        try {
          const { data } = await axios.post(
            `${API_BASE_URL}auth/token/refresh/`,
            { refresh: refreshToken }
          );
          
          localStorage.setItem('access_token', data.access);
          originalRequest.headers.Authorization = `Bearer ${data.access}`;
          processQueue(null, data.access);
          return api(originalRequest);
          
        } catch (refreshError) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          processQueue(refreshError, null);
          
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }
          return Promise.reject(refreshError);
          
        } finally {
          isRefreshing = false;
        }
      }
      
      if (!refreshToken) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// =============================================================================
// FONCTIONS API
// =============================================================================

// ✅ RECHERCHE DES OFFRES AVEC PAGINATION + ANTI-CACHE
export const searchOffres = async ({ 
  keyword = '', 
  pays = '', 
  max_days = '', 
  domaine = '', 
  structure = '', 
  date_debut='',
  date_fin='',
  page = 1 
} = {}) => {
  const params = new URLSearchParams();
  if (keyword && keyword.trim()) params.append('search', keyword.trim());
  if (pays) params.append('pays', pays);
  if (max_days) params.append('max_days', max_days);
  if (domaine) params.append('categorie', domaine);
  if (structure) params.append('organisme', structure);
  if (date_debut) params.append('date_publication_gte', date_debut);
  if (date_fin) params.append('date_publication_lte', date_fin);
  if (page) params.append('page', page);
  
  try {
    // ✅ L'intercepteur ajoute automatiquement _t=timestamp pour bypass cache
    const response = await api.get(`/offres/?${params.toString()}`);
    
    console.log('Réponse API offres:', {
      count: response.data.count,
      resultsLength: response.data.results?.length,
      next: response.data.next,
      previous: response.data.previous,
      // Log du paramètre anti-cache (pour debug)
      // cached: response.headers['x-cache'] || 'fresh'
    });
    
    return {
      results: response.data.results || [],
      count: response.data.count || 0,
      next: response.data.next,
      previous: response.data.previous,
    };
  } catch (error) {
    console.error('❌ Erreur API offres:', error);
    throw error;
  }
};

// ✅ DÉTAIL D'UNE OFFRE (avec anti-cache automatique)
export const getOffreById = async (id) => {
  try {
    const response = await api.get(`/offres/${id}/`);
    return response.data;
  } catch (error) {
    console.error('❌ Erreur chargement offre:', error);
    throw error;
  }
};

// ✅ OFFRES RÉCENTES (avec anti-cache automatique)
export const getOffresRecentes = async () => {
  try {
    const response = await api.get('/offres/recent/');
    return response.data.results || response.data;
  } catch (error) {
    console.error('❌ Erreur offres récentes:', error);
    return [];
  }
};

// ✅ NOUVEAU : Fonction de refresh manuel (pour forcer un re-fetch)
export const refreshOffres = async () => {
  try {
    // Force un nouveau timestamp pour garantir un fetch frais
    const response = await api.get('/offres/', {
      params: { _force: Date.now() }  // Paramètre supplémentaire pour forcer
    });
    return {
      results: response.data.results || [],
      count: response.data.count || 0,
      next: response.data.next,
      previous: response.data.previous,
    };
  } catch (error) {
    console.error('❌ Erreur refresh offres:', error);
    throw error;
  }
};

export default api;