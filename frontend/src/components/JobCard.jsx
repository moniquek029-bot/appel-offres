// src/components/JobCard.jsx
import React from 'react';
import { Link } from 'react-router-dom';

const JobCard = ({ offre }) => {
  // 🛡️ Protection : si offre est null/undefined, on n'affiche rien
  if (!offre || !offre.id) return null;

  // Formatage de date
  const formatDate = (dateStr) => {
    if (!dateStr) return 'Non spécifiée';
    return new Date(dateStr).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  // Calcul des jours restants
  const daysLeft = offre.date_cloture 
    ? Math.ceil((new Date(offre.date_cloture) - new Date()) / (1000 * 60 * 60 * 24))
    : null;

  // ✅ LE RETURN PRINCIPAL (à l'intérieur de la fonction JobCard)
  return (
    <div className="card h-100 border-0 shadow-sm hover-shadow">
      <div className="card-body">
        
        {/* Statut + Pays */}
        <div className="d-flex justify-content-between align-items-start mb-2">
          <span className={`badge bg-${offre.statut === 'Ouvert' ? 'success' : 'secondary'}`}>
            {offre.statut}
          </span>
          <small className="text-muted">
            {offre.pays === 'BF' && '🇧🇫 '} {offre.pays}
          </small>
        </div>

        {/* Titre + Organisme */}
        <h5 className="card-title text-primary mb-1">{offre.titre}</h5>
        <p className="text-muted small mb-2">{offre.organisme}</p>

        {/* Description courte */}
        <p className="card-text small text-secondary mb-3">
          {offre.description?.substring(0, 120)}...
        </p>

        {/* Métadonnées */}
        <div className="d-flex justify-content-between align-items-center small text-muted mb-3">
          <span>Publiée : {formatDate(offre.date_publication)}</span>
          {offre.source_origine && (
            <span className="badge bg-light text-dark border">
              {offre.source_origine.nom?.substring(0, 15)}...
            </span>
          )}
        </div>

        {/* Deadline + Actions */}
        <div className="d-flex justify-content-between align-items-center pt-2 border-top">
          <small className={daysLeft <= 7 ? 'text-danger fw-bold' : 'text-muted'}>
            Clôture : {formatDate(offre.date_cloture)}
            {daysLeft > 0 && daysLeft <= 7 && <span className="ms-1">({daysLeft}j)</span>}
          </small>
          
          <div className="d-flex gap-2">
            {/*  BOUTON TDR : Conditionnel */}
            {offre.url_tdr ? (
              <a 
                href={offre.url_tdr} 
                target="_blank" 
                rel="noopener noreferrer"
                className="btn btn-sm btn-primary"
                title="Consulter le TDR sur le site officiel"
              >
               Voir le TDR
              </a>
            ) : (
              <button 
                className="btn btn-sm btn-outline-secondary"
                disabled
                title="Connectez-vous pour accéder au lien officiel"
              >
                TDR
              </button>
            )}
            
            {/* Bouton détails */}
            <Link to={`/offres/${offre.id}`} className="btn btn-sm btn-outline-secondary">
              📄 Détails
            </Link>
          </div>
        </div>
        
      </div>
    </div>
  );
}; // ← ✅ Fermeture CORRECTE de la fonction JobCard (APRÈS le return)

export default JobCard;