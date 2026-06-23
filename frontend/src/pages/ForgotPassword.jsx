// src/pages/ForgotPassword.jsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [emailSent, setEmailSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!email) {
      setMessage({ type: 'danger', text: 'Veuillez entrer votre email' });
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await api.post('/auth/password-reset/', { email });
      
      setMessage({
        type: 'success',
        text: response.data.message
      });
      setEmailSent(true);
      
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Erreur lors de l\'envoi de l\'email';
      setMessage({ type: 'danger', text: errorMsg });
    } finally {
      setLoading(false);
    }
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
              <i className="bi bi-key-fill text-white" style={{ fontSize: '1.5rem' }}></i>
            </div>
          </div>
          <h2 className="h3 mb-1 fw-bold">Mot de passe oublié ?</h2>
          <p className="mb-0 opacity-75" style={{ fontSize: '0.9rem' }}>
            Récupérez l'accès à votre compte
          </p>
        </div>

        <div className="card-body p-4 p-lg-5">
          
          {/* Messages */}
          {message.text && (
            <div className={`alert alert-${message.type} py-2 small d-flex align-items-start`} 
                 role="alert" 
                 style={{ borderRadius: '8px', border: 'none' }}>
              <i className={`bi ${message.type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-triangle-fill'} me-2 mt-1`}></i>
              <div>{message.text}</div>
            </div>
          )}

          {!emailSent ? (
            <>
              <p className="text-center small mb-4" style={{ color: '#475569' }}>
                Entrez votre adresse email et nous vous enverrons un lien pour réinitialiser votre mot de passe.
              </p>

              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label small fw-semibold" style={{ color: '#334155' }}>
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
                      className="form-control"
                      placeholder="exemple@email.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      disabled={loading}
                      autoFocus
                      style={{ 
                        borderRadius: '0 8px 8px 0',
                        borderColor: '#e2e8f0'
                      }}
                    />
                  </div>
                </div>
                
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
                >
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2"></span>
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
            </>
          ) : (
            <div className="text-center py-3">
              <div className="d-flex justify-content-center mb-3">
                <div 
                  className="d-flex align-items-center justify-content-center rounded-circle"
                  style={{ 
                    width: '70px', 
                    height: '70px', 
                    background: '#d1e7dd'
                  }}
                >
                  <i className="bi bi-envelope-check-fill text-success" style={{ fontSize: '2rem' }}></i>
                </div>
              </div>
              <h5 className="fw-bold mb-2">Email envoyé !</h5>
              <p className="small text-muted mb-4">
                Consultez votre boîte de réception et cliquez sur le lien reçu.
              </p>
              <div className="alert alert-warning small py-2" style={{ borderRadius: '8px' }}>
                <i className="bi bi-info-circle me-1"></i>
                Pensez à vérifier vos spams si vous ne trouvez pas l'email.
              </div>
            </div>
          )}

          {/* Lien retour */}
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

export default ForgotPassword;