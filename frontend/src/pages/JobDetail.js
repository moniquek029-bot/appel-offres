// src/pages/JobDetail.jsx - Version corrigée avec logique intelligente TDR/Redirection
// + Persistance des filtres via l'historique du navigateur
import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

const JobDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate(); // ✅ AJOUTÉ pour la navigation intelligente
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

  // ✅ NOUVELLE FONCTION : Retour intelligent qui préserve les filtres
  const handleBack = () => {
    // ✅ Si l'historique contient la page précédente (avec filtres), on y retourne
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      // Sinon, on va vers la liste des offres par défaut
      navigate('/offres');
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Non spécifiée';
    return new Date(dateStr).toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric' });
  };

  // ✅ CORRECTION: Construire l'URL complète sans duplication
  const getFullPdfUrl = (url) => {
    if (!url) return null;
    
    // Si l'URL est déjà absolue (commence par http), la retourner telle quelle
    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url;
    }
    
    // Sinon, c'est un chemin relatif → ajouter le backend URL
    return `http://localhost:8000${url.startsWith('/') ? '' : '/'}${url}`;
  };

  // ✅ DÉTECTER le type de document disponible
  const getDocumentInfo = () => {
    // Priorité 1 : Fichier PDF local (téléchargé sur notre serveur)
    if (offre?.fichier_pdf_url) {
      return {
        type: 'local_pdf',
        url: getFullPdfUrl(offre.fichier_pdf_url),
        label: 'Télécharger le TDR (PDF)',
        icon: 'bi-file-earmark-pdf-fill',
        isPdf: true
      };
    }
    
    // Priorité 2 : URL TDR externe (vrai PDF sur un autre site)
    if (offre?.url_tdr) {
      const isRedirect = offre.url_tdr === offre.url_source;
      
      if (isRedirect) {
        // C'est une redirection vers le site source
        return {
          type: 'redirect',
          url: offre.url_tdr,
          label: 'Voir sur le site de l\'organisme',
          icon: 'bi-box-arrow-up-right',
          isPdf: false
        };
      } else {
        // C'est un vrai PDF externe
        return {
          type: 'external_pdf',
          url: offre.url_tdr,
          label: 'Télécharger le TDR',
          icon: 'bi-file-earmark-pdf-fill',
          isPdf: true
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
        isPdf: false
      };
    }
    
    return null;
  };

  const handleDownloadPDF = () => {
    const docInfo = getDocumentInfo();
    
    if (!docInfo) {
      alert(' Aucun document disponible pour cette offre');
      return;
    }
    
    console.log(` Ouverture (${docInfo.type}):`, docInfo.url);
    
    try {
      // ✅ CORRECTION: Utiliser l'URL directement sans manipulation
      window.open(docInfo.url, '_blank', 'noopener,noreferrer');
    } catch (err) {
      console.error(' Erreur ouverture URL:', err);
      alert(' Impossible d\'ouvrir le document. Veuillez réessayer.');
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
        {/* ✅ MODIFIÉ : Bouton retour intelligent */}
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
  const isAdmin = user?.role === 'ADMIN';

  return (
    <div className="container py-4">
      {/* ✅ MODIFIÉ : Bouton retour qui préserve les filtres */}
      <button 
        onClick={handleBack}
        className="btn btn-outline-secondary mb-3"
      >
        <i className="bi bi-arrow-left me-1"></i>
        Retour aux offres
      </button>
      
      <div className="card shadow-sm">
        <div className="card-header text-white" style={{background: 'linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%)'}}>
          <h3 className="mb-0">{offre.titre}</h3>
        </div>
        
        <div className="card-body">
          {/* Infos générales */}
          <div className="row mb-4">
            <div className="col-md-6">
              <p><strong>
                 <i className="bi bi-c"></i>
                 Organisme :
                 </strong> {offre.organisme}
              </p>
            </div>
            <div className="col-md-6">
              <p>
                <strong>
                  <i className="bi bi-calendar-x me-1 text-muted"></i>
                  Date de clôture :
                </strong> {formatDate(offre.date_cloture)}
              </p>
            </div>
            <div className="col-md-6">
              <p>
                <strong>
                  <i className="bi bi-calendar-check me-1 text-muted"></i>
                  Publication :
                </strong> {formatDate(offre.date_publication)}
              </p>
            </div>
            <div className="col-md-6">
              <p>
                <i className="bi bi-globe-americas me-1 text-muted"></i>
                <strong> Pays :</strong> {offre.pays === 'BF' ? '🇧🇫 Burkina Faso' : offre.pays}
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
                // ✅ UTILISATEUR CONNECTÉ : afficher le bouton adapté au type de document
                <div className="d-flex gap-3 flex-wrap align-items-center">
                  {docInfo.type === 'local_pdf' && (
                    // PDF local stocké sur notre serveur
                    <button 
                      onClick={handleDownloadPDF} 
                      className="btn btn-lg fw-bold"
                      style={{ 
                        display: 'inline-flex', 
                        alignItems: 'center', 
                        gap: '8px', 
                        background: 'linear-gradient(135deg, #D35400 0%, #F59E0B 100%)', 
                        border: 'none', 
                        color: 'white', 
                        boxShadow: '0 2px 8px rgba(211, 84, 0, 0.15)' 
                      }}
                    >
                      <i className={`bi ${docInfo.icon} me-1`}></i>
                      {docInfo.label}
                    </button>
                  )}
                  
                  {docInfo.type === 'external_pdf' && (
                    // PDF externe sur un autre site
                    <button 
                      onClick={handleDownloadPDF} 
                      className="btn btn-lg fw-bold"
                      style={{ 
                        display: 'inline-flex', 
                        alignItems: 'center', 
                        gap: '8px', 
                        background: 'linear-gradient(135deg, #C0392B 0%, #E74C3C 100%)', 
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
                    // Redirection vers le site source
                    <button 
                      onClick={handleDownloadPDF} 
                      className="btn btn-lg fw-bold"
                      style={{ 
                        display: 'inline-flex', 
                        alignItems: 'center', 
                        gap: '8px', 
                        background: 'linear-gradient(135deg, #2980B9 0%, #3498DB 100%)', 
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
              ) : (
                //  UTILISATEUR NON CONNECTÉ : afficher message avec lien de connexion
                <div className="alert alert-info d-flex flex-column gap-2">
                  <p className="mb-0">
                    <strong> Connexion requise</strong>
                  </p>
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
              // ❌ AUCUN DOCUMENT DISPONIBLE
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