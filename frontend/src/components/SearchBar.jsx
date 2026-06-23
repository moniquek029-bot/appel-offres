// src/components/SearchBar.jsx
import React, { useState } from 'react';

const SearchBar = ({ onSearch }) => {
  const [keyword, setKeyword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (typeof onSearch === 'function') {
      onSearch(keyword);
    }
  };

  const handleClear = () => {
    setKeyword('');
    if (typeof onSearch === 'function') {
      onSearch('');
    }
  };

  return (
    <div className="bg-white border-bottom py-3 shadow-sm">
      <div className="container">
        <form onSubmit={handleSubmit} className="row g-2 align-items-center">
          <div className="col-md-10">
            <div className="input-group">
              {/* Icône de recherche */}
              <span className="input-group-text bg-white border-end-0">
                <i className="bi bi-search text-muted"></i>
              </span>
              
              {/* Champ de recherche */}
              <input
                type="text"
                className="form-control border-start-0 border-end-0"
                placeholder="Rechercher un appel d'offres (titre, organisme, description)..."
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                style={{ paddingRight: '40px', position: 'relative' }}
              />
              
              {/* Bouton X pour effacer (apparaît seulement si du texte est présent) */}
              {keyword && (
                <button
                  type="button"
                  className="btn btn-link text-muted position-absolute"
                  onClick={handleClear}
                  title="Effacer la recherche"
                  style={{
                    right: '10px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    zIndex: 10,
                    padding: '0 8px',
                    textDecoration: 'none',
                    border: 'none',
                    background: 'transparent'
                  }}
                >
                  <i className="bi bi-x-lg"></i>
                </button>
              )}
            </div>
          </div>
          
          <div className="col-md-2">
            <button type="submit" className="btn btn-primary w-100">
              <i className="bi bi-search me-2"></i>
              Rechercher
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SearchBar;