// src/components/SearchFilters.jsx
import React, { useState } from 'react';

const SearchFilters = ({ onSearch }) => {
  // État local pour le formulaire
  const [keyword, setKeyword] = useState('');
  const [country, setCountry] = useState('');

  // Gestion de la saisie mot-clé
  const handleKeywordChange = (e) => {
    const value = e.target.value;
    setKeyword(value); // ✅ Mise à jour d'état correcte
  };

  // Soumission du formulaire
  const handleSubmit = (e) => {
    e.preventDefault(); // ⛔ Empêche le rechargement de page
    if (typeof onSearch === 'function') {
      onSearch({ keyword, country });
    }
  };

  // Réinitialisation
  const handleClear = () => {
    setKeyword('');
    setCountry('');
    if (typeof onSearch === 'function') {
      onSearch({ keyword: '', country: '' });
    }
  };

  return (
    <section className="bg-white border-bottom py-3 shadow-sm">
      <div className="container">
        <form onSubmit={handleSubmit} className="row g-2 align-items-end">
          
          {/* Champ mot-clé */}
          <div className="col-md-5">
            <label className="form-label small text-muted mb-1">🔍 Recherche</label>
            <input
              type="text"
              className="form-control"
              placeholder="Ex: informatique, santé, route..."
              value={keyword}
              onChange={handleKeywordChange} // ✅ Handler dédié
              autoComplete="off"
            />
          </div>

          {/* Champ pays */}
          <div className="col-md-3">
            <label className="form-label small text-muted mb-1">🌍 Pays</label>
            <select
              className="form-select"
              value={country}
              onChange={(e) => setCountry(e.target.value)}
            >
              <option value="">Tous</option>
              <option value="BF">🇧🇫 Burkina Faso</option>
              <option value="CI">🇨🇮 Côte d'Ivoire</option>
              <option value="SN">🇸🇳 Sénégal</option>
              <option value="ML">🇲🇱 Mali</option>
            </select>
          </div>

          {/* Boutons */}
          <div className="col-md-2">
            <button type="submit" className="btn btn-primary w-100">
              🔍 Chercher
            </button>
          </div>
          <div className="col-md-2">
            <button 
              type="button" 
              className="btn btn-outline-secondary w-100"
              onClick={handleClear}
              title="Effacer les filtres"
            >
              ✕
            </button>
          </div>
        </form>
      </div>
    </section>
  );
};

export default SearchFilters;