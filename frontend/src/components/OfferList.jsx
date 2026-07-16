// src/components/OfferList.jsx
import React, { useState, useEffect } from 'react';
import JobCard from './JobCard';
import { searchOffres } from '../services/api';

// ✅ AJOUT DE LA PROP 'layout' (valeurs possibles: 'grid' ou 'list')
const OfferList = ({ filters = {}, currentPage = 1, onPageChange, layout = 'list' }) => {
  const [offers, setOffers] = useState([]);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  
  const ITEMS_PER_PAGE = 4; // ✅ 4 offres par page pour les deux vues

  const fetchOffers = async () => {
    setLoading(true);
    setOffers([]);
    try {
      const params = { 
        page: currentPage, 
        page_size: ITEMS_PER_PAGE 
      };
    
      if (filters.keyword) params.keyword = filters.keyword;
      if (filters.pays) params.pays = filters.pays;
      if (filters.domaine) params.domaine = filters.domaine;
      if (filters.structure && filters.structure !== 'toutes' && filters.structure !== '') {
        params.structure = filters.structure;
      }
      if (filters.date_publication) params.date_publication = filters.date_publication;
      if (filters.max_days) params.max_days = filters.max_days;
    
      if (!filters.statut) {
        params.statut = 'Ouvert';
      } else {
        params.statut = filters.statut;
      }
    
      const { results, count } = await searchOffres(params);
      setOffers(Array.isArray(results) ? results : []);
      setTotalCount(count || 0);
      setTotalPages(Math.ceil((count || 0) / ITEMS_PER_PAGE));
    } catch (error) {
      console.error('❌ Erreur fetch offres:', error);
      setOffers([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOffers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPage, filters]);

  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages && typeof onPageChange === 'function') {
      onPageChange(page);
    }
  };

  const getPageNumbers = () => {
    const pages = [];
    const maxVisible = 10;
    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      if (currentPage <= 6) {
        for (let i = 1; i <= 8; i++) pages.push(i);
        pages.push('...');
        pages.push(totalPages);
      } else if (currentPage >= totalPages - 5) {
        pages.push(1);
        pages.push('...');
        for (let i = totalPages - 7; i <= totalPages; i++) pages.push(i);
      } else {
        pages.push(1);
        pages.push('...');
        for (let i = currentPage - 2; i <= currentPage + 2; i++) pages.push(i);
        pages.push('...');
        pages.push(totalPages);
      }
    }
    return pages;
  };

  const getActiveFiltersSummary = () => {
    const active = [];
    if (filters.keyword) active.push(`Mot-clé: "${filters.keyword}"`);
    if (filters.pays) active.push(`Pays: ${filters.pays}`);
    if (filters.domaine) active.push(`Domaine: ${filters.domaine}`);
    if (filters.structure && filters.structure !== 'toutes') active.push(`Structure: ${filters.structure}`);
    if (filters.date_publication) active.push(`Publié le: ${filters.date_publication}`);
    if (filters.max_days) active.push(`Expire dans: ${filters.max_days} jours`);
    return active;
  };

  const activeFilters = getActiveFiltersSummary();

  if (loading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Chargement des offres...</span>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h4 className="mb-0 fw-bold">{totalCount} offre(s) trouvée(s)</h4>
          {activeFilters.length > 0 && (
            <p className="text-muted small mb-0 mt-1">
              Filtres actifs : {activeFilters.join(' | ')}
            </p>
          )}
          {currentPage > 1 && (
            <span className="badge bg-secondary ms-2">Page {currentPage}</span>
          )}
        </div>
      </div>
      
      {/* ✅ LOGIQUE D'AFFICHAGE CONDITIONNELLE */}
      <div>
        {offers.length > 0 ? (
          layout === 'grid' ? (
            // 📐 MODE GRILLE (2 colonnes) pour la Page d'Accueil
            <div className="row g-3">
              {offers.map(offer => (
                <div className="col-md-6" key={offer.id}>
                  <JobCard offre={offer} />
                </div>
              ))}
            </div>
          ) : (
            // 📋 MODE LISTE (1 colonne verticale) pour la Page Offres
            <div>
              {offers.map(offer => (
                <div className="mb-3" key={offer.id}>
                  <JobCard offre={offer} />
                </div>
              ))}
            </div>
          )
        ) : (
          <div className="alert alert-info text-center py-4">
            {activeFilters.length > 0 
              ? 'Aucune offre ne correspond à vos filtres.'
              : 'Aucune offre disponible pour le moment.'}
          </div>
        )}
      </div>

      {/* ✅ PAGINATION */}
      {totalPages > 1 && (
        <nav className="mt-5" aria-label="Pagination des offres">
          <ul className="pagination justify-content-center flex-wrap">
            <li className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}>
              <button className="page-link" onClick={() => handlePageChange(currentPage - 1)}>
                ← Précédent
              </button>
            </li>
            {getPageNumbers().map((page, index) => (
              <li 
                key={index} 
                className={`page-item ${page === currentPage ? 'active' : ''} ${page === '...' ? 'disabled' : ''}`}
              >
                {page === '...' ? (
                  <span className="page-link">…</span>
                ) : (
                  <button className="page-link" onClick={() => handlePageChange(page)}>
                    {page}
                  </button>
                )}
              </li>
            ))}
            <li className={`page-item ${currentPage === totalPages ? 'disabled' : ''}`}>
              <button className="page-link" onClick={() => handlePageChange(currentPage + 1)}>
                Suivant →
              </button>
            </li>
          </ul>
        </nav>
      )}
    </div>
  );
};

export default OfferList;