// src/components/Newsletter.jsx
import React, { useState } from 'react';
import api from '../services/api';

const Newsletter = ({ variant = 'footer' }) => {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState({ type: '', message: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus({ type: '', message: '' });

    try {
      await api.post('/newsletter/subscribe/', { email });
      setStatus({ type: 'success', message: ' Inscription réussie !' });
      setEmail('');
      setTimeout(() => setStatus({ type: '', message: '' }), 3000);
    } catch (err) {
      setStatus({ 
        type: 'error', 
        message: err.response?.status === 400 ? 'Cet email est déjà inscrit.' : 'Erreur lors de l\'inscription.' 
      });
      setTimeout(() => setStatus({ type: '', message: '' }), 3000);
    } finally {
      setLoading(false);
    }
  };

  // Style pour le footer
  if (variant === 'footer') {
    return (
      <form onSubmit={handleSubmit} className="mt-2">
        <div className="input-group input-group-sm">
          <input
            type="email"
            className="form-control bg-dark text-white border-secondary"
            placeholder="Votre adresse email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <button 
            type="submit" 
            className="btn btn-primary btn-sm"
            disabled={loading}
          >
            {loading ? '...' : 'S\'inscrire'}
          </button>
        </div>
        {status.message && (
          <div className={`small mt-2 ${status.type === 'success' ? 'text-success' : 'text-danger'}`}>
            {status.message}
          </div>
        )}
      </form>
    );
  }

  // Style pour modal (si besoin)
  return (
    <div className="card shadow-lg border-0 rounded-4">
      <div className="card-body p-4">
        <div className="text-center mb-3">
          <div className="bg-primary bg-opacity-10 rounded-circle d-inline-flex p-3 mb-2">
            <span className="display-6"></span>
          </div>
          <h3 className="h4 mb-0">Newsletter</h3>
        </div>
        
        <p className="text-muted small text-center">
          Recevez les nouvelles offres directement dans votre boîte email.
        </p>

        {status.message && (
          <div className={`alert alert-${status.type === 'success' ? 'success' : 'danger'} small text-center`}>
            {status.message}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <input
              type="email"
              className="form-control"
              placeholder="Votre adresse email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="btn btn-primary w-50" disabled={loading}>
            {loading ? 'Inscription...' : 'M\'inscrire'}
          </button>
        </form>

        <p className="text-muted small text-center mt-3 mb-0">
           Une fois par semaine • Désabonnement facile
        </p>
      </div>
    </div>
  );
};

export default Newsletter;