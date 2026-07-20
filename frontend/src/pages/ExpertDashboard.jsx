// src/pages/ExpertDashboard.jsx - VERSION MODIFIÉE AVEC SUGGESTIONS
import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import Notifications from './Notifications';
import Messagerie from '../components/Messagerie';
import ExpertCriteres from './ExpertCriteres';

const ExpertDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [messagesNonLus, setMessagesNonLus] = useState(0);
  // ✅ NOUVEAU : État pour les suggestions
  const [suggestionsStats, setSuggestionsStats] = useState(null);

  const fetchMessagesNonLus = useCallback(async () => {
    try {
      const res = await api.get('/messages/non-lus/');
      setMessagesNonLus(res.data.count || 0);
    } catch (err) {
      console.error('Erreur chargement messages:', err);
    }
  }, []);

  // ✅ NOUVEAU : Récupérer les statistiques des suggestions
  const fetchSuggestionsStats = useCallback(async () => {
    try {
      const res = await api.get('/expert/suggestions/');
      setSuggestionsStats(res.data.stats || null);
    } catch (err) {
      console.error('Erreur chargement suggestions:', err);
      setSuggestionsStats(null);
    }
  }, []);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const res = await api.get('/expert/dashboard/');
        setDashboardData(res.data);
        await fetchMessagesNonLus();
        await fetchSuggestionsStats(); // ✅ Charger les suggestions
      } catch (err) {
        console.error('Erreur chargement dashboard:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, [fetchMessagesNonLus, fetchSuggestionsStats]);

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (tab === 'messages') fetchMessagesNonLus();
    if (tab === 'suggestions') fetchSuggestionsStats(); // ✅ Recharger les suggestions
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

  const { user, profile, stats, recent_matching_offres } = dashboardData || {};
  const hasCV = !!profile?.cv_fichier;
  const nom = profile?.full_name || user?.email?.split('@')[0] || 'Expert';
  const competences = profile?.competences ? profile.competences.split(',').slice(0, 3) : [];
  
  // ✅ Calculer le nombre de suggestions en attente
  const suggestionsEnAttente = suggestionsStats?.en_attente || 0;

  return (
    <div className="container py-4" style={{ backgroundColor: 'var(--gray-50)', minHeight: '100vh' }}>
      
      {/* ========== EN-TÊTE AVEC PROFIL INTÉGRÉ ========== */}
      <div className="d-flex justify-content-between align-items-center flex-wrap mb-3">
        {/* Partie gauche - Bonjour + Profil */}
        <div>
          <h1 className="h2 mb-1 fw-bold" style={{ color: '#1c1c9e' }}>
            Expert, <span className="text-primary">{nom}</span>
          </h1>
          
          {/* État du profil */}
          <div className="d-flex align-items-center flex-wrap gap-2 mt-2">
            <div className="d-flex align-items-center">
              <i className="bi bi-person-check-fill text-primary me-1" style={{ fontSize: '0.8rem' }}></i>
              <span className="small fw-semibold me-1" style={{ color: '#1c1c9e' }}>Profil :</span>
              <span className={`badge ${hasCV ? 'bg-success' : 'bg-warning text-dark'} px-2 py-1 rounded-pill`}
                    style={{ fontWeight: '500', fontSize: '0.7rem' }}>
                {hasCV ? 'Complet' : 'CV manquant'}
              </span>
            </div>
            {competences.length > 0 && (
              <div className="d-flex align-items-center flex-wrap gap-1">
                <i className="bi bi-tag-fill text-secondary me-1" style={{ fontSize: '0.7rem' }}></i>
                {competences.map((c, i) => (
                  <span key={i} className="badge bg-light text-dark border px-2 py-1 rounded-pill"
                        style={{ fontWeight: '400', fontSize: '0.65rem' }}>
                    {c.trim()}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
        
        {/* Partie droite - Boutons alignés à droite */}
        <div className="d-flex gap-2 mt-3 mt-sm-0">
          {/*{!hasCV && (
            <Link 
              to="/expert/profile" 
              className="btn btn-primary"
              style={{ 
                borderRadius: '25px', 
                padding: '8px 20px',
                fontWeight: '500',
                fontSize: '0.85rem',
                background: '#1c1c9e',
                border: 'none'
              }}
            >
              <i className="bi bi-cloud-upload me-2"></i>
              Ajouter mon CV
            </Link>
          )}*/}
          <Link 
            to="/expert/profile" 
            className="btn text-white fw-semibold rounded-pill px-3"
            style={{ 
              background: '#F59E0B', // 🟡 OR
              border: 'none',
              transition: 'background 0.2s ease'
            }}
            onMouseEnter={(e) => e.currentTarget.style.background = '#D97706'}
            onMouseLeave={(e) => e.currentTarget.style.background = '#F59E0B'}
          >
            <i className="bi bi-pencil-square me-2"></i>
            Modifier mon profil
        </Link>
        </div>
      </div>

      {/* ========== CARTES STATISTIQUES COMPACTES ========== */}
      <div className="row g-2 mb-4">
        {/* Carte Critères */}
        <div className="col-6 col-md-3">
          <div className="card border-0 shadow-sm h-100 text-center" 
               style={{ borderRadius: '12px', transition: 'transform 0.2s' }}>
            <div className="card-body p-2">
              <div className="bg-primary bg-opacity-10 rounded-circle d-inline-flex p-1 mb-1">
                <i className="bi bi-funnel-fill text-primary" style={{ fontSize: '1.2rem' }}></i>
              </div>
              <h3 className="h4 mb-0 fw-bold text-primary">{stats?.criteres_count || 0}</h3>
              <p className="text-muted mb-1" style={{ fontSize: '0.65rem' }}>
                <i className="bi bi-info-circle me-1"></i>
                Critères
              </p>
              <button 
                className="btn btn-xs btn-outline-primary w-100 rounded-pill"
                onClick={() => handleTabChange('criteres')}
                style={{ fontSize: '0.6rem', padding: '3px 6px' }}
              >
                <i className="bi bi-eye me-1"></i>
                Gérer
              </button>
            </div>
          </div>
        </div>
        
        {/* Carte Offres */}
        <div className="col-6 col-md-3">
          <div className="card border-0 shadow-sm h-100 text-center" 
               style={{ borderRadius: '12px', transition: 'transform 0.2s' }}>
            <div className="card-body p-2">
              <div className="bg-success bg-opacity-10 rounded-circle d-inline-flex p-1 mb-1">
                <i className="bi bi-file-text-fill text-success" style={{ fontSize: '1.2rem' }}></i>
              </div>
              <h3 className="h4 mb-0 fw-bold text-success">{stats?.matching_offres_count || 0}</h3>
              <p className="text-muted mb-1" style={{ fontSize: '0.65rem' }}>
                <i className="bi bi-info-circle me-1"></i>
                Offres
              </p>
              <Link to="/offres" 
                    className="btn btn-xs btn-outline-success w-100 rounded-pill"
                    style={{ fontSize: '0.6rem', padding: '3px 6px' }}>
                <i className="bi bi-eye me-1"></i>
                Voir
              </Link>
            </div>
          </div>
        </div>
        
        {/* Carte Messages */}
        <div className="col-6 col-md-3">
          <div className="card border-0 shadow-sm h-100 text-center" 
               style={{ borderRadius: '12px', transition: 'transform 0.2s' }}>
            <div className="card-body p-2">
              <div className="bg-info bg-opacity-10 rounded-circle d-inline-flex p-1 mb-1">
                <i className="bi bi-chat-dots-fill text-info" style={{ fontSize: '1.2rem' }}></i>
              </div>
              <h3 className="h4 mb-0 fw-bold text-info">{messagesNonLus}</h3>
              <p className="text-muted mb-1" style={{ fontSize: '0.65rem' }}>
                <i className="bi bi-info-circle me-1"></i>
                Messages
              </p>
              <button 
                className="btn btn-xs btn-outline-info w-100 rounded-pill"
                onClick={() => handleTabChange('messages')}
                style={{ fontSize: '0.6rem', padding: '3px 6px' }}>
                <i className="bi bi-eye me-1"></i>
                Consulter
              </button>
            </div>
          </div>
        </div>
        
        {/* ✅ Carte Suggestions - MODIFIÉE avec lien vers page dédiée */}
        <div className="col-6 col-md-3">
          <div className="card border-0 shadow-sm h-100 text-center" 
               style={{ borderRadius: '12px', transition: 'transform 0.2s' }}>
            <div className="card-body p-2">
              <div className="bg-warning bg-opacity-10 rounded-circle d-inline-flex p-1 mb-1">
                <i className="bi bi-lightbulb-fill text-warning" style={{ fontSize: '1.2rem' }}></i>
              </div>
              <h3 className="h4 mb-0 fw-bold text-warning">
                {suggestionsStats?.total || 0}
                {suggestionsEnAttente > 0 && (
                  <span className="badge bg-danger ms-1" style={{ fontSize: '0.6rem' }}>
                    {suggestionsEnAttente}
                  </span>
                )}
              </h3>
              <p className="text-muted mb-1" style={{ fontSize: '0.65rem' }}>
                <i className="bi bi-info-circle me-1"></i>
                Suggestions
              </p>
              {/* ✅ LIEN VERS PAGE DÉDIÉE au lieu de bouton */}
              <Link 
                to="/expert/suggestions" 
                className="btn btn-xs btn-outline-warning w-100 rounded-pill"
                style={{ fontSize: '0.6rem', padding: '3px 6px' }}>
                <i className="bi bi-eye me-1"></i>
                Consulter
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation par onglets */}
      <div className="mb-4">
        <div className="d-flex gap-2 flex-wrap border-bottom pb-2"
             style={{ borderColor: 'var(--gray-300)' }}>
          {[
            { id: 'dashboard', label: 'Tableau de bord', icon: 'bi-speedometer2' },
            { id: 'criteres', label: 'Critères', icon: 'bi-funnel' },
            { id: 'notifications', label: 'Notifications', icon: 'bi-bell' },
            { id: 'messages', label: 'Messages', icon: 'bi-envelope', badge: messagesNonLus },
            // ✅ NOUVEAU : Onglet Suggestions
            { 
              id: 'suggestions', 
              label: 'Suggestions', 
              icon: 'bi-lightbulb', 
              badge: suggestionsEnAttente 
            }
          ].map(tab => (
            <button
              key={tab.id}
              className={`btn btn-sm ${activeTab === tab.id ? 'btn-primary' : 'btn-outline-secondary'} px-3 py-1`}
              onClick={() => handleTabChange(tab.id)}
              style={{ 
                borderRadius: '20px',
                fontWeight: activeTab === tab.id ? '500' : '400',
                fontSize: '0.8rem'
              }}
            >
              <i className={`${tab.icon} me-1`} style={{ fontSize: '0.8rem' }}></i>
              {tab.label}
              {tab.badge > 0 && (
                <span className="badge bg-danger ms-1 rounded-pill" style={{ fontSize: '0.6rem' }}>{tab.badge}</span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Contenu Dashboard - Offres */}
      {activeTab === 'dashboard' && (
        <div>
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h5 className="mb-0 fw-semibold" style={{ fontSize: '1rem', color: '#1a1a2e' }}>
              <i className="bi bi-star-fill text-warning me-1"></i>
              Offres qui vous correspondent
            </h5>
            <Link to="/offres" className="btn btn-sm btn-link text-decoration-none" 
                  style={{ color: 'var(--primary)', fontSize: '0.8rem' }}>
              Voir toutes <i className="bi bi-arrow-right ms-1"></i>
            </Link>
          </div>
          
          {recent_matching_offres && recent_matching_offres.length > 0 ? (
            <div className="row g-3">
              {recent_matching_offres.slice(0, 6).map((offre) => (
                <div className="col-md-6 col-lg-4" key={offre.id}>
                  <div className="card border-0 shadow-sm h-100" 
                       style={{ borderRadius: '12px' }}>
                    <div className="card-body p-3">
                      <div className="d-flex justify-content-between align-items-start mb-2">
                        <span className="badge bg-success rounded-pill px-2 py-1" style={{ fontSize: '0.65rem' }}>Ouvert</span>
                        <small className="text-muted" style={{ fontSize: '0.65rem' }}>
                          <i className="bi bi-calendar3 me-1"></i>
                          {new Date(offre.date_cloture).toLocaleDateString('fr-FR')}
                        </small>
                      </div>
                      <h6 className="card-title fw-bold mb-1" style={{ fontSize: '0.85rem' }}>{offre.titre}</h6>
                      <p className="text-muted small mb-2" style={{ fontSize: '0.7rem' }}>{offre.organisme}</p>
                      <p className="card-text text-secondary mb-2" style={{ fontSize: '0.7rem' }}>{offre.description?.substring(0, 80)}...</p>
                      <Link to={`/offres/${offre.id}`} 
                            className="btn btn-sm btn-primary w-100 rounded-pill"
                            style={{ fontSize: '0.7rem', padding: '5px' }}>
                        <i className="bi bi-eye me-1"></i>
                        Voir détails
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="card border-0 shadow-sm text-center py-4" 
                 style={{ borderRadius: '12px' }}>
              <div className="card-body">
                <i className="bi bi-inbox fs-1 text-muted"></i>
                <p className="text-muted mt-2 mb-0 small">Aucune offre ne correspond à vos critères</p>
                <button 
                  className="btn btn-link btn-sm mt-1" 
                  onClick={() => handleTabChange('criteres')}
                  style={{ color: 'var(--primary)', fontSize: '0.75rem' }}
                >
                  <i className="bi bi-plus-circle me-1"></i>
                  Ajouter des critères
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ✅ Contenu Suggestions - Résumé rapide dans le dashboard */}
      {activeTab === 'suggestions' && (
        <div>
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h5 className="mb-0 fw-semibold" style={{ fontSize: '1rem', color: '#1a1a2e' }}>
              <i className="bi bi-lightbulb-fill text-warning me-1"></i>
              Mes suggestions d'offres
            </h5>
            <Link 
              to="/expert/suggestions" 
              className="btn btn-sm btn-primary"
              style={{ fontSize: '0.8rem' }}
            >
              <i className="bi bi-arrow-right me-1"></i>
              Voir toutes les suggestions
            </Link>
          </div>
          
          {suggestionsStats && suggestionsStats.total > 0 ? (
            <div className="row g-3">
              {/* Résumé des statistiques */}
              <div className="col-12">
                <div className="card border-0 shadow-sm" style={{ borderRadius: '12px' }}>
                  <div className="card-body p-3">
                    <div className="row g-2 text-center">
                      <div className="col-3">
                        <div className="p-2 bg-warning bg-opacity-10 rounded">
                          <h4 className="mb-0 fw-bold text-warning">{suggestionsStats.en_attente}</h4>
                          <small className="text-muted" style={{ fontSize: '0.7rem' }}>En attente</small>
                        </div>
                      </div>
                      <div className="col-3">
                        <div className="p-2 bg-info bg-opacity-10 rounded">
                          <h4 className="mb-0 fw-bold text-info">{suggestionsStats.consultees}</h4>
                          <small className="text-muted" style={{ fontSize: '0.7rem' }}>Consultées</small>
                        </div>
                      </div>
                      <div className="col-3">
                        <div className="p-2 bg-success bg-opacity-10 rounded">
                          <h4 className="mb-0 fw-bold text-success">{suggestionsStats.acceptees}</h4>
                          <small className="text-muted" style={{ fontSize: '0.7rem' }}>Acceptées</small>
                        </div>
                      </div>
                      <div className="col-3">
                        <div className="p-2 bg-danger bg-opacity-10 rounded">
                          <h4 className="mb-0 fw-bold text-danger">{suggestionsStats.refusees}</h4>
                          <small className="text-muted" style={{ fontSize: '0.7rem' }}>Refusées</small>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Message d'action */}
              {suggestionsEnAttente > 0 && (
                <div className="col-12">
                  <div className="alert alert-warning d-flex align-items-center" role="alert" style={{ borderRadius: '12px' }}>
                    <i className="bi bi-exclamation-triangle-fill me-2 fs-4"></i>
                    <div className="flex-grow-1">
                      <strong>Vous avez {suggestionsEnAttente} suggestion{suggestionsEnAttente > 1 ? 's' : ''} en attente de réponse !</strong>
                      <p className="mb-0 small mt-1">
                        L'administrateur vous a suggéré des offres correspondant à votre profil. Prenez le temps de les consulter et d'y répondre.
                      </p>
                    </div>
                    <Link 
                      to="/expert/suggestions" 
                      className="btn btn-warning btn-sm"
                    >
                      <i className="bi bi-eye me-1"></i>
                      Répondre
                    </Link>
                  </div>
                </div>
              )}
              
              {suggestionsEnAttente === 0 && suggestionsStats.total > 0 && (
                <div className="col-12">
                  <div className="alert alert-success d-flex align-items-center" role="alert" style={{ borderRadius: '12px' }}>
                    <i className="bi bi-check-circle-fill me-2 fs-4"></i>
                    <div>
                      <strong>Bien joué !</strong> Vous avez traité toutes vos suggestions.
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="card border-0 shadow-sm text-center py-4" 
                 style={{ borderRadius: '12px' }}>
              <div className="card-body">
                <i className="bi bi-lightbulb fs-1 text-muted"></i>
                <p className="text-muted mt-2 mb-0 small">Aucune suggestion pour le moment</p>
                <p className="text-muted small">
                  L'administrateur vous suggérera des offres correspondant à votre profil.
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Autres onglets */}
      {activeTab === 'criteres' && <ExpertCriteres />}
      {activeTab === 'notifications' && <Notifications />}
      {activeTab === 'messages' && <Messagerie />}
    </div>
  );
};

export default ExpertDashboard;