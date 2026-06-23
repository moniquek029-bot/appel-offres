// src/pages/Login.jsx
import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const isMountedRef = useRef(true);

  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isMountedRef.current) return;
    
    setError('');
    setLoading(true);
    
    try {
      const result = await login(email, password, rememberMe);
      
      if (result.success && isMountedRef.current) {
        // ✅ Reset du formulaire après connexion réussie
        setEmail('');
        setPassword('');
        
        setTimeout(() => {
          if (isMountedRef.current) {
            navigate('/');
          }
        }, 100);
      } else if (!result.success && isMountedRef.current) {
        setError(result.error || 'Erreur de connexion');
        setLoading(false);
      }
    } catch (err) {
      if (isMountedRef.current) {
        setError(err.response?.data?.detail || 'Erreur de connexion');
        setLoading(false);
      }
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(prev => !prev);
  };

  return (
    <div className="container d-flex justify-content-center align-items-center" 
         style={{ minHeight: '85vh', backgroundColor: '#f8fafc' }}>
      <div className="card border-0 shadow-lg" 
           style={{ 
             width: '100%', 
             maxWidth: '480px', 
             borderRadius: '16px',
             overflow: 'hidden'
           }}>
        
        {/* Header */}
        <div className="py-4 px-4 text-center" 
             style={{ 
               background: 'linear-gradient(135deg, #1E3A8A 0%, #172554 100%)',
               color: 'white'
             }}>
          <div className="d-flex justify-content-center mb-3">
            <div className="d-flex align-items-center justify-content-center" 
                 style={{ 
                   width: '60px', 
                   height: '60px', 
                   borderRadius: '50%',
                   background: 'linear-gradient(135deg, #F59E0B, #1E3A8A)',
                   boxShadow: '0 4px 15px rgba(245, 158, 11, 0.4)'
                 }}>
              <span className="text-white fw-bold" style={{ fontSize: '1.5rem' }}>E</span>
            </div>
          </div>
          <h2 className="h3 mb-1 fw-bold">Connexion</h2>
          <p className="mb-0 opacity-75" style={{ fontSize: '0.9rem' }}>
            Espace EXPERTISE-ID
          </p>
        </div>

        <div className="card-body p-4 p-lg-5">
          
          {error && (
            <div className="alert alert-danger py-2 small" 
                 role="alert" 
                 style={{ borderRadius: '8px', border: 'none' }}>
              <i className="bi bi-exclamation-triangle-fill me-2"></i>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} autoComplete="on">
            
            {/* Email - autocomplétion native du navigateur */}
            <div className="mb-3">
              <label className="form-label small fw-semibold" style={{ color: '#334155' }}>
                {/*<i className="bi bi-envelope-fill me-1 text-muted"></i>*/}
                Adresse e-mail
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
                  <i className="bi bi-envelope-fill"></i>
                </span>
                <input
                  type="email"
                  name="email"
                  className="form-control"
                  placeholder="exemple@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="email"
                  required
                  style={{ 
                    borderRadius: '0 8px 8px 0',
                    borderColor: '#e2e8f0',
                    flex: 1
                  }}
                />
              </div>
              {/* ✅ Petit rappel que le navigateur gère l'autocomplétion */}
              {/*<div className="form-text text-muted mt-1" style={{ fontSize: '0.65rem' }}>
                <i className="bi bi-info-circle-fill me-1"></i>
                Votre navigateur peut sauvegarder votre email
              </div>*/}
            </div>

            {/* Mot de passe */}
            <div className="mb-3">
              <label className="form-label small fw-semibold" style={{ color: '#334155' }}>
                {/*<i className="bi bi-lock-fill me-1 text-muted"></i>*/}
                Mot de passe
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
                  type={showPassword ? "text" : "password"}
                  name="password"
                  className="form-control"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                  required
                  style={{ 
                    borderRadius: '0',
                    borderColor: '#e2e8f0',
                    borderRight: 'none'
                  }}
                />
                <button
                  type="button"
                  className="btn btn-outline-secondary"
                  onClick={togglePasswordVisibility}
                  style={{ 
                    borderRadius: '0 8px 8px 0',
                    borderColor: '#e2e8f0',
                    borderLeft: 'none',
                    width: '40px',
                    backgroundColor: '#f1f5f9'
                  }}
                  aria-label={showPassword ? "Masquer le mot de passe" : "Afficher le mot de passe"}
                >
                  <i className={`bi ${showPassword ? 'bi-eye-slash-fill' : 'bi-eye-fill'}`}></i>
                </button>
              </div>
            </div>

            {/* Options */}
            <div className="d-flex justify-content-between align-items-center mb-4">
              <div className="form-check">
                <input
                  type="checkbox"
                  className="form-check-input"
                  id="rememberMe"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                />
                <label className="form-check-label small" htmlFor="rememberMe" 
                       style={{ color: '#475569' }}>
                  Se souvenir de moi
                </label>
              </div>
              <Link to="/forgot-password" 
                    className="small text-decoration-none" 
                    style={{ color: '#1E3A8A', fontWeight: '500' }}>
                Mot de passe oublié ?
              </Link>
            </div>

            {/* Bouton connexion */}
            <button
              type="submit"
              className="btn w-100 py-2 fw-semibold shadow-sm"
              style={{ 
                borderRadius: '8px',
                fontSize: '1rem',
                background: 'linear-gradient(135deg, #1E3A8A, #172554)',
                border: 'none',
                color: 'white',
                transition: 'all 0.2s'
              }}
              disabled={loading}
              onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-1px)'}
              onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
            >
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
                <span 
                  className="spinner-border spinner-border-sm" 
                  role="status" 
                  aria-hidden="true"
                  style={{ display: loading ? 'inline-block' : 'none' }}
                ></span>
                <i 
                  className="bi bi-box-arrow-in-right" 
                  style={{ display: loading ? 'none' : 'inline-block' }}
                ></i>
                <span>{loading ? 'Connexion en cours...' : 'Se connecter'}</span>
              </span>
            </button>
          </form>

          {/* Lien inscription */}
          <div className="text-center mt-4 pt-3 border-top" style={{ borderColor: '#e2e8f0' }}>
            <p className="small mb-0" style={{ color: '#475569' }}>
              Vous n'avez pas de compte ?{' '}
              <Link to="/register" 
                    className="text-decoration-none fw-semibold" 
                    style={{ color: '#1E3A8A' }}>
                Créer un compte
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;