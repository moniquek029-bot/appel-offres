// src/pages/ResetPassword.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import api from '../services/api';

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [tokenValid, setTokenValid] = useState(false);
  const [checkingToken, setCheckingToken] = useState(true);
  const navigate = useNavigate();

  // ✅ Récupérer le token depuis l'URL (?token=xyz)
  const token = searchParams.get('token');

  // ✅ Vérifier la validité du token au chargement
  useEffect(() => {
    const checkToken = async () => {
      if (!token) {
        setError('❌ Lien invalide : aucun token trouvé.');
        setCheckingToken(false);
        return;
      }

      try {
        // Appel à l'endpoint de validation du token
        await api.get(`/password-reset/validate/${token}/`);
        setTokenValid(true); // Token valide
      } catch (err) {
        console.error('Token invalide:', err);
        setError('❌ Ce lien a expiré ou a déjà été utilisé. Veuillez faire une nouvelle demande.');
      } finally {
        setCheckingToken(false);
      }
    };

    checkToken();
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');

    if (password.length < 8) {
      setError('❌ Le mot de passe doit contenir au moins 8 caractères');
      return;
    }

    if (password !== confirmPassword) {
      setError('❌ Les mots de passe ne correspondent pas');
      return;
    }

    setLoading(true);

    try {
      await api.post('/password-reset/confirm/', {
        token: token,
        new_password: password
      });
      
      setMessage('✅ Mot de passe réinitialisé avec succès ! Vous allez être redirigé...');
      
      setTimeout(() => {
        navigate('/login');
      }, 3000);
      
    } catch (err) {
      console.error('Erreur:', err);
      setError(err.response?.data?.error || '❌ Erreur lors de la réinitialisation');
    } finally {
      setLoading(false);
    }
  };

  // ✅ Écran de chargement pendant la vérification du token
  if (checkingToken) {
    return (
      <div className="container py-5 text-center">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Vérification...</span>
        </div>
        <p className="mt-3 text-muted">Vérification du lien en cours...</p>
      </div>
    );
  }

  // ✅ Écran d'erreur si le token est invalide
  if (!tokenValid) {
    return (
      <div className="container py-5">
        <div className="row justify-content-center">
          <div className="col-md-6">
            <div className="card shadow">
              <div className="card-body p-4 text-center">
                <i className="bi bi-exclamation-triangle-fill text-danger" style={{ fontSize: '3rem' }}></i>
                <h4 className="mt-3">Lien invalide</h4>
                <p className="text-muted">{error}</p>
                <button 
                  className="btn btn-primary"
                  onClick={() => navigate('/forgot-password')}
                >
                  <i className="bi bi-envelope me-1"></i>
                  Demander un nouveau lien
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ✅ Formulaire de réinitialisation
  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-md-6 col-lg-5">
          <div className="card shadow border-0" style={{ borderRadius: '16px' }}>
            <div className="card-body p-4 p-md-5">
              <div className="text-center mb-4">
                <div 
                  className="d-inline-flex align-items-center justify-content-center mb-3"
                  style={{
                    width: '70px', 
                    height: '70px',
                    background: 'linear-gradient(135deg, #1E3A8A, #F59E0B)',
                    borderRadius: '50%'
                  }}
                >
                  <i className="bi bi-shield-lock-fill text-white" style={{ fontSize: '2rem' }}></i>
                </div>
                <h3 className="fw-bold">Nouveau mot de passe</h3>
                <p className="text-muted">
                  Définissez votre nouveau mot de passe sécurisé.
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

              <form onSubmit={handleSubmit} autoComplete="off">
                <div className="mb-3">
                  <label className="form-label fw-semibold">
                    <i className="bi bi-lock me-1"></i>
                    Nouveau mot de passe
                  </label>
                  <div className="position-relative">
                    <input
                      type={showPassword ? "text" : "password"}
                      className="form-control form-control-lg"
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      disabled={loading}
                      autoComplete="new-password"
                      minLength="8"
                    />
                    <button
                      type="button"
                      className="btn position-absolute end-0 top-50 translate-middle-y me-2 text-secondary"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      <i className={`bi ${showPassword ? 'bi-eye-slash-fill' : 'bi-eye-fill'}`}></i>
                    </button>
                  </div>
                  <small className="text-muted">Minimum 8 caractères</small>
                </div>

                <div className="mb-4">
                  <label className="form-label fw-semibold">
                    <i className="bi bi-lock-fill me-1"></i>
                    Confirmer le mot de passe
                  </label>
                  <input
                    type="password"
                    className="form-control form-control-lg"
                    placeholder="••••••••"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    disabled={loading}
                    autoComplete="new-password"
                  />
                </div>

                <button 
                  type="submit" 
                  className="btn btn-primary btn-lg w-100"
                  disabled={loading}
                  style={{
                    background: 'linear-gradient(135deg, #1E3A8A 0%, #1E293B 100%)',
                    border: 'none'
                  }}
                >
                  {loading ? (
                    <><span className="spinner-border spinner-border-sm me-2"></span>Traitement...</>
                  ) : (
                    <><i className="bi bi-check-lg me-2"></i>Réinitialiser le mot de passe</>
                  )}
                </button>
              </form>

              <div className="text-center mt-4">
                <button 
                  className="btn btn-link text-decoration-none"
                  onClick={() => navigate('/login')}
                >
                  <i className="bi bi-arrow-left me-1"></i>
                  Retour à la connexion
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResetPassword;