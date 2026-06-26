// =============================================================================
// FICHIER: src/components/SearchFilters.jsx
// MODIFICATION: Liaison de TOUS les filtres (Domaine, Structure, Date Pub, etc.)
// ENTREPRISE: EXPERTISE-ID
// =============================================================================

import React, { useState } from 'react';

const SearchFilters = ({ onSearch }) => {
  // =============================================================================
  // ÉTATS DE TOUS LES FILTRES
  // =============================================================================
  const [keyword, setKeyword] = useState('');
  const [country, setCountry] = useState('');
  const [domaine, setDomaine] = useState('');
  const [structure, setStructure] = useState('');
  const [datePublication, setDatePublication] = useState(''); // 🎯 Choix unique
  const [maxDays, setMaxDays] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);

  // =============================================================================
  // SOUMISSION: Envoi de la totalité des filtres combinés
  // =============================================================================
  const handleSubmit = (e) => {
    e.preventDefault();
    if (typeof onSearch === 'function') {
      onSearch({
        keyword: keyword,
        pays: country,
        domaine: domaine,
        structure: structure,
        date_publication: datePublication,
        max_days: maxDays
      });
    }
  };

  // =============================================================================
  // RÉINITIALISATION: Remise à zéro complète
  // =============================================================================
  const handleClear = () => {
    setKeyword('');
    setCountry('');
    setDomaine('');
    setStructure('');
    setDatePublication('');
    setMaxDays('');
    
    if (typeof onSearch === 'function') {
      onSearch({
        keyword: '',
        pays: '',
        domaine: '',
        structure: '',
        date_publication: '',
        max_days: ''
      });
    }
  };

  return (
    <div className="bg-white border-bottom shadow-sm">
      <div className="container py-3">
        <form onSubmit={handleSubmit}>
          
          {/* -----------------------------------------------------------------
              LIGNE PRINCIPALE DE RECHERCHE
              ----------------------------------------------------------------- */}
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
                  <option value="BJ">🇧🇯 Bénin</option>
                  <option value="CM">🇨🇲 Cameroun</option>
                  <option value="GA">🇬🇦 Gabon</option>
                  <option value="NG">🇳🇬 Nigeria</option>
                  <option value="RW">🇷🇼 Rwanda</option>
                  <option value="GN">GN Ghana</option>
                  <option value="LM">LM Lomé</option>
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

          {/* -----------------------------------------------------------------
              SECTION FILTRES AVANCÉS (DÉPLOYABLE)
              ----------------------------------------------------------------- */}
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
                
                {/*  Domaine lié à son état */}
                <div className="col-md-3">
                  <label className="form-label small text-muted">
                    <i className="bi bi-folder me-1"></i>Domaine
                  </label>
                  <select 
                    className="form-select"
                    value={domaine}
                    onChange={(e) => setDomaine(e.target.value)}
                  >
                    <option value="">Tous</option>
                    <option value="Informatique">Informatique</option>
                    <option value="BTP">BTP</option>
                    <option value="Santé">Santé</option>
                    <option value="Finance">Finance</option>
                    <option value="Construction">Construction</option>
                    <option value="Fourniture">Fourniture</option>
                    <option value="Transport">Transport</option>
                    <option value="Télécommunications">Télécommunications</option>
                    <option value="Autre">Autre</option>
                  </select>
                </div>

                {/*  Structure liée à son état */}
                <div className="col-md-3">
                  <label className="form-label small text-muted">
                    <i className="bi bi-building me-1"></i>Structure
                  </label>
                  <input 
                    type="text" 
                    className="form-control" 
                    placeholder="Nom de l'organisme" 
                    value={structure}
                    onChange={(e) => setStructure(e.target.value)}
                  />
                </div>

                {/*  Date de publication (Calendrier Unique) */}
                <div className="col-md-2">
                  <label className="form-label small text-muted">
                    <i className="bi bi-calendar-check me-1"></i>Publié le
                  </label>
                  <input 
                    type="date" 
                    className="form-control"
                    value={datePublication}
                    onChange={(e) => setDatePublication(e.target.value)}
                  />
                </div>

                {/*  Date d'expiration liée à son état */}
                <div className="col-md-2">
                  <label className="form-label small text-muted">
                    <i className="bi bi-calendar-event me-1"></i>Date d'expiration
                  </label>
                  <select 
                    className="form-select"
                    value={maxDays}
                    onChange={(e) => setMaxDays(e.target.value)}
                  >
                    <option value="">Toutes</option>
                    <option value="2">Dans 2 jours</option>
                    <option value="5">Dans 5 jours</option>
                    <option value="7">Dans 7 jours</option>
                    <option value="14">Dans 14 days</option>
                    <option value="30">Dans 30 jours</option>
                  </select>
                </div>

                {/* Bouton de réinitialisation de la section avancée */}
                <div className="col-md-2 d-flex align-items-end justify-content-end">
                  <button 
                    type="button" 
                    className="btn btn-outline-secondary w-100"
                    onClick={handleClear}
                    title="Réinitialiser tous les filtres"
                  >
                    <i className="bi bi-arrow-counterclockwise me-1"></i>Réinitialiser
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