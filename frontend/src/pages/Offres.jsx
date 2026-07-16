// src/pages/Offres.jsx
import React from 'react';
import { useSearchParams } from 'react-router-dom';
import OfferList from '../components/OfferList';

const Offres = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const filters = {
    keyword: searchParams.get('keyword') || '',
    pays: searchParams.get('pays') || '',
    domaine: searchParams.get('domaine') || '',
    structure: searchParams.get('structure') || '',
    date_publication: searchParams.get('date_publication') || '',
    max_days: searchParams.get('max_days') || '',
  };

  const currentPage = parseInt(searchParams.get('page') || '1', 10);

  const updateFilters = (newFilters, newPage = 1) => {
    const params = new URLSearchParams();
    Object.entries(newFilters).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });
    if (newPage > 1) params.set('page', newPage.toString());
    setSearchParams(params);
  };

  const handlePageChange = (page) => {
    updateFilters(filters, page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleFilterChange = (newFilters) => {
    updateFilters(newFilters, 1);
  };

  return (
    <div>
      {/* ✅ BANNIÈRE SIMPLE */}
      <div className="bg-light border-bottom py-3">
        <div className="container">
          <div className="d-flex justify-content-between align-items-center">
            {/*<div>
              <h2 className="mb-0 fw-bold">
                <i className="bi bi-briefcase-fill text-primary me-2"></i>
                Tous les appels d'offres
              </h2>
              <p className="text-muted small mb-0">
                {currentPage === 1 ? 'Liste des offres disponibles' : `Page ${currentPage}`}
              </p>
            </div>*/}
          </div>
        </div>
      </div>

      {/* ✅ UNIQUEMENT LA LISTE DES OFFRES - PLEINE LARGEUR */}
      <div className="container py-3">
        <OfferList 
          filters={filters}
          currentPage={currentPage}
          onPageChange={handlePageChange}
          layout="list"
        />
      </div>
    </div>
  );
};

export default Offres;