// src/pages/Home.jsx
import React, { useState, useEffect } from 'react';
import SearchFilters from '../components/SearchFilters';
import JobCard from '../components/JobCard';
import { searchOffres } from '../services/api';

const Home = () => {
  const [offres, setOffres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchOffres = async ({ keyword = '', country = '' } = {}) => {
    try {
      setLoading(true);
      setError(null);
      
      const { results, count } = await searchOffres({ keyword, country });
      // ✅ Protection : toujours un tableau
      setOffres(Array.isArray(results) ? results : []);
      
    } catch (err) {
      console.error('❌ Erreur API:', err);
      setError('Impossible de charger les offres.');
      setOffres([]); // ✅ État sécurisé en cas d'erreur
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOffres();
  }, []);

  return (
    <div className="min-vh-100 d-flex flex-column">
      {/* Bannière */}
      <div className="bg-primary text-white py-4 text-center">
        <div className="container">
          <h1 className="fw-bold">📢 Appels d'Offres</h1>
          <p className="mb-0">Trouvez et consultez les marchés publics du Burkina Faso</p>
        </div>
      </div>

      {/* Filtres */}
      <SearchFilters onSearch={fetchOffres} />

      {/* Contenu principal */}
      <main className="flex-grow-1 py-4 bg-light">
        <div className="container">
          
          {/* Message d'erreur */}
          {error && (
            <div className="alert alert-danger alert-dismissible fade show" role="alert">
              ⚠️ {error}
              <button type="button" className="btn-close" onClick={() => { setError(null); fetchOffres({}); }}></button>
            </div>
          )}

          {/* État de chargement */}
          {loading ? (
            <div className="text-center py-5">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Chargement...</span>
              </div>
            </div>
          ) : (
            <>
              {/* En-tête de résultats */}
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h5 className="mb-0">📋 Résultats</h5>
                <span className="badge bg-secondary">{offres.length} offre(s)</span>
              </div>

              {/* Liste des offres */}
              {offres.length > 0 ? (
                <div className="row g-3">
                  {offres.map((offre) => (
                    // ✅ KEY STABLE : jamais d'index ou Math.random()
                    <div className="col-md-6 col-lg-4" key={offre?.id || `offre-${offre?.titre?.slice(0,10)}`}>
                      <JobCard offre={offre} />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="alert alert-info text-center">
                  🔍 Aucune offre trouvée pour ces critères.
                  <br />
                  <button 
                    className="btn btn-link p-0 mt-1" 
                    onClick={() => fetchOffres({ keyword: '', country: '' })}
                  >
                    Afficher toutes les offres
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
};

export default Home;