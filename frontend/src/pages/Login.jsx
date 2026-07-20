// src/pages/Login.jsx
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError('❌ Email ou mot de passe incorrect');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div 
      className="min-vh-100 d-flex align-items-center justify-content-center"
      style={{
        background: 'linear-gradient(135deg, #f4f5f6 0%, #dbe3f0 100%)',
        padding: '20px'
      }}
    >
      <div 
        className="card shadow-lg"
        style={{
          maxWidth: '450px',
          width: '100%',
          borderRadius: '16px',
          overflow: 'hidden'
        }}
      >
        {/* En-tête avec logo */}
        <div 
          className="card-header text-white text-center py-4"
          style={{
            background: '#1E3A8A',
            borderBottom: 'none'
          }}
        >
          <div 
            className="d-inline-flex align-items-center justify-content-center mb-3"
            style={{
              width: '70px',
              height: '70px',
              background: 'linear-gradient(135deg, #1E3A8A, #172554) ',              
              borderRadius: '50%',
              boxShadow: '0 4px 12px rgba(245, 158, 11, 0.4)'
            }}
          >
            <span style={{ color: 'white', fontWeight: 'bold', fontSize: '2rem' }}>E</span>
          </div>
          <h2 className="mb-2 fw-bold">Connexion</h2>
          <p className="mb-0" style={{ fontSize: '0.9rem', opacity: 0.9 }}>
            Espace EXPERTISE-ID
          </p>
        </div>

        {/* Corps du formulaire */}
        <div className="card-body p-4 p-md-5">
          {error && (
            <div className="alert alert-danger alert-dismissible fade show" role="alert">
              {error}
              <button type="button" className="btn-close" onClick={() => setError('')}></button>
            </div>
          )}

          {/* ✅ autoComplete="off" sur le formulaire pour désactiver le remplissage global */}
          <form onSubmit={handleSubmit} autoComplete="off">
            
            {/* Email */}
            <div className="mb-4">
              <label htmlFor="email" className="form-label fw-semibold text-secondary">
                <i className="bi bi-envelope me-1"></i>
                Adresse e-mail
              </label>
              <div className="input-group">
                <span className="input-group-text bg-light border-0"></span>
                <input
                  type="email"
                  className="form-control form-control-lg border-0 bg-light"
                  id="email"
                  placeholder="votre@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  disabled={loading}
                  autoComplete="off" /* ✅ EMPÊCHE LE REMPLISSAGE AUTO À L'OUVERTURE */
                />
              </div>
            </div>

            {/* Mot de passe avec icône œil */}
            <div className="mb-4">
              <label htmlFor="password" className="form-label fw-semibold text-secondary">
                <i className="bi bi-lock me-1"></i>
                Mot de passe
              </label>
              <div className="input-group position-relative">
                <span className="input-group-text bg-light border-0"></span>
                <input
                  type={showPassword ? "text" : "password"}
                  className="form-control form-control-lg border-0 bg-light"
                  id="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  disabled={loading}
                  style={{ paddingRight: '50px' }}
                  autoComplete="new-password" /* ✅ ASTUCE : "new-password" empêche le navigateur de remplir un mot de passe existant */
                />
                {/* Bouton œil */}
                <button
                  type="button"
                  className="btn position-absolute end-0 top-50 translate-middle-y me-2"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{ 
                    zIndex: 10,
                    color: '#6c757d',
                    border: 'none',
                    background: 'transparent',
                    padding: '8px'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.color = '#1E3A8A';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.color = '#6c757d';
                  }}
                  title={showPassword ? "Masquer le mot de passe" : "Afficher le mot de passe"}
                >
                  <i 
                    className={`bi ${showPassword ? 'bi-eye-slash-fill' : 'bi-eye-fill'}`}
                    style={{ fontSize: '1.2rem' }}
                  ></i>
                </button>
              </div>
            </div>

            {/* Options */}
            <div className="d-flex justify-content-between align-items-center mb-4">
              <div className="form-check">
                <input
                  className="form-check-input"
                  type="checkbox"
                  id="remember"
                />
                <label className="form-check-label text-secondary small" htmlFor="remember">
                  Se souvenir de moi
                </label>
              </div>
              <Link to="/forgot-password" className="text-decoration-none small" style={{ color: '#1E3A8A' }}>
                Mot de passe oublié ?
              </Link>
            </div>

            {/* Bouton de connexion */}
            <button
              type="submit"
              className="btn btn-primary btn-lg w-100 mb-4"
              disabled={loading}
              style={{
                background: 'linear-gradient(135deg, #059669, #047857)', //
                border: 'none',
                padding: '12px',
                fontWeight: '600',
                boxShadow: '0 4px 12px rgba(30, 58, 138, 0.3)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'linear-gradient(135deg, #1E293B 0%, #1E3A8A 100%)';
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 6px 16px rgba(30, 58, 138, 0.4)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'linear-gradient(135deg, #1E3A8A 0%, #1E293B 100%)';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(30, 58, 138, 0.3)';
              }}
            >
              {loading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                  Connexion en cours...
                </>
              ) : (
                <>
                  <i className="bi bi-box-arrow-in-right me-2"></i>
                  Se connecter
                </>
              )}
            </button>
          </form>

          {/* Lien d'inscription */}
          <div className="text-center">
            <p className="text-secondary mb-0">
              Vous n'avez pas de compte ?{' '}
              <Link to="/register" className="text-decoration-none fw-semibold" style={{ color: '#1E3A8A' }}>
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