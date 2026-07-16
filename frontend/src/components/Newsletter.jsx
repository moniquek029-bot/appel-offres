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

  // Validation basique de l'email
    if (!email || !/\S+@\S+\.\S+/.test(email)) {
      setStatus({ 
        type: 'error', 
        message: '❌ Veuillez entrer une adresse email valide.' 
      });
      setLoading(false);
      setTimeout(() => setStatus({ type: '', message: '' }), 4000);
      return;
    }

    try {
      const response = await api.post('/newsletter/subscribe/', { email });
    
    // ✅ Utiliser le message du backend (plus informatif)
      const backendMessage = response.data?.message || '✅ Inscription réussie !';
      const emailSent = response.data?.email_sent;
    
    // ✅ Message différent selon si l'email a été envoyé ou non
      if (emailSent) {
        setStatus({ 
          type: 'success', 
          message: `${backendMessage} 📧 Vérifiez votre boîte de réception.` 
        });
      } else {
        setStatus({ 
          type: 'success', 
          message: `${backendMessage}` 
        });
      }
    
      setEmail('');
    
    // ✅ Délai plus long pour que l'utilisateur puisse lire
      setTimeout(() => setStatus({ type: '', message: '' }), 5000);
    
    } catch (err) {
      let errorMessage = '❌ Erreur lors de l\'inscription.';
    
    // Gestion des différents codes d'erreur
      if (err.response?.status === 400) {
      // Email déjà inscrit ou données invalides
        const backendError = err.response?.data?.error || err.response?.data?.email?.[0];
        errorMessage = backendError 
          ? `⚠️ ${backendError}` 
          : '⚠️ Cet email est déjà inscrit.';
      } else if (err.response?.status === 500) {
        errorMessage = '❌ Erreur serveur. Veuillez réessayer plus tard.';
      } else if (!err.response) {
        errorMessage = '❌ Impossible de contacter le serveur. Vérifiez votre connexion.';
      }
    
      setStatus({ 
        type: 'error', 
        message: errorMessage 
      });
      setTimeout(() => setStatus({ type: '', message: '' }), 5000);
    
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
            className="form-control"
            style={{
              backgroundColor: '#f2f4f9',  // Bleu corporate
              color: '#070000',             // Texte blanc
              border: '1px solid #230886', // Bordure dorée
            }}
            placeholder="Votre adresse email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <button 
            type="submit" 
            className="btn btn-sm"
            style={{
              background: ' #ad5f06',
              color: '#ffffff',
              border: 'none',
              fontWeight: '600',
            }}
            disabled={loading}
          >
            {loading ? '...' : 'S\'inscrire'}
          </button>
        </div>
        {status.message && (
          <div 
            className={`alert alert-${status.type === 'success' ? 'success' : 'danger'} mt-3 d-flex align-items-center`}
            role="alert"
            style={{ 
              animation: 'slideIn 0.3s ease-out',
              borderLeft: `4px solid ${status.type === 'success' ? '#10B981' : '#EF4444'}`
            }}
          >
            <i className={`bi ${status.type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-triangle-fill'} me-2`}></i>
            <span>{status.message}</span>
            <button 
              type="button" 
              className="btn-close ms-auto" 
              onClick={() => setStatus({ type: '', message: '' })}
              style={{ fontSize: '0.7rem' }}
            ></button>
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