// src/pages/BureauDashboard.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import Notifications from '../components/Notifications';
import Messagerie from '../components/Messagerie';

const BureauDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [user, setUser] = useState(null);
  const [bureauData, setBureauData] = useState(null);
  const [profileComplete, setProfileComplete] = useState(false);
  const [messagesNonLus, setMessagesNonLus] = useState(0);
  const [refreshKey, setRefreshKey] = useState(0);

  // Récupérer les messages non lus depuis l'API
  const fetchMessagesNonLus = useCallback(async () => {
    try {
      const res = await api.get('/messages/non-lus/');
      setMessagesNonLus(res.data.count || 0);
    } catch (err) {
      console.error('Erreur chargement messages non lus:', err);
    }
  }, []);

  // Charger les données depuis localStorage et API
  const loadData = useCallback(() => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        const userData = JSON.parse(userStr);
        setUser(userData);
      } catch (e) {
        console.error(e);
      }
    }
    
    const savedProfile = localStorage.getItem('bureau_profile');
    if (savedProfile) {
      try {
        const data = JSON.parse(savedProfile);
        setBureauData(data);
        const isComplete = data.nom_structure && data.email_contact && data.telephone;
        setProfileComplete(isComplete);
      } catch (e) {
        console.error(e);
      }
    }
    
    setLoading(false);
  }, []);

  useEffect(() => {
    loadData();
    fetchMessagesNonLus();
    
    const handleProfileUpdate = () => {
      loadData();
    };
    
    window.addEventListener('profileUpdated', handleProfileUpdate);
    
    return () => {
      window.removeEventListener('profileUpdated', handleProfileUpdate);
    };
  }, [loadData, fetchMessagesNonLus]);

  // Rafraîchir les messages non lus quand on change d'onglet
  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (tab === 'messages') {
      fetchMessagesNonLus();
      setRefreshKey(prev => prev + 1);
    }
  };

  if (loading) {
    return (
      <div className="container py-5 text-center">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Chargement...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container py-4">
      
      {/* En-tête */}
      <div className="row mb-3">
        <div className="col-12">
          <h2 className="mb-0 fs-4">👋 Bonjour, {user?.nom || user?.first_name || 'Bureau'}</h2>
          <p className="text-muted small">Tableau de bord Bureau d'études</p>
        </div>
      </div>

      {/* Onglets horizontaux */}
      <div className="mb-4">
        <div className="d-flex gap-2 border-bottom pb-2">
          <button 
            className={`btn btn-sm ${activeTab === 'dashboard' ? 'btn-primary' : 'btn-outline-secondary'}`}
            onClick={() => handleTabChange('dashboard')}
            style={{ borderRadius: '20px', padding: '5px 15px', fontSize: '0.75rem' }}
          >
            📊 Dashboard
          </button>
          <button 
            className={`btn btn-sm ${activeTab === 'notifications' ? 'btn-primary' : 'btn-outline-secondary'}`}
            onClick={() => handleTabChange('notifications')}
            style={{ borderRadius: '20px', padding: '5px 15px', fontSize: '0.75rem' }}
          >
            🔔 Notifications
          </button>
          <button 
            className={`btn btn-sm position-relative ${activeTab === 'messages' ? 'btn-primary' : 'btn-outline-secondary'}`}
            onClick={() => handleTabChange('messages')}
            style={{ borderRadius: '20px', padding: '5px 15px', fontSize: '0.75rem' }}
          >
            💬 Messages
            {messagesNonLus > 0 && (
              <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                {messagesNonLus}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Dashboard */}
      {activeTab === 'dashboard' && (
        <>
          {/* Alerte profil */}
          <div className="alert alert-light border d-flex align-items-center justify-content-between py-2 px-3 mb-4">
            <div className="d-flex align-items-center gap-2">
              <strong className="small">📋 État du profil :</strong>
              <span className={`badge ${profileComplete ? 'bg-success' : 'bg-warning text-dark'} px-2 py-1`} style={{ fontSize: '0.7rem' }}>
                {profileComplete ? '✅ Profil complet' : '⚠️ À compléter'}
              </span>
            </div>
            {!profileComplete && (
              <Link 
                to="/bureau/profile" 
                className="btn btn-sm btn-primary"
                style={{ fontSize: '0.7rem', padding: '4px 12px' }}
              >
                + Compléter mon profil
              </Link>
            )}
          </div>

          {/* Statistiques */}
          <div className="row g-3 mb-4">
            <div className="col-6">
              <div className="card border-0 shadow-sm text-center">
                <div className="card-body py-3">
                  <div className="fs-2 mb-1">📨</div>
                  <h3 className="h5 mb-0">{messagesNonLus}</h3>
                  <p className="text-muted small mb-0">Message(s) non lu(s)</p>
                  <button className="btn btn-sm btn-outline-primary mt-2" onClick={() => handleTabChange('messages')}>
                    Consulter
                  </button>
                </div>
              </div>
            </div>
            <div className="col-6">
              <div className="card border-0 shadow-sm text-center">
                <div className="card-body py-3">
                  <div className="fs-2 mb-1">📋</div>
                  <h3 className="h5 mb-0">{profileComplete ? '✓' : '!'}</h3>
                  <p className="text-muted small mb-0">État du profil</p>
                  {!profileComplete && (
                    <Link to="/bureau/profile" className="btn btn-sm btn-warning mt-2">
                      Compléter
                    </Link>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Informations de la structure */}
          <div className="card border-0 shadow-sm">
            <div className="card-header bg-white py-2">
              <h5 className="mb-0 fs-6">📌 Informations de votre structure</h5>
            </div>
            <div className="card-body">
              {bureauData?.nom_structure ? (
                <div className="row g-3">
                  <div className="col-md-6">
                    <p className="mb-1 small text-muted">🏢 Structure</p>
                    <p className="mb-0 fw-semibold">{bureauData.nom_structure}</p>
                  </div>
                  <div className="col-md-6">
                    <p className="mb-1 small text-muted">📧 Email de contact</p>
                    <p className="mb-0">{bureauData.email_contact}</p>
                  </div>
                  <div className="col-md-6">
                    <p className="mb-1 small text-muted">📞 Téléphone</p>
                    <p className="mb-0">{bureauData.telephone}</p>
                  </div>
                  <div className="col-md-6">
                    <p className="mb-1 small text-muted">🌍 Pays</p>
                    <p className="mb-0">{bureauData.pays}</p>
                  </div>
                  <div className="col-12">
                    <p className="mb-1 small text-muted">📋 Domaine d'activité</p>
                    <p className="mb-0">{bureauData.domaine_activite}</p>
                  </div>
                  {bureauData.adresse && (
                    <div className="col-12">
                      <p className="mb-1 small text-muted">📍 Adresse</p>
                      <p className="mb-0">{bureauData.adresse}</p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-4">
                  <p className="text-muted mb-0">Aucune information enregistrée.</p>
                  <Link to="/bureau/profile" className="btn btn-primary btn-sm mt-3">
                    + Compléter mon profil
                  </Link>
                </div>
              )}
            </div>
          </div>

          {/* Lien vers les offres */}
          <div className="mt-4">
            <Link to="/offres" className="btn btn-outline-primary btn-sm">
              🔍 Voir les offres disponibles
            </Link>
          </div>
        </>
      )}

      {/* Onglet Notifications */}
      {activeTab === 'notifications' && <Notifications />}
      
      {/* Onglet Messages - avec key pour forcer le rafraîchissement */}
      {activeTab === 'messages' && <Messagerie key={refreshKey} />}
    </div>
  );
};

export default BureauDashboard;