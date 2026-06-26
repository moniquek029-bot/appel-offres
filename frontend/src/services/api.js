// src/services/api.js - Version CORRIGÉE

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
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
// INTERCEPTEUR REQUEST
// =============================================================================
api.interceptors.request.use(
  async (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    if (config.method === 'get' || config.method === 'GET') {
      config.params = {
        ...config.params,
        _t: Date.now()
      };
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// =============================================================================
// INTERCEPTEUR RESPONSE
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
            `${API_BASE_URL}token/refresh/`,
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
// ✅ FONCTION searchOffres CORRIGÉE
// =============================================================================
export const searchOffres = async ({ 
  keyword = '', 
  pays = '', 
  max_days = '', 
  domaine = '', 
  structure = '', 
  date_publication = '',  // ✅ Nom correct (pas date_debut)
  date_cloture = '',      // ✅ Nom correct (pas date_fin)
  page = 1 
} = {}) => {
  const params = new URLSearchParams();
  
  if (keyword && keyword.trim()) params.append('keyword', keyword.trim());
  if (pays) params.append('pays', pays);
  if (max_days) params.append('max_days', max_days);
  if (domaine) params.append('domaine', domaine);  // ✅ Pas 'categorie'
  if (structure) params.append('structure', structure);  // ✅ Pas 'organisme'
  
  // ✅ CORRECTION CRITIQUE : Envoyer les bons noms de paramètres
  if (date_publication) params.append('date_publication', date_publication);
  if (date_cloture) params.append('date_cloture', date_cloture);
  
  if (page) params.append('page', page);
  
  try {
    console.log('🔗 URL complète:', `/offres/?${params.toString()}`);
    console.log('📊 Paramètres:', Object.fromEntries(params));
    
    const response = await api.get(`/offres/?${params.toString()}`);
    
    console.log('✅ Réponse API offres:', {
      count: response.data.count,
      resultsLength: response.data.results?.length,
      next: response.data.next,
      previous: response.data.previous,
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

// =============================================================================
// AUTRES FONCTIONS API
// =============================================================================
export const getOffreById = async (id) => {
  try {
    const response = await api.get(`/offres/${id}/`);
    return response.data;
  } catch (error) {
    console.error('❌ Erreur chargement offre:', error);
    throw error;
  }
};

export const getOffresRecentes = async () => {
  try {
    const response = await api.get('/offres/recent/');
    return response.data.results || response.data;
  } catch (error) {
    console.error('❌ Erreur offres récentes:', error);
    return [];
  }
};

export const refreshOffres = async () => {
  try {
    const response = await api.get('/offres/', {
      params: { _force: Date.now() }
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