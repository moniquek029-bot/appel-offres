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
          <div className="col-md-8">
            <div className="input-group">
              <span className="input-group-text bg-white border-end-0">
                🔍
              </span>
              <input
                type="text"
                className="form-control border-start-0"
                placeholder="Rechercher un appel d'offres (titre, organisme, description)..."
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
              />
            </div>
          </div>
          <div className="col-md-2">
            <button type="submit" className="btn btn-primary w-100">
              Rechercher
            </button>
          </div>
          <div className="col-md-2">
            <button 
              type="button" 
              className="btn btn-outline-secondary w-100"
              onClick={handleClear}
            >
              Effacer
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SearchBar;