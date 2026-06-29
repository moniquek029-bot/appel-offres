// src/pages/Home.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import SearchFilters from '../components/SearchFilters';
import VerticalFilters from '../components/VerticalFilters';
import JobCard from '../components/JobCard';
import { searchOffres } from '../services/api';

const Home = () => {
  const navigate = useNavigate();
  
  // ✅ ÉTAT DES OFFRES
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  
  // ✅ ÉTAT DES FILTRES (unifié pour les deux composants)
  const [filters, setFilters] = useState({
    keyword: '',
    pays: '',
    domaine: '',
    structure: '',
    date_publication: '',
    max_days: ''
  });

  const ITEMS_PER_PAGE = 10;

  // =============================================================================
  // FONCTION 1 : Récupérer les offres avec les filtres actuels
  // =============================================================================
  const fetchOffers = async (page = 1, currentFilters = filters) => {
    setLoading(true);
    
    try {
      console.log('🔍 Paramètres envoyés à l\'API:', currentFilters);
      
      const { results, count } = await searchOffres({
        page: page,
        page_size: ITEMS_PER_PAGE,
        ...currentFilters  // ✅ Envoie tous les filtres
      });
      
      console.log('✅ Réponse API:', { results: results?.length, count });
      
      setOffers(Array.isArray(results) ? results : []);
      setTotalCount(count || 0);
      setTotalPages(Math.ceil((count || 0) / ITEMS_PER_PAGE));
      
    } catch (error) {
      console.error('❌ Erreur chargement offres:', error);
      setOffers([]);
    } finally {
      setLoading(false);
    }
  };

  // =============================================================================
  // FONCTION 2 : Gérer les changements de filtres (depuis les deux composants)
  // =============================================================================
  // src/pages/Home.jsx

  const handleFilterChange = (newFilters) => {
    console.log('🎯 Nouveaux filtres reçus:', newFilters);
  
    // ✅ CORRECTION : Si l'objet est vide (réinitialisation), on réinitialise tout
    const updatedFilters = Object.keys(newFilters).length === 0 
      ? {
          keyword: '',
          pays: '',
          domaine: '',
          structure: '',
          date_publication: '',
          max_days: ''
        }
      : { ...filters, ...newFilters };
  
    setFilters(updatedFilters);
    setCurrentPage(1);
    fetchOffers(1, updatedFilters);
  };

  // =============================================================================
  // FONCTION 3 : Changement de page
  // =============================================================================
  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
      fetchOffers(page, filters);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  // =============================================================================
  // EFFET INITIAL : Charger les offres au montage
  // =============================================================================
  useEffect(() => {
    fetchOffers(1, filters);
  }, []);  // ✅ Exécuter une seule fois au montage

  // =============================================================================
  // GÉNÉRATION DES NUMÉROS DE PAGE
  // =============================================================================
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

  // =============================================================================
  // RENDU
  // =============================================================================
  return (
    <div className="min-vh-100" style={{ backgroundColor: '#f8f9fa' }}>
      
      {/* ✅ FILTRES HORIZONTAUX EN HAUT */}
      <SearchFilters onSearch={handleFilterChange} />

      <div className="container-fluid py-4">
        <div className="row">
          
          {/* ✅ FILTRES VERTICAUX À GAUCHE */}
          <div className="col-lg-3">
            <div className="sticky-top" style={{ top: '20px' }}>
              <VerticalFilters onFilterChange={handleFilterChange} />
            </div>
          </div>

          {/* ✅ RÉSULTATS À DROITE */}
          <div className="col-lg-9">
            
            {/* En-tête avec compteur */}
            <div className="d-flex justify-content-between align-items-center mb-3">
              <div>
                <h4 className="mb-1">
                  <i className="bi bi-briefcase me-2"></i>
                  Appels d'offres
                </h4>
                <p className="text-muted small mb-0">
                  {totalCount} offre(s) trouvée(s)
                  {filters.domaine && <span className="ms-2 badge bg-primary">Domaine: {filters.domaine}</span>}
                  {filters.pays && <span className="ms-2 badge bg-success">Pays: {filters.pays}</span>}
                </p>
              </div>
              
              <button 
                className="btn btn-outline-primary btn-sm"
                onClick={() => fetchOffers(currentPage, filters)}
                title="Rafraîchir"
              >
                <i className="bi bi-arrow-clockwise me-1"></i>
                Actualiser
              </button>
            </div>

            {/* Loading */}
            {loading ? (
              <div className="text-center py-5">
                <div className="spinner-border text-primary" role="status">
                  <span className="visually-hidden">Chargement...</span>
                </div>
                <p className="text-muted mt-3">Chargement des offres...</p>
              </div>
            ) : (
              <>
                {/* Grille des offres */}
                <div className="row g-3">
                  {offers.length > 0 ? (
                    offers.map(offer => (
                      <div className="col-12" key={offer.id}>
                        <JobCard offre={offer} />
                      </div>
                    ))
                  ) : (
                    <div className="col-12">
                      <div className="alert alert-info text-center py-5">
                        <i className="bi bi-inbox" style={{ fontSize: '3rem' }}></i>
                        <p className="mt-3 mb-0">Aucune offre trouvée avec ces critères</p>
                        {/*<button 
                          className="btn btn-outline-primary mt-3"
                          onClick={() => handleFilterChange({})}
                        >
                          Réinitialiser les filtres
                        </button>*/}
                      </div>
                    </div>
                  )}
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <nav className="mt-4" aria-label="Pagination">
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
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;