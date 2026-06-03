// src/pages/ExpertDashboard.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import Notifications from '../components/Notifications';
import Messagerie from '../components/Messagerie';
import ExpertCriteres from './ExpertCriteres';

const ExpertDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [messagesNonLus, setMessagesNonLus] = useState(0);
  const [refreshKey, setRefreshKey] = useState(0);

  // Récupérer les messages non lus
  const fetchMessagesNonLus = useCallback(async () => {
    try {
      const messagesRes = await api.get('/messages/non-lus/');
      setMessagesNonLus(messagesRes.data.count || 0);
    } catch (err) {
      console.error('Erreur chargement messages non lus:', err);
    }
  }, []);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const res = await api.get('/expert/dashboard/');
        setDashboardData(res.data);
        await fetchMessagesNonLus();
      } catch (err) {
        console.error('Erreur chargement dashboard:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, [fetchMessagesNonLus]);

  // Rafraîchir les messages non lus quand on revient sur l'onglet messages
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

  const { user, profile, stats, recent_matching_offres, next_steps } = dashboardData || {};

  return (
    <div className="container py-4">
      
      {/* Onglets horizontaux */}
      <div className="mb-4">
        <div className="d-flex justify-content-center gap-2" style={{ flexWrap:'nowrap', overflowX: 'auto'}}>
          
          <button 
            className={`btn px-3 py-2 rounded-pill ${
              activeTab === 'dashboard' 
                ? 'btn-primary shadow-sm' 
                : 'btn-outline-secondary'
            }`}
            onClick={() => handleTabChange('dashboard')}
            style={{ whiteSpace: 'nowrap', fontSize: '0.85rem' }}
          >
            📊 Dashboard
          </button>
          
          <button 
            className={`btn px-3 py-2 rounded-pill ${
              activeTab === 'criteres' 
                ? 'btn-primary shadow-sm' 
                : 'btn-outline-secondary'
            }`}
            onClick={() => handleTabChange('criteres')}
            style={{ whiteSpace: 'nowrap', fontSize: '0.85rem' }}
          >
            🔍 Critères
          </button>
          
          <button 
            className={`btn px-3 py-2 rounded-pill ${
              activeTab === 'notifications' 
                ? 'btn-primary shadow-sm' 
                : 'btn-outline-secondary'
            }`}
            onClick={() => handleTabChange('notifications')}
            style={{ whiteSpace: 'nowrap', fontSize: '0.85rem' }}
          >
            🔔 Notifications
            {profile?.notifications_non_lues > 0 && (
              <span className="badge bg-danger ms-1">{profile.notifications_non_lues}</span>
            )}
          </button>
          
          <button 
            className={`btn px-3 py-2 rounded-pill position-relative ${
              activeTab === 'messages' 
                ? 'btn-primary shadow-sm' 
                : 'btn-outline-secondary'
            }`}
            onClick={() => handleTabChange('messages')}
            style={{ whiteSpace: 'nowrap', fontSize: '0.85rem' }}
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
          <div className="row mb-4">
            <div className="col-12">
              <h2 className="mb-1 fs-4">Bonjour, {user?.nom || user?.first_name || 'Expert'} 👋</h2>
              <p className="text-muted small">Tableau de bord Expert</p>
              
              <div className="alert alert-light border d-flex align-items-center justify-content-between mt-2 py-2">
                <div>
                  <strong className="small">Profil :</strong>{' '}
                  <span className={`badge ${profile?.cv_fichier ? 'bg-success' : 'bg-warning text-dark'} ms-1`}>
                    {profile?.cv_fichier ? '✅ Complet' : '⚠️ CV manquant'}
                  </span>
                </div>
                {!profile?.cv_fichier && (
                  <Link to="/expert/profile" className="btn btn-xs btn-primary">
                    + CV
                  </Link>
                )}
              </div>
            </div>
          </div>

          {/* Cartes statistiques */}
          <div className="row g-2 mb-4">
            <div className="col-4">
              <div className="card border-0 shadow-sm h-100 stat-card">
                <div className="card-body text-center p-2">
                  <div className="fs-1 text-primary mb-1">🔍</div>
                  <h3 className="h4 mb-1 fw-bold">{stats?.criteres_count || 0}</h3>
                  <p className="text-muted small mb-1">Critères</p>
                  <button className="btn btn-xs btn-outline-primary w-100" onClick={() => handleTabChange('criteres')}>
                    Gérer
                  </button>
                </div>
              </div>
            </div>
            
            <div className="col-4">
              <div className="card border-0 shadow-sm h-100 stat-card">
                <div className="card-body text-center p-2">
                  <div className="fs-1 text-success mb-1">📄</div>
                  <h3 className="h4 mb-1 fw-bold">{stats?.matching_offres_count || 0}</h3>
                  <p className="text-muted small mb-1">Offres</p>
                </div>
              </div>
            </div>
            
            <div className="col-4">
              <div className="card border-0 shadow-sm h-100 stat-card">
                <div className="card-body text-center p-2">
                  <div className="fs-1 text-info mb-1">📨</div>
                  <h3 className="h4 mb-1 fw-bold">{messagesNonLus}</h3>
                  <p className="text-muted small mb-1">Messages</p>
                  <button className="btn btn-xs btn-outline-info w-100" onClick={() => handleTabChange('messages')}>
                    Voir
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Actions recommandées */}
          {next_steps && next_steps.length > 0 && (
            <div className="row mb-4">
              <div className="col-12">
                <div className="card border-0 shadow-sm">
                  <div className="card-header bg-light py-2">
                    <h5 className="mb-0 fs-6">🎯 Actions</h5>
                  </div>
                  <div className="card-body py-2">
                    {next_steps.map((step, index) => (
                      <div key={index} className={`alert alert-${step.priority === 'high' ? 'danger' : 'info'} d-flex justify-content-between align-items-center mb-1 py-1 small`}>
                        <span>{step.message}</span>
                        <Link to={step.url} className="btn btn-xs btn-outline-dark">
                          {step.action === 'upload_cv' && 'CV'}
                          {step.action === 'add_criteria' && 'Ajouter'}
                          {step.action === 'browse_offres' && 'Voir'}
                        </Link>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Offres correspondantes */}
          <div className="row">
            <div className="col-12">
              <div className="d-flex justify-content-between align-items-center mb-2">
                <h4 className="mb-0 fs-6">📋 Offres correspondantes</h4>
                <Link to="/offres" className="btn btn-outline-primary btn-xs">
                  Voir tout →
                </Link>
              </div>
              
              {recent_matching_offres && recent_matching_offres.length > 0 ? (
                <div className="row g-2">
                  {recent_matching_offres.slice(0, 6).map((offre) => (
                    <div className="col-md-6 col-lg-4" key={offre.id}>
                      <div className="card h-100 border-0 shadow-sm">
                        <div className="card-body p-2">
                          <h6 className="card-title text-primary mb-1 small text-truncate">{offre.titre}</h6>
                          <p className="text-muted small mb-1">{offre.organisme}</p>
                          <p className="card-text small text-secondary mb-2 text-truncate-2">
                            {offre.description}
                          </p>
                          <div className="d-flex justify-content-between align-items-center">
                            <small className="text-muted">
                              {new Date(offre.date_cloture).toLocaleDateString('fr-FR')}
                            </small>
                            <Link to={`/offres/${offre.id}`} className="btn btn-xs btn-primary">
                              Voir
                            </Link>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="alert alert-info small py-2">
                  Aucune offre ne correspond.
                  <button className="btn btn-link p-0 ms-1" onClick={() => handleTabChange('criteres')}>
                    Ajouter des critères
                  </button>
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {activeTab === 'criteres' && <ExpertCriteres />}
      {activeTab === 'notifications' && <Notifications />}
      {activeTab === 'messages' && <Messagerie key={refreshKey} />}
    </div>
  );
};

export default ExpertDashboard;