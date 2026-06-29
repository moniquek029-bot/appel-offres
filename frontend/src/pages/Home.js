// src/pages/Home.jsx
import React from 'react';
import { useSearchParams } from 'react-router-dom';
import SearchFilters from '../components/SearchFilters';
import VerticalFilters from '../components/VerticalFilters';
import OfferList from '../components/OfferList';

const Home = () => {
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

  return (
    <div>
      {/* Hero */}
      {/*<div className="bg-primary text-white py-5 text-center">
        <h1 className="display-5 fw-bold">Trouvez votre prochain appel d'offres</h1>
        <p className="lead">Des milliers d'opportunités à travers l'Afrique et le monde</p>
      </div>*/}

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

export default Home;