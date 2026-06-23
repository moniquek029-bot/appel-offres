// src/pages/JobDetail.jsx - Version corrigée
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

const JobDetail = () => {
  const { id } = useParams();
  const { user } = useAuth();
  const [offre, setOffre] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchOffre = async () => {
      try {
        const response = await api.get(`/offres/${id}/`);
        console.log('Offre reçue:', response.data);
        setOffre(response.data);
      } catch (err) {
        console.error('Erreur:', err);
        setError('Offre non trouvée');
      } finally {
        setLoading(false);
      }
    };
    fetchOffre();
  }, [id]);

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Non spécifiée';
    return new Date(dateStr).toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric' });
  };

  // ✅ CORRECTION: Utiliser le backend (port 8000) pour les PDF
  const getFullPdfUrl = () => {
    if (offre?.fichier_pdf_url) {
      // Construire l'URL complète vers le backend (port 8000)
      const backendUrl = `http://localhost:8000${offre.fichier_pdf_url}`;
      console.log('PDF URL backend:', backendUrl);
      return backendUrl;
    }
    if (offre?.url_tdr) {
      return offre.url_tdr;
    }
    return null;
  };

  const handleDownloadPDF = () => {
    const pdfUrl = getFullPdfUrl();
    console.log('PDF URL complète:', pdfUrl);
    
    if (pdfUrl) {
      window.open(pdfUrl, '_blank', 'noopener,noreferrer');
    } else {
      alert(' Aucun document PDF disponible pour cette offre');
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
        <Link to="/" className="btn btn-outline-primary">
        <i className="bi bi-arrow-left me-1"></i>
         Retour</Link>
      </div>
    );
  }

  const pdfUrl = getFullPdfUrl();
  const hasPdf = !!(pdfUrl);
  const isAdmin = user?.role === 'ADMIN';

  return (
    <div className="container py-4">
      <Link to="/" className="btn btn-outline-secondary mb-3">
      <i className="bi bi-arrow-left me-1"></i>
        Retour aux offres</Link>
      
      <div className="card shadow-sm">
        <div className="card-header text-white" style={{background: 'linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%)'}}>
          <h3 className="mb-0">{offre.titre}</h3>
        </div>
        
        <div className="card-body">
          {/* Infos générales */}
          <div className="row mb-4">
            <div className="col-md-6">
              <p><strong> Organisme :</strong> {offre.organisme}</p>
            </div>
            <div className="col-md-6">
              <p><strong> 
                <i className="bi bi-calendar-x me-1 text-muted"></i>
                Date de clôture :</strong> {formatDate(offre.date_cloture)}</p>
            </div>
            <div className="col-md-6">
              <p><strong>
                <i className="bi bi-calendar-check me-1 text-muted"></i>
                 Publication :</strong> {formatDate(offre.date_publication)}</p>
            </div>
            <div className="col-md-6">
              <i className="bi bi-globe-americas me-1 text-muted"></i>
              <p><strong> Pays :</strong> {offre.pays === 'BF' ? '🇧🇫 Burkina Faso' : offre.pays}</p>
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
          
          {/* SECTION TDR */}
          <div className="mb-4">
            {hasPdf ? (
              user ? (
                //  UTILISATEUR CONNECTÉ: afficher le bouton de téléchargement
                <div className="d-flex gap-3 flex-wrap align-items-center">
                  <button 
                    onClick={handleDownloadPDF} 
                    className="btn btn-lg fw-bold"
                    style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: 'linear-gradient(135deg, #D35400 0%, #F59E0B 100%)', border: 'none', color: 'white', boxShadow: '0 2px 8px rgba(211, 84, 0, 0.15)' }}
                  >
                    <i className="bi bi-download me-1"></i>
                    Télécharger TDR
                  </button>
                </div>
              ) : (
                // ❌ UTILISATEUR NON CONNECTÉ: afficher message avec lien de connexion
                <div className="alert alert-info d-flex flex-column gap-2">
                  <p className="mb-0">
                    <strong>Connexion requise</strong>
                  </p>
                  <p className="mb-0 text-muted">
                    <i className="bi bi-info-circle-fill me-1"></i>
                    Veuillez vous connecter pour télécharger le TDR de cette offre.
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
                Aucun document TDR n'est disponible pour cette offre.
              </div>
            )}
          </div>

          {/* Section Admin uniquement */}
          {isAdmin && pdfUrl && (
            <div className="mt-3 pt-2 text-muted small border-top">
              <span className="badge bg-light text-dark">
                PDF URL: {pdfUrl}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default JobDetail;