// src/pages/Home.jsx
import React, { useState, useEffect } from 'react';
import JobCard from '../components/JobCard';
import VerticalFilters from '../components/VerticalFilters';
import SearchBar from '../components/SearchBar';
import { searchOffres } from '../services/api';
import { useAuth } from '../context/AuthContext';

const Home = () => {
  const { user } = useAuth();
  const [offres, setOffres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [filters, setFilters] = useState({
    keyword: '',
    pays: '',
    max_days: '',
    domaine: '',
    structure: '',
  });

  const fetchOffres = async (page = 1, newFilters = null) => {
    try {
      setLoading(true);
      setError(null);
      
      const currentFilters = newFilters || filters;
      const response = await searchOffres({ 
        keyword: currentFilters.keyword,
        pays: currentFilters.pays,
        max_days: currentFilters.max_days,
        domaine: currentFilters.domaine,
        structure: currentFilters.structure,
        date_debut: currentFilters.date_debut,
        date_fin: currentFilters.date_fin,
        page 
      });
      
      setOffres(response.results || []);
      setTotalCount(response.count || 0);
      
      const itemsPerPage = 10;
      const pages = Math.ceil((response.count || 0) / itemsPerPage);
      setTotalPages(pages);
      setCurrentPage(page);
      
      if (newFilters) {
        setFilters(newFilters);
      }
    } catch (err) {
      console.error('Erreur API:', err);
      setError('Impossible de charger les offres.');
      setOffres([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOffres();
  }, []);

  const handleSearch = (searchKeyword) => {
    const newFilters = { ...filters, keyword: searchKeyword };
    setFilters(newFilters);
    fetchOffres(1, newFilters);
  };

  const handleFilterChange = (newFilters) => {
    const updatedFilters = { ...filters, keyword: filters.keyword, ...newFilters };
    setFilters(updatedFilters);
    fetchOffres(1, updatedFilters);
  };

  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages) {
      fetchOffres(page);
      window.scrollTo({ top: 0, behavior: 'smooth' });
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

  return (
    <div className="min-vh-100 d-flex flex-column bg-light">
      

      {/* Barre de recherche en haut */}
      <SearchBar onSearch={handleSearch} />

      {/* Layout: Filtres (gauche) + Résultats (droite) - EN FLEX ROW */}
      <div className="container py-4">
        <div className="row g-4">
          
          {/* Colonne des filtres - 1/4 de largeur */}
          <div className="col-lg-4 col-md-4">
            <div className="sticky-top" style={{ top: '20px'  ,sIndex:1000}}>
              <VerticalFilters onFilterChange={handleFilterChange} />
            </div>
          </div>
          
          {/* Colonne des résultats - 3/4 de largeur */}
          <div className="col-lg-8 col-md-8">
            
            {/* En-tête des résultats */}
            <div className="d-flex justify-content-between align-items-center mb-4">
              <div>
                <h4 className="mb-0 fw-bold">Appels d'offres disponibles</h4>
                <p className="text-muted small mb-0 mt-1">
                  {totalCount} offre(s) trouvée(s) - Page {currentPage} / {totalPages}
                </p>
              </div>
            </div>

            {error && (
              <div className="alert alert-danger alert-dismissible fade show">
                 {error}
                <button type="button" className="btn-close" onClick={() => { setError(null); fetchOffres(1); }}></button>
              </div>
            )}

            {loading ? (
              <div className="text-center py-5">
                <div className="spinner-border text-primary" role="status">
                  <span className="visually-hidden">Chargement...</span>
                </div>
              </div>
            ) : offres.length > 0 ? (
              <>
                {offres.map((offre) => (
                  <JobCard key={offre.id} offre={offre} />
                ))}
              </>
            ) : (
              <div className="alert alert-info text-center py-5">
                <h5 className="mt-3">Aucune offre trouvée</h5>
                <button className="btn btn-outline-primary mt-2" onClick={() => {
                  const resetFilters = { keyword: '', pays: '', max_days: '', domaine: '', structure: '' };
                  setFilters(resetFilters);
                  fetchOffres(1, resetFilters);
                }}>
                  <i className="bi bi-arrow-right me-1"></i>
                  Afficher toutes les offres
                </button>
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <nav className="mt-5" aria-label="Pagination des offres">
                <ul className="pagination justify-content-center flex-wrap">
                  <li className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}>
                    <button className="page-link" onClick={() => handlePageChange(currentPage - 1)}>
                      <i className="bi bi-arrow-left me-1"></i>
                      Précédent
                    </button>
                  </li>
                  
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
                  
                  <li className={`page-item ${currentPage === totalPages ? 'disabled' : ''}`}>
                    <button className="page-link" onClick={() => handlePageChange(currentPage + 1)}>
                      <i className="bi bi-arrow-right me-1"></i>
                      Suivant 

                    </button>
                  </li>
                </ul>
              </nav>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;