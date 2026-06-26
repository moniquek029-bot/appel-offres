// src/pages/ForgotPassword.jsx
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    setError('');

    if (!email) {
      setError('❌ Veuillez entrer votre adresse email');
      setLoading(false);
      return;
    }

    try {
      // ✅ URL CORRECTE : /password-reset/ (pas /auth/password-reset/)
      const response = await api.post('/password-reset/', { email });
      
      setMessage(
        response.data?.message || 
        '✅ Si cet email est associé à un compte, vous recevrez un lien de réinitialisation.'
      );
      
      // Redirection après 3 secondes
      setTimeout(() => {
        navigate('/login');
      }, 3000);
      
    } catch (err) {
      console.error('❌ Erreur:', err);
      
      if (err.response?.status === 400) {
        setError(err.response?.data?.error || '❌ Email invalide');
      } else if (err.response?.status === 500) {
        setError('❌ Erreur serveur. Veuillez réessayer.');
      } else {
        setError('❌ Une erreur est survenue. Veuillez réessayer.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-md-6 col-lg-5">
          <div className="card shadow">
            <div className="card-body p-4">
              <div className="text-center mb-4">
                <div 
                  className="d-inline-flex align-items-center justify-content-center mb-3"
                  style={{
                    width: '60px',
                    height: '60px',
                    background: 'linear-gradient(135deg, #F59E0B, #1E3A8A)',
                    borderRadius: '50%'
                  }}
                >
                  <i className="bi bi-key-fill text-white" style={{ fontSize: '1.8rem' }}></i>
                </div>
                <h3 className="fw-bold">Mot de passe oublié ?</h3>
                <p className="text-muted">
                  Entrez votre email pour recevoir un lien de réinitialisation
                </p>
              </div>

              {message && (
                <div className="alert alert-success d-flex align-items-center" role="alert">
                  <i className="bi bi-check-circle-fill me-2"></i>
                  <div>{message}</div>
                </div>
              )}

              {error && (
                <div className="alert alert-danger d-flex align-items-center" role="alert">
                  <i className="bi bi-exclamation-triangle-fill me-2"></i>
                  <div>{error}</div>
                </div>
              )}

              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label htmlFor="email" className="form-label fw-semibold">
                    <i className="bi bi-envelope me-1"></i>
                    Adresse email
                  </label>
                  <input
                    type="email"
                    id="email"
                    className="form-control form-control-lg"
                    placeholder="votre@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    disabled={loading}
                  />
                </div>

                <button 
                  type="submit" 
                  className="btn btn-primary btn-lg w-100"
                  disabled={loading}
                  style={{
                    background: 'linear-gradient(135deg, var(--primary) 0%, #D35400 100%)',
                    border: 'none'
                  }}
                >
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                      Envoi en cours...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-send me-2"></i>
                      Envoyer le lien
                    </>
                  )}
                </button>
              </form>

              <div className="text-center mt-4">
                <Link to="/login" className="text-decoration-none">
                  <i className="bi bi-arrow-left me-1"></i>
                  Retour à la connexion
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;