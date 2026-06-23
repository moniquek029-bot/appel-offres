// src/components/JobCard.jsx
import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const JobCard = ({ offre }) => {
  const { user } = useAuth();
  const [downloading, setDownloading] = useState(false);
  const isMounted = useRef(true);
  const downloadTimeoutRef = useRef(null);
  
  // Vérifier si l'utilisateur est admin
  const isAdmin = user?.role === 'ADMIN';
  
  // ✅ NOUVEAU: Fonction pour vérifier si l'offre est récente (< 24h)
  const isRecent = (dateScraping) => {
    if (!dateScraping) return false;
    const now = new Date();
    const scrapingDate = new Date(dateScraping);
    const diffHours = (now - scrapingDate) / (1000 * 60 * 60);
    return diffHours < 24; // Moins de 24 heures
  };

  // ✅ NOUVEAU: Fonction pour formater la date de scraping
  const formatScrapingDate = (dateStr) => {
    if (!dateStr) return null;
    const date = new Date(dateStr);
    return date.toLocaleString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  
  // Nettoyage au démontage du composant
  useEffect(() => {
    isMounted.current = true;
    return () => {
      isMounted.current = false;
      if (downloadTimeoutRef.current) {
        clearTimeout(downloadTimeoutRef.current);
      }
    };
  }, []);
  
  if (!offre || !offre.id) return null;

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Non spécifiée';
    const date = new Date(dateStr);
    const now = new Date();
    const diffHours = Math.floor((now - date) / (1000 * 60 * 60));
    if (diffHours < 24) return `il y a ${diffHours} heure${diffHours > 1 ? 's' : ''}`;
    return date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
  };

  const daysLeft = offre.date_cloture 
    ? Math.ceil((new Date(offre.date_cloture) - new Date()) / (1000 * 60 * 60 * 24))
    : null;

  // ✅ CORRECTION: Utiliser fichier_pdf_url au lieu de fichier_pdf
  const handleDownloadPDF = () => {
    if (downloading) return;
    
    setDownloading(true);
    
    try {
      // Priorité au PDF local
      if (offre.fichier_pdf_url) {
        window.open(offre.fichier_pdf_url, '_blank', 'noopener,noreferrer');
      } 
      // Sinon URL externe
      else if (offre.url_tdr) {
        window.open(offre.url_tdr, '_blank', 'noopener,noreferrer');
      } 
      else {
        alert(' Aucun PDF disponible pour cette offre');
      }
    } catch (err) {
      console.error('Erreur:', err);
      alert(' Impossible d\'ouvrir le PDF');
    } finally {
      downloadTimeoutRef.current = setTimeout(() => {
        if (isMounted.current) {
          setDownloading(false);
        }
      }, 1000);
    }
  };

  // Version avec appel API (fallback)
  const handleDownloadPDFWithAPI = async () => {
    if (downloading) return;
    
    setDownloading(true);
    
    try {
      const response = await api.get(`/offres/${offre.id}/download-pdf/`, { 
        responseType: 'blob'
      });
      
      if (!isMounted.current) return;
      
      const textResponse = await response.data.text();
      
      try {
        const jsonData = JSON.parse(textResponse);
        if (jsonData.redirect_url) {
          window.open(jsonData.redirect_url, '_blank', 'noopener,noreferrer');
        } else if (jsonData.error) {
          alert(` ${jsonData.error}`);
        }
      } catch {
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `TDR_${offre.id}.pdf`);
        document.body.appendChild(link);
        link.click();
        
        setTimeout(() => {
          if (link.parentNode) {
            link.parentNode.removeChild(link);
          }
          window.URL.revokeObjectURL(url);
        }, 100);
      }
    } catch (err) {
      console.error('Erreur téléchargement:', err);
      if (isMounted.current) {
        if (offre.fichier_pdf_url) {
          window.open(offre.fichier_pdf_url, '_blank', 'noopener,noreferrer');
        } else if (offre.url_tdr) {
          window.open(offre.url_tdr, '_blank', 'noopener,noreferrer');
        } else {
          alert(' Impossible de télécharger le PDF');
        }
      }
    } finally {
      if (isMounted.current) {
        downloadTimeoutRef.current = setTimeout(() => {
          if (isMounted.current) {
            setDownloading(false);
          }
        }, 1000);
      }
    }
  };

  // Utiliser la version simple par défaut
  const handleDownload = handleDownloadPDF;

  // ✅ CORRECTION: Vérifier correctement la présence d'un PDF
  const hasPdf = !!(offre.fichier_pdf_url || offre.url_tdr);
  const isPdfVisible = user && hasPdf;

  return (
    <div className="card border-0 shadow-sm hover-shadow mb-3">
      <div className="card-body p-4">
        <div className="row">
          <div className="col-md-8">
            {/* Badges */}
            <div className="d-flex align-items-center gap-2 mb-2 flex-wrap">
              <span className="badge bg-primary bg-opacity-10 text-primary px-3 py-2"> Appel d'offres</span>
              
              {offre.statut === 'Ouvert' && <span className="badge bg-success">Ouvert</span>}
              
              {/* ✅ NOUVEAU: Badge "Nouveau" pour les offres récentes */}
              {isRecent(offre.date_scraping) && (
                <span className="badge bg-warning text-dark">
                   Nouveau
                </span>
              )}
              
              {isAdmin && offre.mode_acquisition === 'MANUEL' && (
                <span className="badge bg-info text-white">Publié par admin</span>
              )}
              
              {isAdmin && offre.mode_acquisition === 'AUTO' && (
                <span className="badge bg-secondary text-white">Scrapé</span>
              )}
            </div>

            {/* Titre */}
            <h5 className="card-title fw-bold mb-2">
              <Link to={`/offres/${offre.id}`} className="text-dark text-decoration-none">
                {offre.titre}
              </Link>
            </h5>

            {/* Description */}
            <p className="card-text text-secondary small mb-3">
              {offre.description?.substring(0, 200)}...
              {offre.description?.length > 200 && (
                <Link to={`/offres/${offre.id}`} className="text-primary ms-1">
                  <i className="bi bi-arrow-right-circle me-1"></i>
                  Lire la suite
                </Link>
              )}
            </p>

            {/* Infos */}
            <div className="d-flex flex-wrap align-items-center gap-3 small text-muted">
              <span><i className="bi bi-building me-1"></i> {offre.organisme}</span>
              <span><i className="bi bi-clock me-1"></i> {formatDate(offre.date_publication)}</span>
              
              {/* ✅ NOUVEAU: Affichage de la date de scraping */}
              {offre.date_scraping && (
                <span className="text-info" title={`Collecté le ${formatScrapingDate(offre.date_scraping)}`}>
                  <i className="bi bi-download me-1"></i> 
                  Collecté {formatDate(offre.date_scraping)}
                </span>
              )}
              
              <span className={daysLeft !== null && daysLeft <= 7 ? 'text-danger fw-bold' : ''}>
                <i className="bi bi-calendar-x me-1"></i> Clôture: {offre.date_cloture ? new Date(offre.date_cloture).toLocaleDateString('fr-FR') : 'Non spécifiée'}
                {daysLeft !== null && daysLeft > 0 && daysLeft <= 30 && <span className="ms-1">({daysLeft}j)</span>}
                {daysLeft !== null && daysLeft <= 0 && daysLeft > -30 && <span className="ms-1 text-danger">(Expiré)</span>}
              </span>
            </div>
          </div>

          <div className="col-md-4 text-end mt-3 mt-md-0">
            <div className="d-flex flex-column gap-2">
              {/* Bouton Détails */}
              <Link to={`/offres/${offre.id}`} className="btn btn-outline-primary">
                <i className="bi bi-eye me-1"></i>
                 Voir détails
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobCard;