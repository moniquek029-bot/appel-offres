// src/pages/Profil.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const Profil = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    telephone: '',
  });

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const response = await api.get('/profile/');
      setFormData({
        first_name: response.data.first_name || '',
        last_name: response.data.last_name || '',
        email: response.data.email || '',
        telephone: response.data.telephone || '',
      });
    } catch (err) {
      console.error('Erreur chargement profil:', err);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    setError('');

    try {
      await api.put('/profile/', formData);
      setMessage(' Profil mis à jour avec succès !');
      setTimeout(() => setMessage(''), 3000);
    } catch (err) {
      setError(' Erreur lors de la mise à jour du profil');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-md-8">
          <div className="card shadow" style={{ position: 'relative' }}>
            {/* En-tête avec croix de fermeture */}
            <div className="card-header text-white d-flex justify-content-between align-items-center" 
                 style={{ 
                   background: 'linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%)',
                   position: 'relative'
                 }}>
              <h4 className="mb-0">
                <i className="bi bi-person-fill me-2"></i>
                Mon Profil
              </h4>
              
              {/* Croix de fermeture */}
              <button 
                onClick={() => navigate(-1)}
                className="btn btn-link text-white p-0"
                style={{
                  fontSize: '1.5rem',
                  lineHeight: 1,
                  opacity: 0.8,
                  transition: 'all 0.2s ease',
                  width: '36px',
                  height: '36px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  borderRadius: '50%',
                  border: '2px solid rgba(255, 255, 255, 0.3)'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.opacity = '1';
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.47)';
                  e.currentTarget.style.transform = 'rotate(90deg)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.opacity = '0.8';
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.transform = 'rotate(0deg)';
                }}
                title="Fermer"
              >
                <i className="bi bi-x-lg"></i>
              </button>
            </div>
            
            <div className="card-body p-4">
              {message && (
                <div className="alert alert-success alert-dismissible fade show" role="alert">
                  {message}
                  <button type="button" className="btn-close" onClick={() => setMessage('')}></button>
                </div>
              )}

              {error && (
                <div className="alert alert-danger alert-dismissible fade show" role="alert">
                  {error}
                  <button type="button" className="btn-close" onClick={() => setError('')}></button>
                </div>
              )}

              <form onSubmit={handleSubmit}>
                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label className="form-label fw-semibold">
                      <i className="bi bi-person me-1"></i>
                      Prénom
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      name="first_name"
                      value={formData.first_name}
                      onChange={handleChange}
                      required
                    />
                  </div>

                  <div className="col-md-6 mb-3">
                    <label className="form-label fw-semibold">
                      <i className="bi bi-person me-1"></i>
                      Nom
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      name="last_name"
                      value={formData.last_name}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>

                <div className="mb-3">
                  <label className="form-label fw-semibold">
                    <i className="bi bi-envelope me-1"></i>
                    Email
                  </label>
                  <input
                    type="email"
                    className="form-control"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    disabled
                    style={{ backgroundColor: '#E9ECEF' }}
                  />
                  <small className="text-muted">L'email ne peut pas être modifié</small>
                </div>

                <div className="mb-3">
                  <label className="form-label fw-semibold">
                    <i className="bi bi-telephone me-1"></i>
                    Téléphone
                  </label>
                  <input
                    type="tel"
                    className="form-control"
                    name="telephone"
                    value={formData.telephone}
                    onChange={handleChange}
                  />
                </div>

                <div className="d-flex gap-2">
                  <button 
                    type="submit" 
                    className="btn btn-primary flex-grow-1"
                    disabled={loading}
                    style={{ background: 'linear-gradient(135deg, var(--primary) 0%, #D35400 100%)', border: 'none' }}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Enregistrement...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-check-lg me-2"></i>
                        Enregistrer les modifications
                      </>
                    )}
                  </button>
                  
                  <button 
                    type="button"
                    className="btn btn-outline-secondary"
                    onClick={() => navigate(-1)}
                  >
                    Annuler
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profil;