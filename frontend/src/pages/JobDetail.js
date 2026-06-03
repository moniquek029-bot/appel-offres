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
      alert('❌ Aucun document PDF disponible pour cette offre');
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
        <Link to="/" className="btn btn-outline-primary">← Retour</Link>
      </div>
    );
  }

  const pdfUrl = getFullPdfUrl();
  const hasPdf = !!(pdfUrl);
  const isAdmin = user?.role === 'ADMIN';

  return (
    <div className="container py-4">
      <Link to="/" className="btn btn-outline-secondary mb-3">← Retour aux offres</Link>
      
      <div className="card shadow-sm">
        <div className="card-header bg-primary text-white">
          <h3 className="mb-0">{offre.titre}</h3>
        </div>
        
        <div className="card-body">
          {/* Infos générales */}
          <div className="row mb-4">
            <div className="col-md-6">
              <p><strong>🏢 Organisme :</strong> {offre.organisme}</p>
            </div>
            <div className="col-md-6">
              <p><strong>📅 Date de clôture :</strong> {formatDate(offre.date_cloture)}</p>
            </div>
            <div className="col-md-6">
              <p><strong>📆 Publication :</strong> {formatDate(offre.date_publication)}</p>
            </div>
            <div className="col-md-6">
              <p><strong>🌍 Pays :</strong> {offre.pays === 'BF' ? '🇧🇫 Burkina Faso' : offre.pays}</p>
            </div>
          </div>
          
          {/* Description */}
          <h5 className="text-primary mb-3">📋 Description</h5>
          <div className="mb-4 p-3 bg-light rounded" style={{ whiteSpace: 'pre-line' }}>
            {offre.description || 'Aucune description disponible.'}
          </div>
          
          <hr />
          
          {/* SECTION TDR */}
          <div className="mb-4">
            <h5 className="text-primary mb-3">📄 Télécharger le TDR</h5>
            
            {hasPdf ? (
              <div className="d-flex gap-3 flex-wrap align-items-center">
                <button 
                  onClick={handleDownloadPDF} 
                  className="btn btn-success btn-lg"
                  style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}
                >
                  📥 Télécharger le PDF
                </button>
              </div>
            ) : (
              <div className="alert alert-warning">
                ⚠️ Aucun document TDR n'est disponible pour cette offre.
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