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
  
  const isAdmin = user?.role === 'ADMIN';
  
  const isRecent = (dateScraping) => {
    if (!dateScraping) return false;
    const now = new Date();
    const scrapingDate = new Date(dateScraping);
    const diffHours = (now - scrapingDate) / (1000 * 60 * 60);
    return diffHours < 24;
  };

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

  const handleDownloadPDF = () => {
    if (downloading) return;
    
    setDownloading(true);
    
    try {
      if (offre.fichier_pdf_url) {
        window.open(offre.fichier_pdf_url, '_blank', 'noopener,noreferrer');
      } 
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

  const handleDownload = handleDownloadPDF;

  const hasPdf = !!(offre.fichier_pdf_url || offre.url_tdr);

  return (
    // ✅ AJOUT : h-100 pour que toutes les cartes aient la même hauteur dans la grille
    <div className="card border-0 shadow-sm hover-shadow mb-3 h-100">
      <div className="card-body p-3">
        {/* Badges */}
        <div className="d-flex align-items-center gap-2 mb-2 flex-wrap">
          <span className="badge bg-primary bg-opacity-10 text-primary px-2 py-1 small"> Appel d'offres</span>
          
          {offre.statut === 'Ouvert' && <span className="badge bg-success small">Ouvert</span>}
          
          {isRecent(offre.date_scraping) && (
            <span className="badge bg-warning text-dark small">
               Nouveau
            </span>
          )}
          
          {isAdmin && offre.mode_acquisition === 'MANUEL' && (
            <span className="badge bg-info text-white small">Publié par admin</span>
          )}
          
          {isAdmin && offre.mode_acquisition === 'AUTO' && (
            <span className="badge bg-secondary text-white small">Scrapé</span>
          )}
        </div>

        {/* Titre */}
        <h6 className="card-title fw-bold mb-2">
          <Link to={`/offres/${offre.id}`} className="text-dark text-decoration-none">
            {offre.titre}
          </Link>
        </h6>

        {/* Description - tronquée plus court pour 2 colonnes */}
        <p className="card-text text-secondary small mb-3">
          {offre.description?.substring(0, 120)}...
        </p>

        {/* Infos */}
        <div className="d-flex flex-wrap align-items-center gap-2 small text-muted mb-3">
          <span><i className="bi bi-building me-1"></i> {offre.organisme}</span>
        </div>

        <div className="d-flex flex-wrap align-items-center gap-2 small text-muted mb-3">
          <span><i className="bi bi-clock me-1"></i> {formatDate(offre.date_publication)}</span>
          
          {offre.date_scraping && (
            <span className="text-info" title={`Collecté le ${formatScrapingDate(offre.date_scraping)}`}>
              <i className="bi bi-download me-1"></i> 
              {formatDate(offre.date_scraping)}
            </span>
          )}
        </div>

        <div className="mb-3">
          <span className={daysLeft !== null && daysLeft <= 7 ? 'text-danger fw-bold small' : 'small text-muted'}>
            <i className="bi bi-calendar-x me-1"></i> 
            Clôture: {offre.date_cloture ? new Date(offre.date_cloture).toLocaleDateString('fr-FR') : 'Non spécifiée'}
            {daysLeft !== null && daysLeft > 0 && daysLeft <= 30 && <span className="ms-1">({daysLeft}j)</span>}
            {daysLeft !== null && daysLeft <= 0 && daysLeft > -30 && <span className="ms-1 text-danger">(Expiré)</span>}
          </span>
        </div>

        {/* Bouton Détails */}
        <Link to={`/offres/${offre.id}`} className="btn btn-outline-primary btn-sm w-100">
          <i className="bi bi-eye me-1"></i>
          Voir détails
        </Link>
      </div>
    </div>
  );
};

export default JobCard;