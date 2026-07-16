import React from 'react';
import { useSearchParams } from 'react-router-dom';
import SearchFilters from '../components/SearchFilters';
import VerticalFilters from '../components/VerticalFilters';
import OfferList from '../components/OfferList';

const Home = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  // ✅ On force le statut à 'Ouvert' par défaut pour ne voir que les offres actives
  const filters = {
    keyword: searchParams.get('keyword') || '',
    pays: searchParams.get('pays') || '',
    domaine: searchParams.get('domaine') || '',
    structure: searchParams.get('structure') || '',
    statut: searchParams.get('statut') || 'Ouvert', // ✅ Ajouté
    date_publication: searchParams.get('date_publication') || '',
    max_days: searchParams.get('max_days') || '',
  };

  const currentPage = parseInt(searchParams.get('page') || '1', 10);

  const updateFilters = (newFilters, newPage = 1) => {
    const params = new URLSearchParams();
    Object.entries(newFilters).forEach(([key, value]) => {
      // ✅ On ignore les valeurs vides ou "toutes" pour ne pas polluer l'URL
      if (value && value !== '' && value.toLowerCase() !== 'toutes') {
        params.set(key, value);
      }
    });
    if (newPage > 1) {
      params.set('page', newPage.toString());
    }
    setSearchParams(params);
  };

  const handlePageChange = (page) => {
    updateFilters(filters, page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleFilterChange = (newFilters) => {
    updateFilters(newFilters, 1);
  };

  // ✅ Débogage : voir ce qui est envoyé à OfferList
  console.log(' Home.jsx - Filtres actuels:', filters);
  console.log(' Home.jsx - Page actuelle:', currentPage);

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
              layout="grid" 
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;