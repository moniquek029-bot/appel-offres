// src/pages/BureauDashboard.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import Notifications from './Notifications';
import Messagerie from '../components/Messagerie';

const BureauDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [user, setUser] = useState(null);
  const [bureauData, setBureauData] = useState(null);
  const [profileComplete, setProfileComplete] = useState(false);
  const [messagesNonLus, setMessagesNonLus] = useState(0);

  const fetchMessagesNonLus = useCallback(async () => {
    try {
      const res = await api.get('/messages/non-lus/');
      setMessagesNonLus(res.data.count || 0);
    } catch (err) {
      console.error('Erreur chargement messages:', err);
    }
  }, []);

  const loadData = useCallback(() => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try { setUser(JSON.parse(userStr)); } catch (e) { console.error(e); }
    }
    const savedProfile = localStorage.getItem('bureau_profile');
    if (savedProfile) {
      try {
        const data = JSON.parse(savedProfile);
        setBureauData(data);
        setProfileComplete(data.nom_structure && data.email_contact && data.telephone);
      } catch (e) { console.error(e); }
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    loadData();
    fetchMessagesNonLus();
    const handleProfileUpdate = () => loadData();
    window.addEventListener('profileUpdated', handleProfileUpdate);
    return () => window.removeEventListener('profileUpdated', handleProfileUpdate);
  }, [loadData, fetchMessagesNonLus]);

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (tab === 'messages') fetchMessagesNonLus();
  };

  if (loading) {
    return (
      <div className="container py-5 text-center">
        <div className="spinner-border" role="status" 
             style={{ color: 'var(--primary)', width: '3rem', height: '3rem' }}>
          <span className="visually-hidden">Chargement...</span>
        </div>
      </div>
    );
  }

  const nom = user?.nom || user?.first_name || user?.email?.split('@')[0] || 'Bureau';

  return (
    <div className="container py-4" style={{ backgroundColor: '#f8fafc', minHeight: '100vh' }}>
      
      {/* ========== EN-TÊTE ========== */}
      <div className="card border-0 shadow-sm mb-4" style={{ borderRadius: '16px' }}>
        <div className="card-body p-4">
          <div className="d-flex justify-content-between align-items-center flex-wrap gap-3">
            <div>
              <h1 className="display-6 fw-semibold mb-1" style={{ color: '#33339e' }}>
                {nom}
              </h1>
              <p className="text-muted small mb-0">Tableau de bord Bureau de travail</p>
            </div>
            <Link 
              to="/bureau/profile" 
              className="btn btn-primary"
              style={{ 
                borderRadius: '25px', 
                padding: '8px 24px',
                fontWeight: '500',
                background: 'linear-gradient(135deg, #8a681e, #172554)',
                border: 'none'
              }}
            >
              <i className="bi bi-pencil-square me-2"></i>
              Modifier mon profil
            </Link>
          </div>
        </div>
      </div>

      {/* ========== STATISTIQUES & ACTIONS ========== */}
      <div className="row g-3 mb-4">
        {/* Carte Messages */}
        <div className="col-md-4">
          <div className="card border-0 shadow-sm h-100 text-center" style={{ borderRadius: '16px' }}>
            <div className="card-body p-4">
              <div className="bg-info bg-opacity-10 rounded-circle d-inline-flex p-3 mb-3">
                <i className="bi bi-envelope-fill fs-3 text-info"></i>
              </div>
              <h2 className="display-4 fw-bold mb-0 text-info">{messagesNonLus}</h2>
              <p className="text-muted mb-3">Message(s) non lu(s)</p>
              <button 
                className="btn btn-outline-info rounded-pill px-4"
                onClick={() => handleTabChange('messages')}
              >
                <i className="bi bi-chat-dots me-1"></i>
                Consulter
              </button>
            </div>
          </div>
        </div>

        {/* Carte État du profil */}
        <div className="col-md-4">
          <div className="card border-0 shadow-sm h-100 text-center" style={{ borderRadius: '16px' }}>
            <div className="card-body p-4">
              <div className="bg-success bg-opacity-10 rounded-circle d-inline-flex p-3 mb-3">
                <i className="bi bi-person-check-fill fs-3 text-success"></i>
              </div>
              <h2 className="display-4 fw-bold mb-0 text-success">
                {profileComplete ? '✓' : '!'}
              </h2>
              <p className="text-muted mb-3">État du profil</p>
              {profileComplete ? (
                <span className="badge bg-success rounded-pill px-3 py-2">Complet</span>
              ) : (
                <Link to="/bureau/profile" className="btn btn-warning rounded-pill px-4">
                  À compléter
                </Link>
              )}
            </div>
          </div>
        </div>

        {/* Carte Informations structure */}
        <div className="col-md-4">
          <div className="card border-0 shadow-sm h-100" style={{ borderRadius: '16px' }}>
            <div className="card-body p-4">
              <div className="d-flex align-items-center mb-3">
                <div className="bg-primary bg-opacity-10 rounded-circle p-2 me-3">
                  <i className="bi bi-building fs-4 text-primary"></i>
                </div>
                <h5 className="mb-0 fw-bold">Ma structure</h5>
              </div>
              {bureauData?.nom_structure ? (
                <>
                  <p className="fw-semibold mb-1">{bureauData.nom_structure}</p>
                  <p className="text-muted small mb-2">{bureauData.domaine_activite}</p>
                  <p className="text-muted small mb-0">
                    <i className="bi bi-geo-alt me-1"></i> {bureauData.pays}
                  </p>
                </>
              ) : (
                <p className="text-muted small">Aucune information</p>
              )}
              <Link to="/bureau/profile" className="btn btn-sm btn-outline-primary mt-3 w-100 rounded-pill">
                <i className="bi bi-pencil me-1"></i> Modifier
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* ========== ONGLETS + BOUTON OFFRES (SUR LA MÊME LIGNE) ========== */}
      <div className="card border-0 shadow-sm mb-4" style={{ borderRadius: '16px' }}>
        <div className="card-body p-3">
          <div className="d-flex justify-content-between align-items-center flex-wrap gap-3">
            {/* Onglets */}
            <div className="d-flex gap-2 flex-wrap">
              {[
                { id: 'dashboard', label: 'Tableau de bord', icon: 'bi-speedometer2' },
                { id: 'notifications', label: 'Notifications', icon: 'bi-bell' },
                { id: 'messages', label: 'Messages', icon: 'bi-envelope', badge: messagesNonLus }
              ].map(tab => (
                <button
                  key={tab.id}
                  className={`btn btn-sm ${activeTab === tab.id ? 'btn-primary' : 'btn-outline-secondary'} px-3 py-1`}
                  onClick={() => handleTabChange(tab.id)}
                  style={{ 
                    borderRadius: '20px',
                    fontWeight: activeTab === tab.id ? '500' : '400',
                    fontSize: '0.85rem'
                  }}
                >
                  <i className={`${tab.icon} me-1`}></i>
                  {tab.label}
                  {tab.badge > 0 && (
                    <span className="badge bg-danger ms-1 rounded-pill" style={{ fontSize: '0.6rem' }}>{tab.badge}</span>
                  )}
                </button>
              ))}
            </div>
            
            {/* Bouton Voir les offres */}
            <Link to="/offres" 
                  className="btn btn-primary rounded-pill px-3 py-2"
                  style={{ 
                    fontWeight: '500',
                    fontSize: '0.85rem',
                    background: 'linear-gradient(135deg, #1E3A8A, #e2bb2e)',
                    border: 'none'
                  }}
            >
              <i className="bi bi-search me-2"></i>
              Voir les offres disponibles
            </Link>
          </div>
        </div>
      </div>

      {/* ========== CONTENU DES ONGLETS ========== */}
      {activeTab === 'notifications' && <Notifications />}
      {activeTab === 'messages' && <Messagerie />}
    </div>
  );
};

export default BureauDashboard;