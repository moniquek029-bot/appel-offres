// src/pages/JobDetail.jsx - Version épurée
// ✅ Logique intelligente TDR/Redirection
// ✅ Gestion des dates de clôture vides
// ✅ Persistance des filtres via l'historique du navigateur
import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

const JobDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [offre, setOffre] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchOffre = async () => {
      try {
        const response = await api.get(`/offres/${id}/`);
        console.log('📄 Offre reçue:', response.data);
        console.log('  - fichier_pdf_url:', response.data.fichier_pdf_url);
        console.log('  - url_tdr:', response.data.url_tdr);
        console.log('  - url_source:', response.data.url_source);
        console.log('  - date_cloture:', response.data.date_cloture);
        setOffre(response.data);
      } catch (err) {
        console.error('❌ Erreur:', err);
        setError('Offre non trouvée');
      } finally {
        setLoading(false);
      }
    };
    fetchOffre();
  }, [id]);

  // ✅ Retour intelligent qui préserve les filtres
  const handleBack = () => {
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      navigate('/offres');
    }
  };

  // ✅ Formatage des dates avec gestion des valeurs nulles/invalides
  const formatDate = (dateStr) => {
    if (!dateStr) return 'Non précisée';
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return 'Non précisée';
    return d.toLocaleDateString('fr-FR', { 
      day: '2-digit', 
      month: 'long', 
      year: 'numeric' 
    });
  };

  // ✅ Calcul des jours restants
  const getJoursRestants = (dateStr) => {
    if (!dateStr) return null;
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return null;
    
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    d.setHours(0, 0, 0, 0);
    
    const diff = Math.ceil((d - today) / (1000 * 60 * 60 * 24));
    return diff;
  };

  // ✅ Construction d'URL complète sans duplication
  const getFullPdfUrl = (url) => {
    if (!url) return null;
    
    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url;
    }
    
    return `http://localhost:8000${url.startsWith('/') ? '' : '/'}${url}`;
  };

  // ✅ Détection du type de document avec description
  const getDocumentInfo = () => {
    // Priorité 1 : Fichier PDF local (téléchargé sur notre serveur)
    if (offre?.fichier_pdf_url) {
      return {
        type: 'local_pdf',
        url: getFullPdfUrl(offre.fichier_pdf_url),
        label: 'Télécharger le TDR (PDF)',
        icon: 'bi-file-earmark-pdf-fill',
        isPdf: true,
        description: 'Document PDF stocké sur notre plateforme',
        color: '#022186'
      };
    }
    
    // Priorité 2 : URL TDR externe (vrai PDF sur un autre site)
    if (offre?.url_tdr) {
      const isRedirect = offre.url_tdr === offre.url_source;
      
      if (isRedirect) {
        return {
          type: 'redirect',
          url: offre.url_tdr,
          label: 'Voir sur le site de l\'organisme',
          icon: 'bi-box-arrow-up-right',
          isPdf: false,
          description: 'Pas de PDF disponible - Redirection vers le site source',
          color: 'linear-gradient(135deg, #2980B9 0%, #3498DB 100%)'
        };
      } else {
        return {
          type: 'external_pdf',
          url: offre.url_tdr,
          label: 'Télécharger le TDR',
          icon: 'bi-file-earmark-pdf-fill',
          isPdf: true,
          description: 'Document PDF hébergé sur le site de l\'organisme',
          color: 'linear-gradient(135deg, #C0392B 0%, #e05f51 100%)'
        };
      }
    }
    
    // Priorité 3 : Fallback vers url_source
    if (offre?.url_source) {
      return {
        type: 'redirect',
        url: offre.url_source,
        label: 'Voir sur le site de l\'organisme',
        icon: 'bi-box-arrow-up-right',
        isPdf: false,
        description: 'Pas de PDF disponible - Redirection vers le site source',
        color: 'linear-gradient(135deg, #2980B9 0%, #3498DB 100%)'
      };
    }
    
    return null;
  };

  const handleDownloadPDF = () => {
    const docInfo = getDocumentInfo();
    
    if (!docInfo) {
      alert('❌ Aucun document disponible pour cette offre');
      return;
    }
    
    console.log(`🔗 Ouverture (${docInfo.type}):`, docInfo.url);
    
    try {
      window.open(docInfo.url, '_blank', 'noopener,noreferrer');
    } catch (err) {
      console.error('❌ Erreur ouverture URL:', err);
      alert('❌ Impossible d\'ouvrir le document. Veuillez réessayer.');
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

  if (error || !offre) {
    return (
      <div className="container py-5">
        <div className="alert alert-danger">{error || 'Offre non trouvée'}</div>
        <button 
          onClick={handleBack}
          className="btn btn-outline-primary"
        >
          <i className="bi bi-arrow-left me-1"></i>
          Retour
        </button>
      </div>
    );
  }

  const docInfo = getDocumentInfo();
  const hasDocument = !!docInfo;

  return (
    <div className="container py-4">
      {/* Bouton retour qui préserve les filtres */}
      <button 
        onClick={handleBack}
        className="btn btn-outline-secondary mb-3"
      >
        <i className="bi bi-arrow-left me-1"></i>
        Retour aux offres
      </button>
      
      <div className="card shadow-sm">
        {/* En-tête avec gradient */}
        <div className="card-header text-white" style={{background: 'linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%)'}}>
          <h3 className="mb-0">{offre.titre}</h3>
        </div>
        
        <div className="card-body">
          {/* Infos générales */}
          <div className="row mb-4">
            <div className="col-md-6">
              <p>
                <strong>
                  <i className="bi bi-building me-1 text-muted"></i>
                  Organisme :
                </strong>{' '}
                {offre.organisme || 'Non précisé'}
              </p>
            </div>
            
            {/* ✅ DATE DE CLÔTURE AVEC AFFICHAGE CONDITIONNEL */}
            <div className="col-md-6">
              <p>
                <strong>
                  <i className="bi bi-calendar-x me-1 text-muted"></i>
                  Date de clôture :
                </strong>{' '}
                {offre.date_cloture ? (
                  <span className={
                    getJoursRestants(offre.date_cloture) <= 7 && getJoursRestants(offre.date_cloture) >= 0
                      ? 'text-danger fw-bold' 
                      : getJoursRestants(offre.date_cloture) < 0
                      ? 'text-secondary'
                      : 'text-success'
                  }>
                    {formatDate(offre.date_cloture)}
                    {getJoursRestants(offre.date_cloture) > 0 && (
                      <span className="badge bg-warning text-dark ms-2">
                        {getJoursRestants(offre.date_cloture)}j restants
                      </span>
                    )}
                    {getJoursRestants(offre.date_cloture) === 0 && (
                      <span className="badge bg-danger ms-2">Aujourd'hui</span>
                    )}
                    {getJoursRestants(offre.date_cloture) < 0 && (
                      <span className="badge bg-secondary ms-2">Expirée</span>
                    )}
                  </span>
                ) : (
                  <span className="text-muted fst-italic">
                    <i className="bi bi-info-circle me-1"></i>
                    Non précisée
                  </span>
                )}
              </p>
            </div>
            
            <div className="col-md-6">
              <p>
                <strong>
                  <i className="bi bi-calendar-check me-1 text-muted"></i>
                  Publication :
                </strong>{' '}
                {formatDate(offre.date_publication)}
              </p>
            </div>
            
            <div className="col-md-6">
              <p>
                <i className="bi bi-globe-americas me-1 text-muted"></i>
                <strong> Pays :</strong>{' '}
                {offre.pays === 'BF' ? '🇧🇫 Burkina Faso' : offre.pays}
              </p>
            </div>
          </div>
          
          {/* Description */}
          <h5 className="mb-3" style={{color: 'var(--primary)'}}>
            <i className="bi bi-card-text me-1"></i>
            Description
          </h5>
          <div className="mb-4 p-3 bg-light rounded" style={{ whiteSpace: 'pre-line' }}>
            {offre.description || 'Aucune description disponible.'}
          </div>
          
          <hr />
          
          {/* ✅ SECTION DOCUMENT/TDR AMÉLIORÉE */}
          <div className="mb-4">
            <h5 className="mb-3" style={{color: 'var(--primary)'}}>
              <i className="bi bi-file-earmark-text me-1"></i>
              Document de référence
            </h5>
            
            {hasDocument ? (
              user ? (
                <div className="d-flex flex-column gap-3">
                  {/* Bouton principal */}
                  <div className="d-flex gap-3 flex-wrap align-items-center">
                    {docInfo.type === 'local_pdf' && (
                      <button 
                        onClick={handleDownloadPDF} 
                        className="btn btn-lg fw-bold"
                        style={{ 
                          display: 'inline-flex', 
                          alignItems: 'center', 
                          gap: '8px', 
                          background: '#cc8203', 
                          border: 'none', 
                          color: 'white', 
                          boxShadow: '0 2px 8px rgba(171, 160, 6, 0.15)' 
                        }}
                      >
                        <i className={`bi ${docInfo.icon} me-1`}></i>
                        {docInfo.label}
                      </button>
                    )}
                    
                    {docInfo.type === 'external_pdf' && (
                      <button 
                        onClick={handleDownloadPDF} 
                        className="btn btn-lg fw-bold"
                        style={{ 
                          display: 'inline-flex', 
                          alignItems: 'center', 
                          gap: '8px', 
                          background: docInfo.color, 
                          border: 'none', 
                          color: 'white', 
                          boxShadow: '0 2px 8px rgba(192, 57, 43, 0.15)' 
                        }}
                      >
                        <i className={`bi ${docInfo.icon} me-1`}></i>
                        {docInfo.label}
                      </button>
                    )}
                    
                    {docInfo.type === 'redirect' && (
                      <button 
                        onClick={handleDownloadPDF} 
                        className="btn btn-lg fw-bold"
                        style={{ 
                          display: 'inline-flex', 
                          alignItems: 'center', 
                          gap: '8px', 
                          background: docInfo.color, 
                          border: 'none', 
                          color: 'white', 
                          boxShadow: '0 2px 8px rgba(41, 128, 185, 0.15)' 
                        }}
                      >
                        <i className={`bi ${docInfo.icon} me-1`}></i>
                        {docInfo.label}
                      </button>
                    )}
                  </div>
                  
                  {/* Information sur le type de document */}
                  <div className="alert alert-light border d-flex align-items-center gap-2 mb-0">
                    <i className={`bi ${docInfo.isPdf ? 'bi-file-earmark-check-fill text-success' : 'bi-box-arrow-up-right text-primary'}`}></i>
                    <small className="text-muted">
                      {docInfo.description}
                    </small>
                  </div>
                </div>
              ) : (
                <div className="alert alert-info d-flex flex-column gap-2">
                  {/*<p className="mb-0">
                    <strong>🔒 Connexion requise</strong>
                  </p>*/}
                  <p className="mb-0 text-muted">
                    <i className="bi bi-info-circle-fill me-1"></i>
                    Veuillez vous connecter pour accéder au document de cette offre.
                  </p>
                  <div>
                    <Link 
                      to={`/login?from=/offre/${id}`} 
                      className="btn btn-primary btn-sm"
                    >
                      <i className="bi bi-box-arrow-in-right me-1"></i>
                      Se connecter
                    </Link>
                  </div>
                </div>
              )
            ) : (
              <div className="alert alert-warning">
                <i className="bi bi-exclamation-triangle-fill me-2"></i>
                Aucun document n'est disponible pour cette offre.
              </div>
            )}
          </div>
          
        </div>
      </div>
    </div>
  );
};

export default JobDetail;