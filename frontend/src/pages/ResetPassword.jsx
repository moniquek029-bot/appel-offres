import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import api from '../services/api';

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const token = searchParams.get('token');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (password !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }

    if (password.length < 8) {
      setError('Le mot de passe doit contenir au moins 8 caractères');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await api.post('/password-reset/confirm/', {
        token: token,
        new_password: password
      });
      
      setMessage(' Mot de passe réinitialisé avec succès !');
      setTimeout(() => navigate('/login'), 3000);
    } catch (err) {
      setError(' Erreur: ' + (err.response?.data?.error || 'Token invalide ou expiré'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card shadow">
            <div className="card-body p-4">
              <h3 className="text-center mb-4">Réinitialiser le mot de passe</h3>
              
              {message && (
                <div className="alert alert-success">{message}</div>
              )}
              
              {error && (
                <div className="alert alert-danger">{error}</div>
              )}

              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label">Nouveau mot de passe</label>
                  <input
                    type="password"
                    className="form-control"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label">Confirmer le mot de passe</label>
                  <input
                    type="password"
                    className="form-control"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                  />
                </div>

                <button 
                  type="submit" 
                  className="btn btn-primary w-100"
                  disabled={loading}
                >
                  {loading ? 'Traitement...' : 'Réinitialiser'}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResetPassword;