// src/pages/Offres.jsx
import React from 'react';
import { useSearchParams } from 'react-router-dom';
import SearchFilters from '../components/SearchFilters';
import VerticalFilters from '../components/VerticalFilters';
import OfferList from '../components/OfferList';

const Offres = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  // ✅ Restaurer TOUS les paramètres depuis l'URL (filtres + page)
  const filters = {
    keyword: searchParams.get('keyword') || '',
    pays: searchParams.get('pays') || '',
    domaine: searchParams.get('domaine') || '',
    structure: searchParams.get('structure') || '',
    date_publication: searchParams.get('date_publication') || '',
    max_days: searchParams.get('max_days') || '',
  };

  // ✅ Page courante depuis l'URL (défaut = 1)
  const currentPage = parseInt(searchParams.get('page') || '1', 10);

  // ✅ Mettre à jour l'URL (filtres + page)
  const updateFilters = (newFilters, newPage = 1) => {
    const params = new URLSearchParams();
    
    // Ajouter les filtres
    Object.entries(newFilters).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });
    
    // Ajouter la page (si > 1)
    if (newPage > 1) {
      params.set('page', newPage.toString());
    }
    
    setSearchParams(params);
  };

  // ✅ Callback pour le changement de page
  const handlePageChange = (page) => {
    updateFilters(filters, page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // ✅ Callback pour le changement de filtres (reset à page 1)
  const handleFilterChange = (newFilters) => {
    updateFilters(newFilters, 1);
  };

  return (
    <div>
      <SearchFilters 
        onSearch={handleFilterChange}
        initialValues={filters}
      />

      <div className="container-fluid py-3">
        <div className="row">
          <div className="col-md-3">
            <VerticalFilters 
              onFilterChange={handleFilterChange}
              initialValues={filters}
            />
          </div>

          <div className="col-md-9">
            <OfferList 
              filters={filters}
              currentPage={currentPage}
              onPageChange={handlePageChange}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Offres;