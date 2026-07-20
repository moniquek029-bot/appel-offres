import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const ExpertSuggestions = () => {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [filter, setFilter] = useState('');
  const [selectedSuggestion, setSelectedSuggestion] = useState(null);
  const [showResponseModal, setShowResponseModal] = useState(false);
  const [responseForm, setResponseForm] = useState({
    statut_reponse: '',
    commentaire_expert: ''
  });
  const [submitting, setSubmitting] = useState(false);
  
  const [selectedOffre, setSelectedOffre] = useState(null);
  const [showOffreModal, setShowOffreModal] = useState(false);
  const [offreLoading, setOffreLoading] = useState(false);
  
  const navigate = useNavigate();

  useEffect(() => {
    fetchSuggestions();
  }, [filter]);

  const fetchSuggestions = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const params = {};
      if (filter) params.statut = filter;
      
      const res = await api.get('/expert/suggestions/', { params });
      setSuggestions(res.data.suggestions || []);
      // ✅ stats n'est plus utilisé
    } catch (err) {
      console.error('❌ Erreur suggestions:', err);
      setError('Impossible de charger les suggestions');
    } finally {
      setLoading(false);
    }
  };

  const openResponseModal = (suggestion) => {
    setSelectedSuggestion(suggestion);
    setResponseForm({
      statut_reponse: '',
      commentaire_expert: ''
    });
    setShowResponseModal(true);
  };

  const closeResponseModal = () => {
    setShowResponseModal(false);
    setSelectedSuggestion(null);
    setResponseForm({ statut_reponse: '', commentaire_expert: '' });
  };

  const handleResponse = async (e) => {
    e.preventDefault();
    
    if (!responseForm.statut_reponse) {
      setError('Veuillez sélectionner une réponse');
      return;
    }
    
    setSubmitting(true);
    setError(null);
    
    try {
      await api.post(
        `/expert/suggestions/${selectedSuggestion.id}/repondre/`,
        responseForm
      );
      
      setSuccess(`✅ Suggestion ${responseForm.statut_reponse === 'ACCEPTEE' ? 'acceptée' : responseForm.statut_reponse === 'REFUSEE' ? 'refusée' : 'marquée comme consultée'} avec succès`);
      closeResponseModal();
      fetchSuggestions();
      
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error('❌ Erreur réponse:', err);
      setError(err.response?.data?.error || 'Erreur lors de la réponse');
    } finally {
      setSubmitting(false);
    }
  };

  const handleQuickConsult = async (suggestionId) => {
    try {
      await api.post(`/expert/suggestions/${suggestionId}/marquer-consultee/`);
      setSuccess('✅ Suggestion marquée comme consultée');
      fetchSuggestions();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('Erreur lors du marquage');
    }
  };

  const handleViewOffre = async (sug) => {
    setOffreLoading(true);
    try {
      const res = await api.get(`/offres/${sug.offre}/`);
      setSelectedOffre(res.data);
      setShowOffreModal(true);
    } catch (err) {
      console.error('❌ Erreur chargement offre:', err);
      setSelectedOffre({
        id: sug.offre,
        titre: sug.offre_titre,
        organisme: sug.offre_organisme,
        description: sug.offre_description,
        pays: sug.offre_pays,
        date_cloture: sug.offre_date_cloture,
        url_source: sug.offre_url_source,
        statut: 'Ouvert',
        mode_acquisition: 'AUTO'
      });
      setShowOffreModal(true);
    } finally {
      setOffreLoading(false);
    }
  };

  const closeOffreModal = () => {
    setShowOffreModal(false);
    setSelectedOffre(null);
  };

  const getStatutBadge = (statut) => {
    const styles = {
      'EN_ATTENTE': 'bg-warning text-dark',
      'CONSULTEE': 'bg-info text-white',
      'ACCEPTEE': 'bg-success',
      'REFUSEE': 'bg-danger'
    };
    const labels = {
      'EN_ATTENTE': '⏳ En attente',
      'CONSULTEE': '👁️ Consultée',
      'ACCEPTEE': '✅ Acceptée',
      'REFUSEE': ' Refusée'
    };
    return (
      <span className={`badge ${styles[statut] || 'bg-secondary'}`} style={{ fontSize: '0.7rem' }}>
        {labels[statut] || statut}
      </span>
    );
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
    <div className="container-fluid py-3">
      {/* Messages */}
      {error && (
        <div className="alert alert-danger alert-dismissible fade show py-2 small d-flex align-items-center">
          <i className="bi bi-exclamation-triangle-fill me-2"></i>
          <span className="flex-grow-1">{error}</span>
          <button type="button" className="btn-close btn-close-sm" onClick={() => setError(null)}></button>
        </div>
      )}
      {success && (
        <div className="alert alert-success alert-dismissible fade show py-2 small d-flex align-items-center">
          <i className="bi bi-check-circle-fill me-2"></i>
          <span className="flex-grow-1">{success}</span>
          <button type="button" className="btn-close btn-close-sm" onClick={() => setSuccess(null)}></button>
        </div>
      )}

      {/* En-tête */}
      <div className="row mb-3">
        <div className="col-12">
          <h3 className="mb-0" style={{ fontSize: '1.5rem' }}>
            <i className="bi bi-lightbulb me-2"></i>
            Mes Suggestions d'Offres
          </h3>
          <p className="text-muted small mb-0">
            Offres suggérées par l'administrateur selon votre profil
          </p>
        </div>
      </div>

      {/* ✅ STATISTIQUES SUPPRIMÉES */}

      {/* Filtres */}
      <div className="card mb-3">
        <div className="card-body py-2">
          <div className="d-flex gap-2 flex-wrap">
            <button 
              className={`btn btn-sm ${!filter ? 'btn-primary' : 'btn-outline-secondary'}`}
              onClick={() => setFilter('')}
              style={{ fontSize: '0.75rem' }}
            >
              <i className="bi bi-inbox me-1"></i>Toutes
            </button>
            <button 
              className={`btn btn-sm ${filter === 'EN_ATTENTE' ? 'btn-warning' : 'btn-outline-secondary'}`}
              onClick={() => setFilter('EN_ATTENTE')}
              style={{ fontSize: '0.75rem' }}
            >
              <i className="bi bi-hourglass-split me-1"></i>En attente
            </button>
            <button 
              className={`btn btn-sm ${filter === 'CONSULTEE' ? 'btn-info text-white' : 'btn-outline-secondary'}`}
              onClick={() => setFilter('CONSULTEE')}
              style={{ fontSize: '0.75rem' }}
            >
              <i className="bi bi-eye me-1"></i>Consultées
            </button>
            <button 
              className={`btn btn-sm ${filter === 'ACCEPTEE' ? 'btn-success' : 'btn-outline-secondary'}`}
              onClick={() => setFilter('ACCEPTEE')}
              style={{ fontSize: '0.75rem' }}
            >
              <i className="bi bi-check-circle me-1"></i>Acceptées
            </button>
            <button 
              className={`btn btn-sm ${filter === 'REFUSEE' ? 'btn-danger' : 'btn-outline-secondary'}`}
              onClick={() => setFilter('REFUSEE')}
              style={{ fontSize: '0.75rem' }}
            >
              <i className="bi bi-x-circle me-1"></i>Refusées
            </button>
          </div>
        </div>
      </div>

      {/* Liste des suggestions */}
      {suggestions.length === 0 ? (
        <div className="card">
          <div className="card-body text-center py-5">
            <i className="bi bi-inbox" style={{ fontSize: '3rem', color: '#ccc' }}></i>
            <p className="text-muted mt-2 mb-0">Aucune suggestion pour le moment</p>
          </div>
        </div>
      ) : (
        <div className="row g-3">
          {suggestions.map(sug => (
            <div key={sug.id} className="col-12">
              <div className="card border-0 shadow-sm">
                <div className="card-body p-3">
                  <div className="d-flex justify-content-between align-items-start mb-2">
                    <div>
                      <h5 className="mb-1 fw-bold" style={{ fontSize: '1rem' }}>
                        <i className="bi bi-file-earmark-text me-1 text-primary"></i>
                        {sug.offre_titre}
                      </h5>
                      <p className="mb-1 small text-muted">
                        <i className="bi bi-building me-1"></i>
                        {sug.offre_organisme}
                      </p>
                    </div>
                    {getStatutBadge(sug.statut_reponse)}
                  </div>

                  <div className="row g-2 mb-3">
                    <div className="col-md-4">
                      <small className="text-muted d-block" style={{ fontSize: '0.7rem' }}>
                        <i className="bi bi-geo-alt me-1"></i>Pays
                      </small>
                      <span style={{ fontSize: '0.8rem' }}>{sug.offre_pays || 'N/A'}</span>
                    </div>
                    <div className="col-md-4">
                      <small className="text-muted d-block" style={{ fontSize: '0.7rem' }}>
                        <i className="bi bi-calendar-x me-1"></i>Date de clôture
                      </small>
                      <span style={{ fontSize: '0.8rem' }}>
                        {sug.offre_date_cloture ? new Date(sug.offre_date_cloture).toLocaleDateString('fr-FR') : 'N/A'}
                      </span>
                    </div>
                    <div className="col-md-4">
                      <small className="text-muted d-block" style={{ fontSize: '0.7rem' }}>
                        <i className="bi bi-clock me-1"></i>Suggérée le
                      </small>
                      <span style={{ fontSize: '0.8rem' }}>
                        {new Date(sug.date_suggestion).toLocaleDateString('fr-FR')}
                      </span>
                    </div>
                  </div>

                  {sug.offre_description && (
                    <div className="mb-3">
                      <small className="text-muted d-block" style={{ fontSize: '0.7rem' }}>
                        <i className="bi bi-card-text me-1"></i>Description
                      </small>
                      <p className="mb-0 small" style={{ fontSize: '0.8rem' }}>
                        {sug.offre_description.substring(0, 200)}
                        {sug.offre_description.length > 200 && '...'}
                      </p>
                    </div>
                  )}

                  {sug.commentaire_admin && (
                    <div className="alert alert-light mb-3 py-2" style={{ borderLeft: '3px solid #1E3A8A' }}>
                      <small className="text-primary fw-semibold d-block" style={{ fontSize: '0.7rem' }}>
                        <i className="bi bi-chat-left-text me-1"></i>Commentaire de l'administrateur :
                      </small>
                      <p className="mb-0 small" style={{ fontSize: '0.8rem' }}>
                        {sug.commentaire_admin}
                      </p>
                    </div>
                  )}

                  {sug.commentaire_expert && (
                    <div className="alert alert-success mb-3 py-2" style={{ borderLeft: '3px solid #059669' }}>
                      <small className="text-success fw-semibold d-block" style={{ fontSize: '0.7rem' }}>
                        <i className="bi bi-reply-fill me-1"></i>Votre réponse :
                      </small>
                      <p className="mb-0 small" style={{ fontSize: '0.8rem' }}>
                        {sug.commentaire_expert}
                      </p>
                    </div>
                  )}

                  <div className="d-flex gap-2 flex-wrap">
                    <button 
                      onClick={() => handleViewOffre(sug)}
                      className="btn btn-sm btn-outline-primary"
                      style={{ fontSize: '0.75rem' }}
                    >
                      <i className="bi bi-eye me-1"></i>
                      Voir l'offre
                    </button>
                    
                    {sug.statut_reponse === 'EN_ATTENTE' && (
                      <>
                        <button 
                          className="btn btn-sm btn-outline-info"
                          onClick={() => handleQuickConsult(sug.id)}
                          style={{ fontSize: '0.75rem' }}
                        >
                          <i className="bi bi-eye me-1"></i>
                          Marquer consultée
                        </button>
                        <button 
                          className="btn btn-sm btn-primary"
                          onClick={() => openResponseModal(sug)}
                          style={{ fontSize: '0.75rem' }}
                        >
                          <i className="bi bi-reply me-1"></i>
                          Répondre
                        </button>
                      </>
                    )}
                    
                    {sug.statut_reponse !== 'EN_ATTENTE' && (
                      <button 
                        className="btn btn-sm btn-outline-secondary"
                        onClick={() => openResponseModal(sug)}
                        style={{ fontSize: '0.75rem' }}
                      >
                        <i className="bi bi-pencil me-1"></i>
                        Modifier ma réponse
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ✅ Modal de visualisation de l'offre - SANS MODE D'ACQUISITION */}
      {showOffreModal && selectedOffre && (
        <div className="modal fade show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.7)', zIndex: 1050 }}>
          <div className="modal-dialog modal-dialog-centered modal-xl modal-dialog-scrollable">
            <div className="modal-content" style={{ borderRadius: '16px', border: 'none', overflow: 'hidden' }}>
              
              {/* En-tête avec dégradé */}
              <div 
                className="modal-header py-3 px-4 text-white"
                style={{ 
                  background: 'linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%)',
                  borderBottom: '3px solid #F59E0B'
                }}
              >
                <h5 className="modal-title fw-bold" style={{ fontSize: '1.1rem' }}>
                  <i className="bi bi-file-earmark-text me-2"></i>
                  Détails de l'offre suggérée
                </h5>
                <button 
                  type="button" 
                  className="btn-close btn-close-white" 
                  onClick={closeOffreModal}
                  style={{ filter: 'brightness(0) invert(1)' }}
                ></button>
              </div>
              
              <div className="modal-body p-4" style={{ backgroundColor: '#f8fafc' }}>
                {offreLoading ? (
                  <div className="text-center py-5">
                    <div className="spinner-border text-primary" role="status" style={{ width: '3rem', height: '3rem' }}>
                      <span className="visually-hidden">Chargement...</span>
                    </div>
                    <p className="text-muted mt-3">Chargement des détails...</p>
                  </div>
                ) : (
                  <>
                    {/* Titre de l'offre */}
                    <div 
                      className="p-3 mb-4 text-white"
                      style={{ 
                        background: 'linear-gradient(135deg, #1E3A8A, #172554)',
                        borderRadius: '12px',
                        boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                      }}
                    >
                      <h4 className="fw-bold mb-2" style={{ fontSize: '1.3rem' }}>
                        {selectedOffre.titre}
                      </h4>
                      <p className="mb-0" style={{ fontSize: '0.95rem', opacity: 0.9 }}>
                        <i className="bi bi-building me-2"></i>
                        {selectedOffre.organisme}
                      </p>
                    </div>
                    
                    {/* Informations principales */}
                    <div className="row g-3 mb-4">
                      <div className="col-md-4">
                        <div className="card border-0 shadow-sm h-100" style={{ borderRadius: '12px' }}>
                          <div className="card-body p-3 text-center">
                            <div className="bg-primary bg-opacity-10 rounded-circle d-inline-flex p-2 mb-2">
                              <i className="bi bi-geo-alt-fill text-primary" style={{ fontSize: '1.5rem' }}></i>
                            </div>
                            <small className="text-muted d-block" style={{ fontSize: '0.7rem' }}>Pays</small>
                            <span className="fw-bold" style={{ fontSize: '1rem', color: '#1E3A8A' }}>
                              {selectedOffre.pays || 'N/A'}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="col-md-4">
                        <div className="card border-0 shadow-sm h-100" style={{ borderRadius: '12px' }}>
                          <div className="card-body p-3 text-center">
                            <div className="bg-danger bg-opacity-10 rounded-circle d-inline-flex p-2 mb-2">
                              <i className="bi bi-calendar-x-fill text-danger" style={{ fontSize: '1.5rem' }}></i>
                            </div>
                            <small className="text-muted d-block" style={{ fontSize: '0.7rem' }}>Date de clôture</small>
                            <span className="fw-bold" style={{ fontSize: '1rem', color: '#DC2626' }}>
                              {selectedOffre.date_cloture ? new Date(selectedOffre.date_cloture).toLocaleDateString('fr-FR') : 'N/A'}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="col-md-4">
                        <div className="card border-0 shadow-sm h-100" style={{ borderRadius: '12px' }}>
                          <div className="card-body p-3 text-center">
                            <div className={`bg-${selectedOffre.statut === 'Ouvert' ? 'success' : 'secondary'} bg-opacity-10 rounded-circle d-inline-flex p-2 mb-2`}>
                              <i className={`bi bi-info-circle-fill text-${selectedOffre.statut === 'Ouvert' ? 'success' : 'secondary'}`} style={{ fontSize: '1.5rem' }}></i>
                            </div>
                            <small className="text-muted d-block" style={{ fontSize: '0.7rem' }}>Statut</small>
                            <span className={`badge bg-${selectedOffre.statut === 'Ouvert' ? 'success' : 'secondary'}`} style={{ fontSize: '0.9rem' }}>
                              {selectedOffre.statut || 'N/A'}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Description */}
                    {selectedOffre.description && (
                      <div className="card border-0 shadow-sm mb-4" style={{ borderRadius: '12px' }}>
                        <div 
                          className="card-header py-2 px-3 text-white"
                          style={{ 
                            background: 'linear-gradient(135deg, #059669, #047857)',
                            borderRadius: '12px 12px 0 0'
                          }}
                        >
                          <h6 className="mb-0" style={{ fontSize: '0.9rem' }}>
                            <i className="bi bi-card-text me-2"></i>
                            Description de l'offre
                          </h6>
                        </div>
                        <div className="card-body p-3" style={{ backgroundColor: 'white' }}>
                          <p className="mb-0" style={{ fontSize: '0.95rem', lineHeight: '1.6', color: '#334155', whiteSpace: 'pre-wrap' }}>
                            {selectedOffre.description}
                          </p>
                        </div>
                      </div>
                    )}
                    
                    {/* ✅ Date de publication uniquement (mode d'acquisition supprimé) */}
                    {selectedOffre.date_publication && (
                      <div className="row g-3 mb-4">
                        <div className="col-md-12">
                          <div className="card border-0 shadow-sm h-100" style={{ borderRadius: '12px' }}>
                            <div className="card-body p-3">
                              <small className="text-muted d-block mb-1" style={{ fontSize: '0.7rem' }}>
                                <i className="bi bi-calendar-check me-1"></i>Date de publication
                              </small>
                              <span className="fw-semibold" style={{ fontSize: '0.9rem', color: '#1E3A8A' }}>
                                {new Date(selectedOffre.date_publication).toLocaleDateString('fr-FR')}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                    
                    {/* Actions : PDF et lien source */}
                    <div className="row g-3">
                      {selectedOffre.fichier_pdf && (
                        <div className="col-md-6">
                          <a 
                            href={selectedOffre.fichier_pdf} 
                            target="_blank"
                            rel="noopener noreferrer"
                            className="btn w-100 py-2 text-white fw-semibold"
                            style={{ 
                              background: 'linear-gradient(135deg, #DC2626, #B91C1C)',
                              borderRadius: '12px',
                              fontSize: '0.9rem',
                              boxShadow: '0 4px 6px rgba(220, 38, 38, 0.3)'
                            }}
                          >
                            <i className="bi bi-file-earmark-pdf-fill me-2"></i>
                            Télécharger le PDF
                          </a>
                        </div>
                      )}
                      {selectedOffre.url_source && (
                        <div className={selectedOffre.fichier_pdf ? 'col-md-6' : 'col-12'}>
                          <a 
                            href={selectedOffre.url_source} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="btn w-100 py-2 text-white fw-semibold"
                            style={{ 
                              background: 'linear-gradient(135deg, #3B82F6, #1E3A8A)',
                              borderRadius: '12px',
                              fontSize: '0.9rem',
                              boxShadow: '0 4px 6px rgba(59, 130, 246, 0.3)'
                            }}
                          >
                            <i className="bi bi-box-arrow-up-right me-2"></i>
                            Voir sur le site source
                          </a>
                        </div>
                      )}
                    </div>
                  </>
                )}
              </div>
              
              {/* Pied du modal */}
              <div 
                className="modal-footer py-3 px-4"
                style={{ 
                  backgroundColor: '#f1f5f9',
                  borderTop: '2px solid #e2e8f0'
                }}
              >
                <button 
                  type="button" 
                  className="btn btn-secondary btn-sm px-4"
                  onClick={closeOffreModal}
                  style={{ 
                    borderRadius: '8px',
                    fontSize: '0.85rem',
                    fontWeight: '500'
                  }}
                >
                  <i className="bi bi-x-circle me-1"></i>
                  Fermer
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de réponse */}
      {showResponseModal && selectedSuggestion && (
        <div className="modal fade show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header py-2 px-3 bg-primary text-white">
                <h6 className="modal-title" style={{ fontSize: '0.85rem' }}>
                  <i className="bi bi-reply me-2"></i>
                  Répondre à la suggestion
                </h6>
                <button type="button" className="btn-close btn-close-white btn-close-sm" onClick={closeResponseModal}></button>
              </div>
              
              <div className="modal-body py-2 px-3">
                <div className="alert alert-light py-2 small mb-3">
                  <strong>Offre :</strong> {selectedSuggestion.offre_titre}
                </div>
                
                <form onSubmit={handleResponse}>
                  <div className="mb-3">
                    <label className="form-label fw-semibold" style={{ fontSize: '0.75rem' }}>
                      <i className="bi bi-check-circle me-1"></i>
                      Votre décision <span className="text-danger">*</span>
                    </label>
                    <select 
                      className="form-select form-select-sm"
                      value={responseForm.statut_reponse}
                      onChange={(e) => setResponseForm({...responseForm, statut_reponse: e.target.value})}
                      required
                      style={{ fontSize: '0.8rem' }}
                    >
                      <option value="">-- Sélectionnez --</option>
                      <option value="CONSULTEE">👁️ J'ai consulté l'offre</option>
                      <option value="ACCEPTEE">✅ J'accepte cette suggestion (je suis intéressé)</option>
                      <option value="REFUSEE">❌ Je refuse cette suggestion (pas intéressé)</option>
                    </select>
                  </div>
                  
                  <div className="mb-3">
                    <label className="form-label fw-semibold" style={{ fontSize: '0.75rem' }}>
                      <i className="bi bi-chat-left-text me-1"></i>
                      Commentaire (optionnel)
                    </label>
                    <textarea 
                      className="form-control form-control-sm"
                      rows="3"
                      value={responseForm.commentaire_expert}
                      onChange={(e) => setResponseForm({...responseForm, commentaire_expert: e.target.value})}
                      placeholder="Expliquez votre choix..."
                      maxLength={500}
                      style={{ fontSize: '0.8rem' }}
                    />
                    <small className="text-muted">{responseForm.commentaire_expert.length}/500</small>
                  </div>
                  
                  <div className="d-flex gap-2">
                    <button 
                      type="button" 
                      className="btn btn-secondary btn-sm"
                      onClick={closeResponseModal}
                      style={{ fontSize: '0.75rem' }}
                    >
                      <i className="bi bi-x-circle me-1"></i>
                      Annuler
                    </button>
                    <button 
                      type="submit" 
                      className="btn btn-primary btn-sm flex-grow-1"
                      disabled={submitting || !responseForm.statut_reponse}
                      style={{ fontSize: '0.75rem' }}
                    >
                      {submitting ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-1"></span>
                          Envoi...
                        </>
                      ) : (
                        <>
                          <i className="bi bi-send me-1"></i>
                          Envoyer ma réponse
                        </>
                      )}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExpertSuggestions;