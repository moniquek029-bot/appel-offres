// src/pages/ExpertDashboard.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

const ExpertDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await api.get('/expert/dashboard/');
        setDashboardData(response.data);
      } catch (err) {
        console.error('Erreur chargement dashboard:', err);
        setError('Impossible de charger le tableau de bord');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="container py-5 text-center">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Chargement...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container py-5">
        <div className="alert alert-danger">{error}</div>
      </div>
    );
  }

  // ✅ Déstructuration UNIQUE et correcte
  const { user, profile, stats, recent_matching_offres, next_steps } = dashboardData || {};

  // Protection si les données sont incomplètes
  if (!user || !stats) {
    return (
      <div className="container py-5">
        <div className="alert alert-warning">Données du dashboard incomplètes.</div>
      </div>
    );
  }

  return (
    <div className="container py-4">
      
      {/* === EN-TÊTE + STATUT PROFIL === */}
      <div className="row mb-4">
        <div className="col-12">
          <h2 className="mb-1">👋 Bonjour, {user.nom || user.first_name}</h2>
          <p className="text-muted">Tableau de bord Expert</p>
          
          {/* ✅ Affichage du statut du profil (CORRIGÉ : profile est à la racine) */}
          <div className="alert alert-light border d-flex align-items-center justify-content-between mt-3" role="alert">
            <div>
              <strong>📋 État du profil :</strong>{' '}
              <span className={`badge ${profile?.cv_fichier ? 'bg-success' : 'bg-warning text-dark'} ms-2`}>
                {profile?.cv_fichier ? '✅ Profil complet' : '⚠️ CV manquant'}
              </span>
            </div>
            {!profile?.cv_fichier && (
              <Link to="/expert/profile" className="btn btn-sm btn-primary">
                + Ajouter mon CV
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* === STATISTIQUES === */}
      <div className="row g-3 mb-4">
        <div className="col-md-4">
          <div className="card border-0 shadow-sm h-100">
            <div className="card-body text-center">
              <div className="display-4 text-primary mb-2">📄</div>
              <h3 className="h2 mb-1">{stats.criteres_count}</h3>
              <p className="text-muted mb-0">Critères de recherche</p>
            </div>
          </div>
        </div>
        
        <div className="col-md-4">
          <div className="card border-0 shadow-sm h-100">
            <div className="card-body text-center">
              <div className="display-4 text-success mb-2">🎯</div>
              <h3 className="h2 mb-1">{stats.matching_offres_count}</h3>
              <p className="text-muted mb-0">Offres correspondantes</p>
            </div>
          </div>
        </div>
        
        <div className="col-md-4">
          <div className="card border-0 shadow-sm h-100">
            <div className="card-body text-center">
              <div className="display-4 text-info mb-2">📋</div>
              <h3 className="h2 mb-1">
                {stats.profile_complete ? '✅' : '⚠️'}
              </h3>
              <p className="text-muted mb-0">
                Profil {stats.profile_complete ? 'complété' : 'incomplet'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* === ACTIONS RECOMMANDÉES === */}
      {next_steps && next_steps.length > 0 && (
        <div className="row mb-4">
          <div className="col-12">
            <div className="card border-0 shadow-sm">
              <div className="card-header bg-light">
                <h5 className="mb-0">📌 Actions recommandées</h5>
              </div>
              <div className="card-body">
                {next_steps.map((step, index) => (
                  <div 
                    key={index} 
                    className={`alert alert-${
                      step.priority === 'high' ? 'danger' : 
                      step.priority === 'medium' ? 'warning' : 'info'
                    } d-flex justify-content-between align-items-center mb-2`}
                  >
                    <span>{step.message}</span>
                    <Link to={step.url} className="btn btn-sm btn-outline-dark">
                      {step.action === 'upload_cv' && 'Télécharger'}
                      {step.action === 'add_criteria' && 'Ajouter'}
                      {step.action === 'browse_offers' && 'Consulter'}
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* === OFFRES CORRESPONDANTES === */}
      <div className="row">
        <div className="col-12">
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h4 className="mb-0">🎯 Offres correspondant à vos critères</h4>
            <Link to="/offres" className="btn btn-outline-primary btn-sm">
              Voir toutes les offres
            </Link>
          </div>
          
          {recent_matching_offres && recent_matching_offres.length > 0 ? (
            <div className="row g-3">
              {recent_matching_offres.map((offre) => (
                <div className="col-md-6 col-lg-4" key={offre.id}>
                  <div className="card h-100 border-0 shadow-sm">
                    <div className="card-body">
                      <h6 className="card-title text-primary mb-2">{offre.titre}</h6>
                      <p className="text-muted small mb-2">{offre.organisme}</p>
                      <p className="card-text small text-truncate-2 mb-3">
                        {offre.description?.substring(0, 100)}...
                      </p>
                      <div className="d-flex justify-content-between align-items-center">
                        <small className="text-muted">
                          📅 {new Date(offre.date_cloture).toLocaleDateString('fr-FR')}
                        </small>
                        {offre.url_tdr && (
                          <a 
                            href={offre.url_tdr} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="btn btn-sm btn-primary"
                          >
                            🔗 TDR
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="alert alert-info">
              Aucune offre ne correspond actuellement à vos critères.
              <br />
              <Link to="/expert/criteres" className="fw-bold">
                Modifiez vos critères de recherche
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ExpertDashboard;