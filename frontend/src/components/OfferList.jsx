// src/components/OfferList.jsx
import React, { useState, useEffect } from 'react';
import JobCard from './JobCard';
import { searchOffres } from '../services/api';

const OfferList = () => {
  const [offers, setOffers] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  
  const ITEMS_PER_PAGE = 10; // 10 offres par page

  useEffect(() => {
    fetchOffers();
  }, [currentPage]);

  const fetchOffers = async () => {
    setLoading(true);
    try {
      const { results, count } = await searchOffres({ page: currentPage, page_size: ITEMS_PER_PAGE });
      setOffers(Array.isArray(results) ? results : []);
      setTotalCount(count || 0);
      setTotalPages(Math.ceil((count || 0) / ITEMS_PER_PAGE));
    } catch (error) {
      console.error('Erreur:', error);
      setOffers([]);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  // Générer les numéros de page à afficher
  const getPageNumbers = () => {
    const pages = [];
    const maxVisible = 10; // Nombre maximum de pages visibles
    
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
    <div className="container py-4">
      <h2 className="mb-4">Appels d'offres disponibles</h2>
      <p className="text-muted small mb-3">{totalCount} offre(s) au total</p>
      
      <div className="row g-3">
        {offers.length > 0 ? (
          offers.map(offer => (
            <div className="col-12" key={offer.id}>
              <JobCard offre={offer} />
            </div>
          ))
        ) : (
          <div className="col-12">
            <div className="alert alert-info text-center">
              Aucune offre disponible pour le moment.
            </div>
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <nav className="mt-5" aria-label="Pagination des offres">
          <ul className="pagination justify-content-center flex-wrap">
            {/* Page précédente */}
            <li className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}>
              <button className="page-link" onClick={() => handlePageChange(currentPage - 1)}>
                ← Précédent
              </button>
            </li>
            
            {/* Numéros de page */}
            {getPageNumbers().map((page, index) => (
              <li key={index} className={`page-item ${page === currentPage ? 'active' : ''} ${page === '...' ? 'disabled' : ''}`}>
                {page === '...' ? (
                  <span className="page-link">...</span>
                ) : (
                  <button className="page-link" onClick={() => handlePageChange(page)}>
                    {page}
                  </button>
                )}
              </li>
            ))}
            
            {/* Page suivante */}
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