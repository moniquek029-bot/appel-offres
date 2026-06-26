// src/pages/Home.jsx
import React, { useState, useEffect } from 'react';
import JobCard from '../components/JobCard';
import VerticalFilters from '../components/VerticalFilters';
import SearchBar from '../components/SearchBar';
import { searchOffres } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { buildMultilingualSearch } from '../utils/multilingualKeywords';


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
    date_publication: '',
    date_cloture: '',
  });

  // src/pages/Home.jsx

  // ✅ AJOUTER CET IMPORT EN HAUT DU FICHIER (avec les autres imports)

  const fetchOffres = async (page = 1, newFilters = null) => {
    try {
      setLoading(true);
      setError(null);
    
      const currentFilters = newFilters || filters;
    
      // ✅ Utiliser la recherche multilingue
      const searchKeyword = currentFilters.keyword || '';
      const multilingualQuery = buildMultilingualSearch(searchKeyword);
    
      // ✅ Construction DIRECTE des paramètres pour l'API
      const apiParams = {
        keyword: multilingualQuery || searchKeyword, // ✅ Utiliser la requête multilingue
        pays: currentFilters.pays,
        max_days: currentFilters.max_days,
        domaine: currentFilters.domaine,
        structure: currentFilters.structure || '', // ✅ Structure peut être vide
        page 
      };
    
      // ✅ Envoyer date_publication DIRECTEMENT (pas de conversion)
      if (currentFilters.date_publication) {
        apiParams.date_publication = currentFilters.date_publication;
        console.log(' Date publication envoyée:', currentFilters.date_publication);
      }
    
      // ✅ Envoyer date_cloture DIRECTEMENT
      if (currentFilters.date_cloture) {
        apiParams.date_cloture = currentFilters.date_cloture;
        console.log(' Date clôture envoyée:', currentFilters.date_cloture);
      }
    
      console.log(' Paramètres envoyés à l API:', apiParams);
    
      const response = await searchOffres(apiParams);
    
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
      console.error('❌ Erreur API:', err);
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
    const updatedFilters = { 
      ...filters, 
      ...newFilters
    };
    
    console.log('🎯 Nouveaux filtres reçus:', newFilters);
    console.log('🔄 Filtres mis à jour:', updatedFilters);
    
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
      <SearchBar onSearch={handleSearch} />

      <div className="container py-4">
        <div className="row g-4">
          <div className="col-lg-4 col-md-4">
            <div className="sticky-top" style={{ top: '20px', zIndex: 1000 }}>
              <VerticalFilters onFilterChange={handleFilterChange} />
            </div>
          </div>
          
          <div className="col-lg-8 col-md-8">
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
                  const resetFilters = { 
                    keyword: '', 
                    pays: '', 
                    max_days: '', 
                    domaine: '', 
                    structure: '',
                    date_publication: '',
                    date_cloture: ''
                  };
                  setFilters(resetFilters);
                  fetchOffres(1, resetFilters);
                }}>
                  <i className="bi bi-arrow-right me-1"></i>
                  Afficher toutes les offres
                </button>
              </div>
            )}

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