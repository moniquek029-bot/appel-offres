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
    // 🌍 AFRIQUE DE L'OUEST (CEDEAO + Mauritanie)
    { code: 'BF', name: 'Burkina Faso', flag: '🇧🇫' },
    { code: 'BJ', name: 'Bénin', flag: '🇧🇯' },
    { code: 'CV', name: 'Cap-Vert', flag: '🇨🇻' },
    { code: 'CI', name: "Côte d'Ivoire", flag: '🇨🇮' },
    { code: 'GM', name: 'Gambie', flag: '🇬🇲' },
    { code: 'GH', name: 'Ghana', flag: '🇬🇭' },
    { code: 'GN', name: 'Guinée', flag: '🇬🇳' },
    { code: 'GW', name: 'Guinée-Bissau', flag: '🇬🇼' },
    { code: 'LR', name: 'Libéria', flag: '🇱🇷' },
    { code: 'ML', name: 'Mali', flag: '🇲🇱' },
    { code: 'MR', name: 'Mauritanie', flag: '🇲🇷' },
    { code: 'NE', name: 'Niger', flag: '🇳🇪' },
    { code: 'NG', name: 'Nigeria', flag: '🇳🇬' },
    { code: 'SN', name: 'Sénégal', flag: '🇸🇳' },
    { code: 'SL', name: 'Sierra Leone', flag: '🇸🇱' },
    { code: 'TG', name: 'Togo', flag: '🇹🇬' },

    // 🌍 AFRIQUE DE L'EST (Corne de l'Afrique + EAC)
    { code: 'BI', name: 'Burundi', flag: '🇧🇮' },
    { code: 'DJ', name: 'Djibouti', flag: '🇩🇯' },
    { code: 'ER', name: 'Érythrée', flag: '🇪🇷' },
    { code: 'ET', name: 'Éthiopie', flag: '🇪🇹' },
    { code: 'KE', name: 'Kenya', flag: '🇰🇪' },
    { code: 'RW', name: 'Rwanda', flag: '🇷🇼' },
    { code: 'SC', name: 'Seychelles', flag: '🇸🇨' },
    { code: 'SO', name: 'Somalie', flag: '🇸🇴' },
    { code: 'SD', name: 'Soudan', flag: '🇸🇩' },
    { code: 'SS', name: 'Soudan du Sud', flag: '🇸🇸' },
    { code: 'TZ', name: 'Tanzanie', flag: '🇹🇿' },
    { code: 'UG', name: 'Ouganda', flag: '🇺🇬' },

    // 🌍 AUTRES PAYS AFRICAINS (Pour exhaustivité)
    { code: 'DZ', name: 'Algérie', flag: '🇩🇿' },
    { code: 'AO', name: 'Angola', flag: '🇦🇴' },
    { code: 'CM', name: 'Cameroun', flag: '🇨🇲' },
    { code: 'CF', name: 'Centrafrique', flag: '🇨🇫' },
    { code: 'TD', name: 'Tchad', flag: '🇹🇩' },
    { code: 'KM', name: 'Comores', flag: '🇰🇲' },
    { code: 'CG', name: 'Congo', flag: '🇨🇬' },
    { code: 'CD', name: 'RD Congo', flag: '🇨🇩' },
    { code: 'GA', name: 'Gabon', flag: '🇬🇦' },
    { code: 'GQ', name: 'Guinée équatoriale', flag: '🇬🇶' },
    { code: 'LS', name: 'Lesotho', flag: '🇱🇸' },
    { code: 'MG', name: 'Madagascar', flag: '🇲🇬' },
    { code: 'MW', name: 'Malawi', flag: '🇲🇼' },
    { code: 'MU', name: 'Maurice', flag: '🇲🇺' },
    { code: 'MA', name: 'Maroc', flag: '🇲🇦' },
    { code: 'MZ', name: 'Mozambique', flag: '🇲🇿' },
    { code: 'NA', name: 'Namibie', flag: '🇳🇦' },
    { code: 'ZA', name: 'Afrique du Sud', flag: '🇿🇦' },
    { code: 'SZ', name: 'Eswatini', flag: '🇸🇿' },
    { code: 'ZM', name: 'Zambie', flag: '🇿🇲' },
    { code: 'ZW', name: 'Zimbabwe', flag: '🇿🇼' },
    { code: 'TN', name: 'Tunisie', flag: '🇹🇳' },
    { code: 'EG', name: 'Égypte', flag: '🇪🇬' },
    { code: 'LY', name: 'Libye', flag: '🇱🇾' },

    // 🌍 PAYS HORS AFRIQUE (Conservés de votre ancienne liste)
    { code: 'AR', name: 'Argentine', flag: '🇦🇷' },
    { code: 'ID', name: 'Indonésie', flag: '🇮🇩' },
    { code: 'BA', name: 'Bosnie-Herzégovine', flag: '🇧🇦' },
    { code: 'US', name: 'États-Unis', flag: '🇺🇸' },
    { code: 'GB', name: 'Royaume-Uni', flag: '🇬🇧' },
    { code: 'FR', name: 'France', flag: '🇫🇷' },
    { code: 'DE', name: 'Allemagne', flag: '🇩🇪' },
    { code: 'BE', name: 'Belgique', flag: '🇧🇪' },
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