// src/components/SearchFilters.jsx
import React, { useState, useEffect } from 'react';

const SearchFilters = ({ onSearch, initialValues = {} }) => {
  // ✅ Initialiser avec les valeurs de l'URL
  const [keyword, setKeyword] = useState(initialValues.keyword || '');
  const [country, setCountry] = useState(initialValues.pays || '');

  // ✅ Synchroniser quand initialValues change (au retour depuis JobDetail)
  useEffect(() => {
    setKeyword(initialValues.keyword || '');
    setCountry(initialValues.pays || '');
  }, [initialValues.keyword, initialValues.pays]);

  const paysList = [
    { code: 'BF', name: 'Burkina Faso', flag: '🇧🇫' },
    { code: 'BJ', name: 'Bénin', flag: '🇧🇯' },
    { code: 'CI', name: "Côte d'Ivoire", flag: '🇨🇮' },
    { code: 'SN', name: 'Sénégal', flag: '🇸🇳' },
    { code: 'ML', name: 'Mali', flag: '🇲🇱' },
    { code: 'NE', name: 'Niger', flag: '🇳🇪' },
    { code: 'TG', name: 'Togo', flag: '🇹🇬' },
    { code: 'CM', name: 'Cameroun', flag: '🇨🇲' },
    { code: 'GA', name: 'Gabon', flag: '🇬🇦' },
    { code: 'NG', name: 'Nigeria', flag: '🇳🇬' },
    { code: 'RW', name: 'Rwanda', flag: '🇷🇼' },
    { code: 'GH', name: 'Ghana', flag: '🇬🇭' },
    { code: 'AR', name: 'Argentine', flag: '🇦🇷' },
    { code: 'ID', name: 'Indonésie', flag: '🇮🇩' },
    { code: 'BA', name: 'Bosnie-Herzégovine', flag: '🇧🇦' },
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (typeof onSearch === 'function') {
      onSearch({
        keyword: keyword,
        pays: country,
        // ✅ On préserve les autres filtres (domaine, etc.) s'ils existent
        domaine: initialValues.domaine || '',
        structure: initialValues.structure || '',
        date_publication: initialValues.date_publication || '',
        max_days: initialValues.max_days || '',
      });
    }
  };

  return (
    <div className="bg-white border-bottom shadow-sm">
      <div className="container py-3">
        <form onSubmit={handleSubmit}>
          <div className="row g-2 align-items-end">
            <div className="col-md-7">
              <label className="form-label small text-muted fw-semibold mb-1">
               {/* <i className="bi bi-search me-1"></i>Recherche*/}
              </label>
              <div className="position-relative">
                <input
                  type="text"
                  className="form-control form-control-lg"
                  placeholder="Rechercher un appel d'offres..."
                  value={keyword}
                  onChange={(e) => setKeyword(e.target.value)}
                  style={{ paddingRight: '40px' }}
                />
                {keyword && (
                  <button
                    type="button"
                    className="btn btn-link position-absolute top-50 end-0 translate-middle-y text-muted"
                    onClick={() => setKeyword('')}
                    style={{ padding: '0 10px', zIndex: 10 }}
                  >
                    <i className="bi bi-x-lg"></i>
                  </button>
                )}
              </div>
            </div>

            {/*<div className="col-md-3">
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
                  {paysList.map(p => (
                    <option key={p.code} value={p.code}>
                      {p.flag} {p.name}
                    </option>
                  ))}
                </select>
                {country && (
                  <button
                    type="button"
                    className="btn btn-link position-absolute top-50 end-0 translate-middle-y text-muted"
                    onClick={() => setCountry('')}
                    style={{ padding: '0 10px', zIndex: 10, marginRight: '20px' }}
                  >
                    <i className="bi bi-x-lg"></i>
                  </button>
                )}
              </div>
            </div>*/}

            <div className="col-md-2">
              <button type="submit" className="btn btn-primary btn-lg w-100">
                <i className="bi bi-search me-2"></i>Chercher
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SearchFilters;