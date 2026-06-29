// =============================================================================
// FICHIER: src/components/SearchFilters.jsx
// MODIFICATION: Listes de pays ÉLARGIES et corrigées
// ENTREPRISE: EXPERTISE-ID
// =============================================================================

import React, { useState } from 'react';

const SearchFilters = ({ onSearch }) => {
  // =============================================================================
  // ÉTATS (seulement les filtres principaux)
  // =============================================================================
  const [keyword, setKeyword] = useState('');
  const [country, setCountry] = useState('');

  // =============================================================================
  // LISTE COMPLÈTE DES PAYS (150+ pays)
  // =============================================================================
  const paysList = [
    // Afrique de l'Ouest
    { code: 'BF', name: 'Burkina Faso', flag: '🇧🇫' },
    { code: 'BJ', name: 'Bénin', flag: '🇧🇯' },
    { code: 'CI', name: "Côte d'Ivoire", flag: '🇨🇮' },
    { code: 'CV', name: 'Cap-Vert', flag: '🇨🇻' },
    { code: 'GH', name: 'Ghana', flag: '🇬🇭' },
    { code: 'GM', name: 'Gambie', flag: '🇬🇲' },
    { code: 'GN', name: 'Guinée', flag: '🇬🇳' },
    { code: 'GW', name: 'Guinée-Bissau', flag: '🇬🇼' },
    { code: 'LR', name: 'Liberia', flag: '🇱🇷' },
    { code: 'ML', name: 'Mali', flag: '🇲🇱' },
    { code: 'MR', name: 'Mauritanie', flag: '🇲🇷' },
    { code: 'NE', name: 'Niger', flag: '🇳🇪' },
    { code: 'NG', name: 'Nigeria', flag: '🇳🇬' },
    { code: 'SN', name: 'Sénégal', flag: '🇸🇳' },
    { code: 'SL', name: 'Sierra Leone', flag: '🇸🇱' },
    { code: 'TG', name: 'Togo', flag: '🇹🇬' },
    
    // Afrique Centrale
    { code: 'AO', name: 'Angola', flag: '🇦🇴' },
    { code: 'CD', name: 'RD Congo', flag: '🇨🇩' },
    { code: 'CF', name: 'République Centrafricaine', flag: '🇨🇫' },
    { code: 'CG', name: 'Congo', flag: '🇨🇬' },
    { code: 'CM', name: 'Cameroun', flag: '🇨🇲' },
    { code: 'GA', name: 'Gabon', flag: '🇬🇦' },
    { code: 'GQ', name: 'Guinée Équatoriale', flag: '🇬🇶' },
    { code: 'ST', name: 'São Tomé-et-Príncipe', flag: '🇸🇹' },
    { code: 'TD', name: 'Tchad', flag: '🇹🇩' },
    
    // Afrique de l'Est
    { code: 'BI', name: 'Burundi', flag: '🇧🇮' },
    { code: 'DJ', name: 'Djibouti', flag: '🇩🇯' },
    { code: 'ER', name: 'Érythrée', flag: '🇪🇷' },
    { code: 'ET', name: 'Éthiopie', flag: '🇪🇹' },
    { code: 'KE', name: 'Kenya', flag: '🇰🇪' },
    { code: 'KM', name: 'Comores', flag: '🇰🇲' },
    { code: 'MG', name: 'Madagascar', flag: '🇲🇬' },
    { code: 'MU', name: 'Maurice', flag: '🇲🇺' },
    { code: 'MW', name: 'Malawi', flag: '🇲🇼' },
    { code: 'MZ', name: 'Mozambique', flag: '🇲🇿' },
    { code: 'RW', name: 'Rwanda', flag: '🇷🇼' },
    { code: 'SC', name: 'Seychelles', flag: '🇸🇨' },
    { code: 'SD', name: 'Soudan', flag: '🇸🇩' },
    { code: 'SO', name: 'Somalie', flag: '🇸🇴' },
    { code: 'SS', name: 'Soudan du Sud', flag: '🇸🇸' },
    { code: 'TZ', name: 'Tanzanie', flag: '🇹🇿' },
    { code: 'UG', name: 'Ouganda', flag: '🇺🇬' },
    { code: 'ZM', name: 'Zambie', flag: '🇿🇲' },
    { code: 'ZW', name: 'Zimbabwe', flag: '🇿🇼' },
    
    // Afrique du Nord
    { code: 'DZ', name: 'Algérie', flag: '🇩🇿' },
    { code: 'EG', name: 'Égypte', flag: '🇪🇬' },
    { code: 'LY', name: 'Libye', flag: '🇱🇾' },
    { code: 'MA', name: 'Maroc', flag: '🇲🇦' },
    { code: 'TN', name: 'Tunisie', flag: '🇹🇳' },
    
    // Afrique Australe
    { code: 'BW', name: 'Botswana', flag: '🇧🇼' },
    { code: 'LS', name: 'Lesotho', flag: '🇱🇸' },
    { code: 'NA', name: 'Namibie', flag: '🇳🇦' },
    { code: 'SZ', name: 'Eswatini', flag: '🇸🇿' },
    { code: 'ZA', name: 'Afrique du Sud', flag: '🇿🇦' },
    
    // Moyen-Orient
    { code: 'AE', name: 'Émirats Arabes Unis', flag: '🇦🇪' },
    { code: 'BH', name: 'Bahreïn', flag: '🇧🇭' },
    { code: 'IL', name: 'Israël', flag: '🇮🇱' },
    { code: 'IQ', name: 'Irak', flag: '🇮🇶' },
    { code: 'IR', name: 'Iran', flag: '🇮🇷' },
    { code: 'JO', name: 'Jordanie', flag: '🇯🇴' },
    { code: 'KW', name: 'Koweït', flag: '🇰🇼' },
    { code: 'LB', name: 'Liban', flag: '🇱🇧' },
    { code: 'OM', name: 'Oman', flag: '🇴🇲' },
    { code: 'PS', name: 'Palestine', flag: '🇵🇸' },
    { code: 'QA', name: 'Qatar', flag: '🇶🇦' },
    { code: 'SA', name: 'Arabie Saoudite', flag: '🇸🇦' },
    { code: 'SY', name: 'Syrie', flag: '🇸🇾' },
    { code: 'TR', name: 'Turquie', flag: '🇹🇷' },
    { code: 'YE', name: 'Yémen', flag: '🇾🇪' },
    
    // Asie
    { code: 'AF', name: 'Afghanistan', flag: '🇦🇫' },
    { code: 'BD', name: 'Bangladesh', flag: '🇧🇩' },
    { code: 'BN', name: 'Brunei', flag: '🇧🇳' },
    { code: 'BT', name: 'Bhoutan', flag: '🇧🇹' },
    { code: 'CN', name: 'Chine', flag: '🇨🇳' },
    { code: 'CY', name: 'Chypre', flag: '🇨🇾' },
    { code: 'GE', name: 'Géorgie', flag: '🇬🇪' },
    { code: 'ID', name: 'Indonésie', flag: '🇮🇩' },
    { code: 'IN', name: 'Inde', flag: '🇮🇳' },
    { code: 'JP', name: 'Japon', flag: '🇯🇵' },
    { code: 'KG', name: 'Kirghizistan', flag: '🇰🇬' },
    { code: 'KH', name: 'Cambodge', flag: '🇰🇭' },
    { code: 'KR', name: 'Corée du Sud', flag: '🇰🇷' },
    { code: 'KZ', name: 'Kazakhstan', flag: '🇰🇿' },
    { code: 'LA', name: 'Laos', flag: '🇱🇦' },
    { code: 'LK', name: 'Sri Lanka', flag: '🇱🇰' },
    { code: 'MM', name: 'Myanmar', flag: '🇲🇲' },
    { code: 'MN', name: 'Mongolie', flag: '🇲🇳' },
    { code: 'MV', name: 'Maldives', flag: '🇲🇻' },
    { code: 'MY', name: 'Malaisie', flag: '🇲🇾' },
    { code: 'NP', name: 'Népal', flag: '🇳🇵' },
    { code: 'PH', name: 'Philippines', flag: '🇵🇭' },
    { code: 'PK', name: 'Pakistan', flag: '🇵🇰' },
    { code: 'SG', name: 'Singapour', flag: '🇸🇬' },
    { code: 'TH', name: 'Thaïlande', flag: '🇹🇭' },
    { code: 'TJ', name: 'Tadjikistan', flag: '🇹🇯' },
    { code: 'TL', name: 'Timor oriental', flag: '🇹🇱' },
    { code: 'TM', name: 'Turkménistan', flag: '🇹🇲' },
    { code: 'UZ', name: 'Ouzbékistan', flag: '🇺🇿' },
    { code: 'VN', name: 'Vietnam', flag: '🇻🇳' },
    
    // Europe
    { code: 'AL', name: 'Albanie', flag: '🇦🇱' },
    { code: 'AT', name: 'Autriche', flag: '🇦🇹' },
    { code: 'BA', name: 'Bosnie-Herzégovine', flag: '🇧🇦' },
    { code: 'BE', name: 'Belgique', flag: '🇧🇪' },
    { code: 'BG', name: 'Bulgarie', flag: '🇧🇬' },
    { code: 'BY', name: 'Biélorussie', flag: '🇧🇾' },
    { code: 'CH', name: 'Suisse', flag: '🇨🇭' },
    { code: 'CZ', name: 'République Tchèque', flag: '🇨🇿' },
    { code: 'DE', name: 'Allemagne', flag: '🇩🇪' },
    { code: 'DK', name: 'Danemark', flag: '🇩🇰' },
    { code: 'EE', name: 'Estonie', flag: '🇪🇪' },
    { code: 'ES', name: 'Espagne', flag: '🇪🇸' },
    { code: 'FI', name: 'Finlande', flag: '🇫🇮' },
    { code: 'FR', name: 'France', flag: '🇫🇷' },
    { code: 'GB', name: 'Royaume-Uni', flag: '🇬🇧' },
    { code: 'GR', name: 'Grèce', flag: '🇬🇷' },
    { code: 'HR', name: 'Croatie', flag: '🇭🇷' },
    { code: 'HU', name: 'Hongrie', flag: '🇭🇺' },
    { code: 'IE', name: 'Irlande', flag: '🇮🇪' },
    { code: 'IS', name: 'Islande', flag: '🇮🇸' },
    { code: 'IT', name: 'Italie', flag: '🇮🇹' },
    { code: 'LT', name: 'Lituanie', flag: '🇱🇹' },
    { code: 'LU', name: 'Luxembourg', flag: '🇱🇺' },
    { code: 'LV', name: 'Lettonie', flag: '🇱🇻' },
    { code: 'MD', name: 'Moldavie', flag: '🇲🇩' },
    { code: 'ME', name: 'Monténégro', flag: '🇲🇪' },
    { code: 'MK', name: 'Macédoine du Nord', flag: '🇲🇰' },
    { code: 'MT', name: 'Malte', flag: '🇲🇹' },
    { code: 'NL', name: 'Pays-Bas', flag: '🇳🇱' },
    { code: 'NO', name: 'Norvège', flag: '🇳🇴' },
    { code: 'PL', name: 'Pologne', flag: '🇵🇱' },
    { code: 'PT', name: 'Portugal', flag: '🇵🇹' },
    { code: 'RO', name: 'Roumanie', flag: '🇷🇴' },
    { code: 'RS', name: 'Serbie', flag: '🇷🇸' },
    { code: 'RU', name: 'Russie', flag: '🇷🇺' },
    { code: 'SE', name: 'Suède', flag: '🇸🇪' },
    { code: 'SI', name: 'Slovénie', flag: '🇸🇮' },
    { code: 'SK', name: 'Slovaquie', flag: '🇸🇰' },
    { code: 'UA', name: 'Ukraine', flag: '🇺🇦' },
    
    // Amériques
    { code: 'AG', name: 'Antigua-et-Barbuda', flag: '🇦🇬' },
    { code: 'AR', name: 'Argentine', flag: '🇦🇷' },
    { code: 'BB', name: 'Barbade', flag: '🇧🇧' },
    { code: 'BO', name: 'Bolivie', flag: '🇧🇴' },
    { code: 'BR', name: 'Brésil', flag: '🇧🇷' },
    { code: 'BS', name: 'Bahamas', flag: '🇧🇸' },
    { code: 'BZ', name: 'Belize', flag: '🇧🇿' },
    { code: 'CA', name: 'Canada', flag: '🇨🇦' },
    { code: 'CL', name: 'Chili', flag: '🇨🇱' },
    { code: 'CO', name: 'Colombie', flag: '🇨🇴' },
    { code: 'CR', name: 'Costa Rica', flag: '🇨🇷' },
    { code: 'CU', name: 'Cuba', flag: '🇨🇺' },
    { code: 'DM', name: 'Dominique', flag: '🇩🇲' },
    { code: 'DO', name: 'République Dominicaine', flag: '🇩🇴' },
    { code: 'EC', name: 'Équateur', flag: '🇪🇨' },
    { code: 'GD', name: 'Grenade', flag: '🇬🇩' },
    { code: 'GT', name: 'Guatemala', flag: '🇬🇹' },
    { code: 'GY', name: 'Guyana', flag: '🇬🇾' },
    { code: 'HN', name: 'Honduras', flag: '🇭🇳' },
    { code: 'HT', name: 'Haïti', flag: '🇭🇹' },
    { code: 'JM', name: 'Jamaïque', flag: '🇯🇲' },
    { code: 'KN', name: 'Saint-Kitts-et-Nevis', flag: '🇰🇳' },
    { code: 'LC', name: 'Sainte-Lucie', flag: '🇱🇨' },
    { code: 'MX', name: 'Mexique', flag: '🇲🇽' },
    { code: 'NI', name: 'Nicaragua', flag: '🇳🇮' },
    { code: 'PA', name: 'Panama', flag: '🇵🇦' },
    { code: 'PE', name: 'Pérou', flag: '🇵🇪' },
    { code: 'PY', name: 'Paraguay', flag: '🇵🇾' },
    { code: 'SR', name: 'Suriname', flag: '🇸🇷' },
    { code: 'SV', name: 'Salvador', flag: '🇸🇻' },
    { code: 'TT', name: 'Trinité-et-Tobago', flag: '🇹🇹' },
    { code: 'US', name: 'États-Unis', flag: '🇺🇸' },
    { code: 'UY', name: 'Uruguay', flag: '🇺🇾' },
    { code: 'VC', name: 'Saint-Vincent-et-les-Grenadines', flag: '🇻🇨' },
    { code: 'VE', name: 'Venezuela', flag: '🇻🇪' },
    
    // Océanie
    { code: 'AU', name: 'Australie', flag: '🇦🇺' },
    { code: 'FJ', name: 'Fidji', flag: '🇫🇯' },
    { code: 'FM', name: 'Micronésie', flag: '🇫🇲' },
    { code: 'KI', name: 'Kiribati', flag: '🇰🇮' },
    { code: 'MH', name: 'Îles Marshall', flag: '🇲🇭' },
    { code: 'NR', name: 'Nauru', flag: '🇳🇷' },
    { code: 'NZ', name: 'Nouvelle-Zélande', flag: '🇳🇿' },
    { code: 'PG', name: 'Papouasie-Nouvelle-Guinée', flag: '🇵🇬' },
    { code: 'PW', name: 'Palaos', flag: '🇵🇼' },
    { code: 'SB', name: 'Îles Salomon', flag: '🇸🇧' },
    { code: 'TO', name: 'Tonga', flag: '🇹🇴' },
    { code: 'TV', name: 'Tuvalu', flag: '🇹🇻' },
    { code: 'VU', name: 'Vanuatu', flag: '🇻🇺' },
    { code: 'WS', name: 'Samoa', flag: '🇼🇸' },
  ];

  // =============================================================================
  // SOUMISSION
  // =============================================================================
  const handleSubmit = (e) => {
    e.preventDefault();
    if (typeof onSearch === 'function') {
      onSearch({
        keyword: keyword,
        pays: country,
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
              LIGNE PRINCIPALE DE RECHERCHE (SEULEMENT)
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

        </form>
      </div>
    </div>
  );
};

export default SearchFilters;