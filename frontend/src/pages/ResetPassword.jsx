// src/pages/ResetPassword.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../services/api';

const ResetPassword = () => {
  const { token } = useParams();
  const navigate = useNavigate();
  
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(true);
  const [tokenValid, setTokenValid] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [success, setSuccess] = useState(false);

  // Vérifier la validité du token au chargement
  useEffect(() => {
    const validateToken = async () => {
      try {
        const response = await api.get(`/auth/password-reset/validate/${token}/`);
        if (response.data.valid) {
          setTokenValid(true);
        } else {
          setMessage({
            type: 'danger',
            text: response.data.error || 'Lien de réinitialisation invalide.'
          });
        }
      } catch (error) {
        setMessage({
          type: 'danger',
          text: error.response?.data?.error || 'Lien de réinitialisation invalide ou expiré.'
        });
      } finally {
        setValidating(false);
      }
    };

    validateToken();
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (newPassword.length < 8) {
      setMessage({ type: 'danger', text: 'Le mot de passe doit contenir au moins 8 caractères' });
      return;
    }
    
    if (newPassword !== confirmPassword) {
      setMessage({ type: 'danger', text: 'Les mots de passe ne correspondent pas' });
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await api.post('/auth/password-reset/confirm/', {
        token,
        new_password: newPassword,
        confirm_password: confirmPassword
      });
      
      setSuccess(true);
      setMessage({
        type: 'success',
        text: response.data.message
      });
      
      setTimeout(() => {
        navigate('/login');
      }, 3000);
      
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Erreur lors de la réinitialisation';
      setMessage({ type: 'danger', text: errorMsg });
    } finally {
      setLoading(false);
    }
  };

  const getPasswordStrength = () => {
    if (newPassword.length === 0) return { level: 0, text: '', color: '' };
    if (newPassword.length < 8) return { level: 1, text: 'Faible', color: 'danger' };
    
    let score = 0;
    if (newPassword.length >= 8) score++;
    if (/[A-Z]/.test(newPassword)) score++;
    if (/[0-9]/.test(newPassword)) score++;
    if (/[^A-Za-z0-9]/.test(newPassword)) score++;
    
    if (score <= 1) return { level: 1, text: 'Faible', color: 'danger' };
    if (score === 2) return { level: 2, text: 'Moyen', color: 'warning' };
    if (score === 3) return { level: 3, text: 'Bon', color: 'info' };
    return { level: 4, text: 'Excellent', color: 'success' };
  };

  const passwordStrength = getPasswordStrength();

  if (validating) {
    return (
      <div className="container py-5 text-center" style={{ minHeight: '85vh' }}>
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Vérification...</span>
        </div>
        <p className="mt-3 text-muted">Vérification du lien...</p>
      </div>
    );
  }

  if (!tokenValid && !success) {
    return (
      <div className="container d-flex justify-content-center align-items-center" 
           style={{ minHeight: '85vh', backgroundColor: '#f8fafc' }}>
        <div className="card border-0 shadow-lg" style={{ maxWidth: '480px', borderRadius: '16px' }}>
          <div className="card-body p-5 text-center">
            <div className="d-flex justify-content-center mb-3">
              <div 
                className="d-flex align-items-center justify-content-center rounded-circle"
                style={{ width: '70px', height: '70px', background: '#f8d7da' }}
              >
                <i className="bi bi-x-circle-fill text-danger" style={{ fontSize: '2rem' }}></i>
              </div>
            </div>
            <h4 className="fw-bold text-danger mb-3">Lien invalide</h4>
            <p className="text-muted small mb-4">{message.text}</p>
            <Link to="/login" className="btn btn-primary">
              <i className="bi bi-arrow-left me-2"></i>
              Retour à la connexion
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container d-flex justify-content-center align-items-center" 
         style={{ minHeight: '85vh', backgroundColor: '#f8fafc' }}>
      <div className="card border-0 shadow-lg" 
           style={{ width: '100%', maxWidth: '480px', borderRadius: '16px', overflow: 'hidden' }}>
        
        {/* Header */}
        <div className="py-4 px-4 text-center" 
             style={{ 
               background: success 
                 ? 'linear-gradient(135deg, #059669 0%, #047857 100%)'
                 : 'linear-gradient(135deg, #1E3A8A 0%, #172554 100%)',
               color: 'white'
             }}>
          <div className="d-flex justify-content-center mb-3">
            <div className="d-flex align-items-center justify-content-center" 
                 style={{ 
                   width: '60px', 
                   height: '60px', 
                   borderRadius: '50%',
                   background: success 
                     ? 'linear-gradient(135deg, #10b981, #059669)'
                     : 'linear-gradient(135deg, #F59E0B, #1E3A8A)',
                   boxShadow: '0 4px 15px rgba(245, 158, 11, 0.4)'
                 }}>
              <i className={`bi ${success ? 'bi-check-circle-fill' : 'bi-shield-lock-fill'} text-white`} 
                 style={{ fontSize: '1.5rem' }}></i>
            </div>
          </div>
          <h2 className="h3 mb-1 fw-bold">
            {success ? 'Mot de passe modifié !' : 'Nouveau mot de passe'}
          </h2>
          <p className="mb-0 opacity-75" style={{ fontSize: '0.9rem' }}>
            {success ? 'Redirection vers la connexion...' : 'Choisissez un mot de passe sécurisé'}
          </p>
        </div>

        <div className="card-body p-4 p-lg-5">
          
          {message.text && (
            <div className={`alert alert-${message.type} py-2 small d-flex align-items-start`} 
                 role="alert" 
                 style={{ borderRadius: '8px', border: 'none' }}>
              <i className={`bi ${message.type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-triangle-fill'} me-2 mt-1`}></i>
              <div>{message.text}</div>
            </div>
          )}

          {!success ? (
            <form onSubmit={handleSubmit}>
              {/* Nouveau mot de passe */}
              <div className="mb-3">
                <label className="form-label small fw-semibold" style={{ color: '#334155' }}>
                  Nouveau mot de passe
                </label>
                <div className="input-group">
                  <span className="input-group-text" 
                        style={{ 
                          backgroundColor: '#f1f5f9',
                          border: '1px solid #e2e8f0',
                          borderRadius: '8px 0 0 8px',
                          color: '#1E3A8A',
                          width: '40px',
                          justifyContent: 'center'
                        }}>
                    <i className="bi bi-lock-fill"></i>
                  </span>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    className="form-control"
                    placeholder="Minimum 8 caractères"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                    disabled={loading}
                    style={{ 
                      borderRadius: '0',
                      borderColor: '#e2e8f0',
                      borderRight: 'none'
                    }}
                  />
                  <button
                    type="button"
                    className="btn btn-outline-secondary"
                    onClick={() => setShowPassword(!showPassword)}
                    style={{ 
                      borderRadius: '0 8px 8px 0',
                      borderColor: '#e2e8f0',
                      borderLeft: 'none',
                      width: '40px',
                      backgroundColor: '#f1f5f9'
                    }}
                  >
                    <i className={`bi ${showPassword ? 'bi-eye-slash-fill' : 'bi-eye-fill'}`}></i>
                  </button>
                </div>
                
                {/* Indicateur de force */}
                {newPassword && (
                  <div className="mt-2">
                    <div className="d-flex gap-1 mb-1">
                      {[1, 2, 3, 4].map((level) => (
                        <div
                          key={level}
                          className="flex-fill rounded"
                          style={{
                            height: '4px',
                            background: level <= passwordStrength.level 
                              ? `var(--bs-${passwordStrength.color})` 
                              : '#e9ecef'
                          }}
                        ></div>
                      ))}
                    </div>
                    <small className={`text-${passwordStrength.color}`}>
                      Force : {passwordStrength.text}
                    </small>
                  </div>
                )}
              </div>

              {/* Confirmation */}
              <div className="mb-3">
                <label className="form-label small fw-semibold" style={{ color: '#334155' }}>
                  Confirmer le mot de passe
                </label>
                <div className="input-group">
                  <span className="input-group-text" 
                        style={{ 
                          backgroundColor: '#f1f5f9',
                          border: '1px solid #e2e8f0',
                          borderRadius: '8px 0 0 8px',
                          color: '#1E3A8A',
                          width: '40px',
                          justifyContent: 'center'
                        }}>
                    <i className="bi bi-lock-fill"></i>
                  </span>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    className={`form-control ${
                      confirmPassword && newPassword !== confirmPassword ? 'is-invalid' : ''
                    }`}
                    placeholder="Retapez le mot de passe"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    disabled={loading}
                    style={{ 
                      borderRadius: '0 8px 8px 0',
                      borderColor: '#e2e8f0'
                    }}
                  />
                </div>
                {confirmPassword && newPassword !== confirmPassword && (
                  <div className="invalid-feedback d-block">
                    Les mots de passe ne correspondent pas
                  </div>
                )}
              </div>

              <button
                type="submit"
                className="btn w-100 py-2 fw-semibold shadow-sm"
                style={{ 
                  borderRadius: '8px',
                  fontSize: '1rem',
                  background: 'linear-gradient(135deg, #1E3A8A, #172554)',
                  border: 'none',
                  color: 'white'
                }}
                disabled={loading || !newPassword || !confirmPassword}
              >
                {loading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2"></span>
                    Réinitialisation...
                  </>
                ) : (
                  <>
                    <i className="bi bi-check-circle me-2"></i>
                    Réinitialiser le mot de passe
                  </>
                )}
              </button>
            </form>
          ) : (
            <div className="text-center py-2">
              <div className="spinner-border text-success" role="status">
                <span className="visually-hidden">Redirection...</span>
              </div>
            </div>
          )}

          <div className="text-center mt-4 pt-3 border-top" style={{ borderColor: '#e2e8f0' }}>
            <Link to="/login" 
                  className="text-decoration-none small" 
                  style={{ color: '#1E3A8A', fontWeight: '500' }}>
              <i className="bi bi-arrow-left me-1"></i>
              Retour à la connexion
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResetPassword;