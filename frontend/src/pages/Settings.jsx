// src/pages/Settings.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Settings = () => {
  const navigate = useNavigate();
  
  const [settings, setSettings] = useState({
    emailNotifications: true,
    pushNotifications: true,
    soundEnabled: true,
    newOffers: true,
    newMessages: true,
    suggestions: true,
  });

  useEffect(() => {
    const saved = localStorage.getItem('notification_settings');
    if (saved) {
      setSettings(JSON.parse(saved));
    }
  }, []);

  const saveSettings = (newSettings) => {
    setSettings(newSettings);
    localStorage.setItem('notification_settings', JSON.stringify(newSettings));
  };

  const toggleSetting = (key) => {
    const newSettings = {
      ...settings,
      [key]: !settings[key]
    };
    saveSettings(newSettings);
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
                <i className="bi bi-gear-fill me-2"></i>
                Paramètres de notifications
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
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
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
              {/* Notifications par email */}
              <div className="d-flex justify-content-between align-items-center mb-4 pb-3 border-bottom">
                <div>
                  <h6 className="mb-1">
                    <i className="bi bi-envelope me-2 text-warning"></i>
                    Notifications par email
                  </h6>
                  <small className="text-muted">
                    Recevoir un email pour les nouvelles offres et messages
                  </small>
                </div>
                <div className="form-check form-switch mb-0">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    role="switch"
                    checked={settings.emailNotifications}
                    onChange={() => toggleSetting('emailNotifications')}
                    style={{ width: '3rem', height: '1.5rem', cursor: 'pointer' }}
                  />
                </div>
              </div>

              {/* Notifications push */}
              <div className="d-flex justify-content-between align-items-center mb-4 pb-3 border-bottom">
                <div>
                  <h6 className="mb-1">
                    <i className="bi bi-bell-fill me-2 text-warning"></i>
                    Notifications push
                  </h6>
                  <small className="text-muted">
                    Afficher des notifications dans le navigateur
                  </small>
                </div>
                <div className="form-check form-switch mb-0">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    role="switch"
                    checked={settings.pushNotifications}
                    onChange={() => toggleSetting('pushNotifications')}
                    style={{ width: '3rem', height: '1.5rem', cursor: 'pointer' }}
                  />
                </div>
              </div>

              {/* Son */}
              <div className="d-flex justify-content-between align-items-center mb-4 pb-3 border-bottom">
                <div>
                  <h6 className="mb-1">
                    <i className="bi bi-volume-up-fill me-2 text-warning"></i>
                    Sons
                  </h6>
                  <small className="text-muted">
                    Jouer un son lors de la réception de notifications
                  </small>
                </div>
                <div className="form-check form-switch mb-0">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    role="switch"
                    checked={settings.soundEnabled}
                    onChange={() => toggleSetting('soundEnabled')}
                    style={{ width: '3rem', height: '1.5rem', cursor: 'pointer' }}
                  />
                </div>
              </div>

              {/* Types de notifications */}
              <h6 className="mb-3 fw-bold">
                <i className="bi bi-funnel-fill me-2 text-warning"></i>
                Types de notifications
              </h6>
              
              <div className="mb-4">
                <div className="form-check mb-2">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    checked={settings.newOffers}
                    onChange={() => toggleSetting('newOffers')}
                    id="newOffers"
                  />
                  <label className="form-check-label" htmlFor="newOffers">
                    Nouvelles offres correspondant à mes critères
                  </label>
                </div>
                
                <div className="form-check mb-2">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    checked={settings.newMessages}
                    onChange={() => toggleSetting('newMessages')}
                    id="newMessages"
                  />
                  <label className="form-check-label" htmlFor="newMessages">
                    Nouveaux messages
                  </label>
                </div>
                
                <div className="form-check mb-2">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    checked={settings.suggestions}
                    onChange={() => toggleSetting('suggestions')}
                    id="suggestions"
                  />
                  <label className="form-check-label" htmlFor="suggestions">
                    Suggestions d'offres
                  </label>
                </div>
              </div>

              <div className="d-flex gap-2">
                <button 
                  className="btn btn-primary flex-grow-1"
                  style={{ background: 'linear-gradient(135deg, var(--primary) 0%, #D35400 100%)', border: 'none' }}
                  onClick={() => {
                    alert(' Paramètres sauvegardés !');
                    navigate(-1);
                  }}
                >
                  <i className="bi bi-check-lg me-2"></i>
                  Sauvegarder et retourner
                </button>
                
                <button 
                  className="btn btn-outline-secondary"
                  onClick={() => navigate(-1)}
                >
                  Annuler
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;