// src/components/SearchFilters.jsx
import React, { useState } from 'react';

const SearchFilters = ({ onSearch }) => {
  const [keyword, setKeyword] = useState('');
  const [country, setCountry] = useState('');
  const [maxDays, setMaxDays] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (typeof onSearch === 'function') {
      onSearch({ keyword, pays: country, max_days: maxDays });
    }
  };

  const handleClear = () => {
    setKeyword('');
    setCountry('');
    setMaxDays('');
    if (typeof onSearch === 'function') {
      onSearch({ keyword: '', pays: '', max_days: '' });
    }
  };

  return (
    <div className="bg-white border-bottom shadow-sm">
      <div className="container py-3">
        <form onSubmit={handleSubmit}>
          {/* Ligne de recherche principale */}
          <div className="row g-2 align-items-end">
            <div className="col-md-7">
              <label className="form-label small text-muted fw-semibold mb-1">
                🔍 Recherche
              </label>
              <input
                type="text"
                className="form-control form-control-lg"
                placeholder="Rechercher un appel d'offres (titre, organisation, description)..."
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
              />
            </div>
            <div className="col-md-3">
              <label className="form-label small text-muted fw-semibold mb-1">
                📍 Localité
              </label>
              <select
                className="form-select form-select-lg"
                value={country}
                onChange={(e) => setCountry(e.target.value)}
              >
                <option value="">Toutes les localités</option>
                <option value="BF">🇧🇫 Burkina Faso</option>
                <option value="CI">🇨🇮 Côte d'Ivoire</option>
                <option value="SN">🇸🇳 Sénégal</option>
                <option value="ML">🇲🇱 Mali</option>
                <option value="NE">🇳🇪 Niger</option>
                <option value="TG">🇹🇬 Togo</option>
                <option value="BJ">🇧🇯 Bénin</option>
                <option value="CM">🇨🇲 Cameroun</option>
                <option value="GH">🇬🇭 Ghana</option>
                <option value="RW">🇷🇼 Rwanda</option>
                <option value="CD">🇨🇩 RDC</option>
                <option value="ET">🇪🇹 Éthiopie</option>
                <option value="DZ">🇩🇿 Algérie</option>
                <option value="MA">🇲🇦 Maroc</option>
                <option value="TN">🇹🇳 Tunisie</option>
                <option value="LY">🇱🇾 Libye</option>
                <option value="SD">🇸🇩 Soudan</option>
                <option value="SO">🇸🇴 Somalie</option>
                <option value="ER">🇪🇷 Érythrée</option>
                <option value="SS">🇸🇸 Soudan du Sud</option>
                <option value="GA">🇬🇦 Gabon</option>
                <option value="CG">🇨🇬 Congo</option>
                <option value="GQ">🇬🇶 Guinée équatoriale</option>
                <option value="CV">🇨🇻 Cap-Vert</option>
                <option value="KM">🇰🇲 Comores</option>
                <option value="ST">🇸🇹 Sao Tomé-et-Principe</option>
                <option value="NG">🇳🇬 Nigeria</option>
                <option value="ZA">🇿🇦 Afrique du Sud</option>
                <option value="ZW">🇿🇼 Zimbabwe</option>
                <option value="TH">🇹🇭 Thaïlande</option>
                <option value="IN">🇮🇳 Inde</option>
                <option value="PK">🇵🇰 Pakistan</option>
                
              </select>
            </div>
            <div className="col-md-2">
              <button type="submit" className="btn btn-primary btn-lg w-100">
                🔍 Chercher
              </button>
            </div>
          </div>

          {/* Filtres avancés (expandables) */}
          <div className="mt-3">
            <button 
              type="button"
              className="btn btn-link text-decoration-none p-0 small"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? '− Masquer les filtres' : '+ Afficher les filtres avancés'}
            </button>

            {isExpanded && (
              <div className="row g-2 mt-2 pt-2 border-top">
                <div className="col-md-3">
                  <label className="form-label small text-muted">Domaine</label>
                  <select className="form-select">
                    <option value="">Tous</option>
                    <option value="informatique">Informatique</option>
                    <option value="btp">BTP</option>
                    <option value="sante">Santé</option>
                    <option value="finance">Finance</option>
                    <option value="construction">Construction</option>
                    <option value="fourniture">Fourniture</option>
                    <option value="comptabilite">Comptabilité</option>
                    <option value="agriculture">Agriculture</option>
                    <option value="education">Éducation</option>
                    <option value="elevage">Élevage</option>
                    <option value="transport">Transport</option>
                  </select>
                </div>
                <div className="col-md-3">
                  <label className="form-label small text-muted">🏢 Structure</label>
                  <input type="text" className="form-control" placeholder="Nom de l'organisme" />
                </div>
                <div className="col-md-3">
                  <label className="form-label small text-muted">⏰ Date d'expiration</label>
                  <select 
                    className="form-select"
                    value={maxDays}
                    onChange={(e) => setMaxDays(e.target.value)}
                  >
                    <option value="">Toutes</option>
                    <option value="7">Dans 7 jours</option>
                    <option value="14">Dans 14 jours</option>
                    <option value="30">Dans 30 jours</option>
                    <option value="60">Dans 60 jours</option>
                  </select>
                </div>
                <div className="col-md-3 d-flex align-items-end">
                  <button 
                    type="button" 
                    className="btn btn-outline-secondary w-100"
                    onClick={handleClear}
                  >
                    ✕ Réinitialiser
                  </button>
                </div>
              </div>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};

export default SearchFilters;