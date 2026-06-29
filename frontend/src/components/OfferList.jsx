// src/components/OfferList.jsx
import React, { useState, useEffect } from 'react';
import JobCard from './JobCard';
import { searchOffres } from '../services/api';

const OfferList = ({ filters = {}, currentPage = 1, onPageChange }) => {
  const [offers, setOffers] = useState([]);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  
  // ✅ MODIFICATION : 6 offres par page (3 lignes × 2 colonnes)
  const ITEMS_PER_PAGE = 4;

  useEffect(() => {
    fetchOffers();
  }, [currentPage, filters]);

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
      if (filters.structure) params.structure = filters.structure;
      if (filters.date_publication) params.date_publication = filters.date_publication;
      if (filters.max_days) params.max_days = filters.max_days;

      const { results, count } = await searchOffres(params);
      setOffers(Array.isArray(results) ? results : []);
      setTotalCount(count || 0);
      setTotalPages(Math.ceil((count || 0) / ITEMS_PER_PAGE));
    } catch (error) {
      console.error('Erreur lors de la récupération des offres:', error);
      setOffers([]);
    } finally {
      setLoading(false);
    }
  };

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
    if (filters.structure) active.push(`Structure: ${filters.structure}`);
    if (filters.date_publication) active.push(`Publié le: ${filters.date_publication}`);
    if (filters.max_days) active.push(`Expire dans: ${filters.max_days} jours`);
    return active;
  };

  const activeFilters = getActiveFiltersSummary();

  if (loading) {
    return (
      <div className="container py-5 text-center">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Chargement des offres en cours...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="mb-1">Appels d'offres disponibles</h2>
          <p className="text-muted small mb-0">
            {totalCount} offre(s) trouvée(s)
            {activeFilters.length > 0 && (
              <span className="ms-2">
                • Filtres actifs : {activeFilters.join(' | ')}
              </span>
            )}
            {currentPage > 1 && (
              <span className="ms-2 badge bg-secondary">
                Page {currentPage}
              </span>
            )}
          </p>
        </div>
        <button 
          className="btn btn-outline-primary btn-sm d-flex align-items-center gap-2"
          onClick={fetchOffers}
          title="Rafraîchir les données"
        >
          Actualiser la liste
        </button>
      </div>
      
      {/* ✅ MODIFICATION : Grille 2 colonnes (col-md-6) */}
      <div className="row g-3">
        {offers.length > 0 ? (
          offers.map(offer => (
            // ✅ MODIFICATION : col-12 → col-md-6 (2 par ligne sur desktop, 1 sur mobile)
            <div className="col-12 col-md-6" key={offer.id}>
              <JobCard offre={offer} />
            </div>
          ))
        ) : (
          <div className="col-12">
            <div className="alert alert-info text-center py-4">
              {activeFilters.length > 0 
                ? 'Aucune offre ne correspond à vos filtres. Essayez de les modifier.'
                : 'Aucune offre disponible pour le moment. Lancez un scraping depuis l\'administration.'}
            </div>
          </div>
        )}
      </div>

      {/* Pagination */}
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
                  <span className="page-link">...</span>
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