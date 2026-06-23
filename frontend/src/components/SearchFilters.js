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
                <i className="bi bi-search me-1"></i>Recherche
              </label>
              <div className="position-relative">
                <input
                  type="text"
                  className="form-control form-control-lg"
                  placeholder="Rechercher un appel d'offres (titre, organisation, description)..."
                  value={keyword}
                  onChange={(e) => setKeyword(e.target.value)}
                  style={{ paddingRight: '40px' }}
                />
                {keyword && (
                  <button
                    type="button"
                    className="btn btn-link position-absolute top-50 end-0 translate-middle-y text-muted"
                    onClick={() => setKeyword('')}
                    title="Effacer la recherche"
                    style={{ padding: '0 10px', zIndex: 10 }}
                  >
                    <i className="bi bi-x-lg"></i>
                  </button>
                )}
              </div>
            </div>
            <div className="col-md-3">
              <label className="form-label small text-muted fw-semibold mb-1">
                <i className="bi bi-geo-alt me-1"></i>Localité
              </label>
              <div className="position-relative">
                <select
                  className="form-select form-select-lg"
                  value={country}
                  onChange={(e) => setCountry(e.target.value)}
                  style={{ paddingRight: '40px' }}
                >
                  <option value="">Toutes les localités</option>
                  <option value="BF">🇧🇫 Burkina Faso</option>
                  <option value="CI">🇨🇮 Côte d'Ivoire</option>
                  <option value="SN">🇸🇳 Sénégal</option>
                  <option value="ML">🇲🇱 Mali</option>
                  <option value="NE">🇳🇪 Niger</option>
                  <option value="TG">🇹🇬 Togo</option>
                  <option value="BJ">🇧 Bénin</option>
                  <option value="CM">🇨🇲 Cameroun</option>
                  <option value="GH">🇬🇭 Ghana</option>
                  <option value="RW">🇷🇼 Rwanda</option>
                  <option value="CD">🇨 RDC</option>
                  <option value="ET">🇪🇹 Éthiopie</option>
                  <option value="DZ">🇩🇿 Algérie</option>
                  <option value="MA">🇲🇦 Maroc</option>
                  <option value="TN">🇹 Tunisie</option>
                  <option value="LY">🇱🇾 Libye</option>
                  <option value="SD">🇸🇩 Soudan</option>
                  <option value="SO">🇸🇴 Somalie</option>
                  <option value="ER">🇪 Érythrée</option>
                  <option value="SS">🇸🇸 Soudan du Sud</option>
                  <option value="GA">🇬 Gabon</option>
                  <option value="CG">🇨🇬 Congo</option>
                  <option value="GQ">🇬 Guinée équatoriale</option>
                  <option value="CV">🇨🇻 Cap-Vert</option>
                  <option value="KM">🇰🇲 Comores</option>
                  <option value="ST">🇸🇹 Sao Tomé-et-Principe</option>
                  <option value="NG">🇳🇬 Nigeria</option>
                  <option value="ZA">🇿🇦 Afrique du Sud</option>
                  <option value="ZW">🇿🇼 Zimbabwe</option>
                  <option value="TH">🇹 Thaïlande</option>
                  <option value="IN">🇮🇳 Inde</option>
                  <option value="PK">🇵 Pakistan</option>
                </select>
                {country && (
                  <button
                    type="button"
                    className="btn btn-link position-absolute top-50 end-0 translate-middle-y text-muted"
                    onClick={() => setCountry('')}
                    title="Effacer la localité"
                    style={{ padding: '0 10px', zIndex: 10, marginRight: '20px' }}
                  >
                    <i className="bi bi-x-lg"></i>
                  </button>
                )}
              </div>
            </div>
            <div className="col-md-2">
              <button type="submit" className="btn btn-primary btn-lg w-100">
                <i className="bi bi-search me-2"></i>Chercher
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
              {isExpanded ? (
                <><i className="bi bi-dash-circle me-1"></i>Masquer les filtres</>
              ) : (
                <><i className="bi bi-plus-circle me-1"></i>Afficher les filtres avancés</>
              )}
            </button>

            {isExpanded && (
              <div className="row g-2 mt-2 pt-2 border-top">
                <div className="col-md-3">
                  <label className="form-label small text-muted">
                    <i className="bi bi-folder me-1"></i>Domaine
                  </label>
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
                  <label className="form-label small text-muted">
                    <i className="bi bi-building me-1"></i>Structure
                  </label>
                  <input type="text" className="form-control" placeholder="Nom de l'organisme" />
                </div>
                <div className="col-md-3">
                  <label className="form-label small text-muted">
                    <i className="bi bi-calendar-event me-1"></i>Date d'expiration
                  </label>
                  <div className="position-relative">
                    <select 
                      className="form-select"
                      value={maxDays}
                      onChange={(e) => setMaxDays(e.target.value)}
                      style={{ paddingRight: '40px' }}
                    >
                      <option value="">Toutes</option>
                      <option value="7">Dans 7 jours</option>
                      <option value="14">Dans 14 jours</option>
                      <option value="30">Dans 30 jours</option>
                      <option value="60">Dans 60 jours</option>
                    </select>
                    {/*{maxDays && (
                      {/*<button
                        type="button"
                        className="btn btn-link position-absolute top-50 end-0 translate-middle-y text-muted"
                        onClick={() => setMaxDays('')}
                        title="Effacer le filtre"
                        style={{ padding: '0 10px', zIndex: 10, marginRight: '20px' }}
                      >
                        <i className="bi bi-x-lg"></i>
                      </button>*/}
                    {/*)}*/}
                  </div>
                </div>
                <div className="col-md-3 d-flex align-items-end justify-content-end">
                  {/* Bouton X pour réinitialiser tous les filtres */}
                  <button 
                    type="button" 
                    className="btn btn-outline-secondary btn-sm"
                    onClick={handleClear}
                    title="Réinitialiser tous les filtres"
                  >
                    <i className="bi bi-x-lg me-1"></i>Réinitialiser
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