import React, { useState, useEffect } from 'react';

const VerticalFilters = ({ onFilterChange, initialValues = {} }) => {
  const [filters, setFilters] = useState({
    domaine: initialValues.domaine || '',
    localite: initialValues.pays || '',
    structure: initialValues.structure || '',
    date_publication: initialValues.date_publication || '',
    max_days: initialValues.max_days || '',
  });

  const [showDomaineList, setShowDomaineList] = useState(false);
  const [showPaysList, setShowPaysList] = useState(false);
  const [searchDomaine, setSearchDomaine] = useState('');
  const [searchPays, setSearchPays] = useState('');

  useEffect(() => {
    setFilters({
      domaine: initialValues.domaine || '',
      localite: initialValues.pays || '',
      structure: initialValues.structure || '',
      date_publication: initialValues.date_publication || '',
      max_days: initialValues.max_days || '',
    });
  }, [
    initialValues.domaine, initialValues.pays, initialValues.structure, 
    initialValues.date_publication, initialValues.max_days
  ]);

  const domaines = [
    'IT & Digital', 'Ingénierie & Construction', 'Santé & Médical',
    'Éducation & Formation', 'Environnement & Climat', 'Finance & Comptabilité',
    'Management & Administration', 'Transport & Logistique', 'Agriculture & Alimentation',
    'Eau & Assainissement', 'Communication & Médias', 'Juridique & Droit',
    'Ressources Humaines', 'Sécurité & Protection', 'Social & Égalité',
    'Biens & Équipements', 'Services & Conseil', 'Autres',
  ];

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

  const filteredDomaines = domaines.filter(d => d.toLowerCase().includes(searchDomaine.toLowerCase()));
  const filteredPays = paysList.filter(p => p.name.toLowerCase().includes(searchPays.toLowerCase()));

  const handleChange = (key, value) => {
    const updatedFilters = { ...filters, [key]: value };
    setFilters(updatedFilters);
    
    if (typeof onFilterChange === 'function') {
      onFilterChange({
        domaine: updatedFilters.domaine,
        pays: updatedFilters.localite, // ✅ Mapping crucial pour le backend
        structure: updatedFilters.structure,
        date_publication: updatedFilters.date_publication,
        max_days: updatedFilters.max_days,
        keyword: initialValues.keyword || '',
      });
    }
  };

  const handleReset = () => {
    const resetFilters = {
      domaine: '', localite: '', structure: '', date_publication: '', max_days: ''
    };
    setFilters(resetFilters);
    setSearchDomaine('');
    setSearchPays('');
    setShowDomaineList(false);
    setShowPaysList(false);
    
    if (typeof onFilterChange === 'function') {
      // ✅ CORRECTION : On envoie la structure complète attendue par le parent, pas juste resetFilters
      onFilterChange({
        domaine: '',
        pays: '', // ✅ Réinitialise le pays pour le backend
        structure: '',
        date_publication: '',
        max_days: '',
        keyword: initialValues.keyword || '',
      });
    }
  };

  useEffect(() => {
    const handleClickOutside = () => {
      setShowDomaineList(false);
      setShowPaysList(false);
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  return (
    <div className="card border-0 shadow-sm" style={{ borderRadius: 'var(--radius-lg)' }}>
      <div className="card-header bg-white border-0 pt-3 pb-0">
        <h5 className="mb-0 fw-bold"><i className="bi bi-funnel me-2"></i>Filtres</h5>
      </div>
      <div className="card-body pt-3">
        {/* DOMAINE */}
        <div className="mb-3" onClick={(e) => e.stopPropagation()}>
          <label className="form-label small fw-semibold text-secondary">Domaine de l'appel d'offre</label>
          <div className="position-relative">
            <div className="input-group input-group-sm">
              <span className="input-group-text bg-white border-end-0"><i className="bi bi-search text-muted"></i></span>
              <input type="text" className="form-control border-start-0" placeholder={filters.domaine || "Rechercher un domaine..."}
                value={searchDomaine} onChange={(e) => { setSearchDomaine(e.target.value); setShowDomaineList(true); }}
                onFocus={() => setShowDomaineList(true)} onClick={(e) => e.stopPropagation()} />
              {filters.domaine && (
                <button className="btn btn-sm btn-outline-secondary border-start-0" onClick={() => { handleChange('domaine', ''); setSearchDomaine(''); }}>
                  <i className="bi bi-x"></i>
                </button>
              )}
            </div>
            {showDomaineList && (filteredDomaines.length > 0 || searchDomaine) && (
              <div className="position-absolute w-100 mt-1" style={{ zIndex: 1000 }}>
                <div className="card shadow-sm border" style={{ maxHeight: '250px', overflowY: 'auto' }}>
                  <div className={`list-group-item list-group-item-action cursor-pointer ${!filters.domaine ? 'active' : ''}`}
                    onClick={() => { handleChange('domaine', ''); setSearchDomaine(''); setShowDomaineList(false); }}>
                    <small className="text-muted">Tous les domaines</small>
                  </div>
                  {filteredDomaines.map((domaine) => (
                    <div key={domaine} className={`list-group-item list-group-item-action cursor-pointer ${filters.domaine === domaine ? 'active' : ''}`}
                      onClick={() => { handleChange('domaine', domaine); setSearchDomaine(domaine); setShowDomaineList(false); }}>
                      {domaine}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* LOCALITÉ */}
        <div className="mb-3" onClick={(e) => e.stopPropagation()}>
          <label className="form-label small fw-semibold text-secondary">Localité</label>
          <div className="position-relative">
            <div className="input-group input-group-sm">
              <span className="input-group-text bg-white border-end-0"><i className="bi bi-search text-muted"></i></span>
              <input type="text" className="form-control border-start-0" placeholder={filters.localite ? paysList.find(p => p.code === filters.localite)?.name || "Rechercher un pays..." : "Rechercher un pays..."}
                value={searchPays} onChange={(e) => { setSearchPays(e.target.value); setShowPaysList(true); }}
                onFocus={() => setShowPaysList(true)} onClick={(e) => e.stopPropagation()} />
              {filters.localite && (
                <button className="btn btn-sm btn-outline-secondary border-start-0" onClick={() => { handleChange('localite', ''); setSearchPays(''); }}>
                  <i className="bi bi-x"></i>
                </button>
              )}
            </div>
            {showPaysList && (filteredPays.length > 0 || searchPays) && (
              <div className="position-absolute w-100 mt-1" style={{ zIndex: 1000 }}>
                <div className="card shadow-sm border" style={{ maxHeight: '250px', overflowY: 'auto' }}>
                  <div className={`list-group-item list-group-item-action cursor-pointer ${!filters.localite ? 'active' : ''}`}
                    onClick={() => { handleChange('localite', ''); setSearchPays(''); setShowPaysList(false); }}>
                    <small className="text-muted">Toutes les localités</small>
                  </div>
                  {filteredPays.map((pays) => (
                    <div key={pays.code} className={`list-group-item list-group-item-action cursor-pointer ${filters.localite === pays.code ? 'active' : ''}`}
                      onClick={() => { handleChange('localite', pays.code); setSearchPays(pays.name); setShowPaysList(false); }}>
                      {pays.flag} {pays.name}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* STRUCTURE */}
        <div className="mb-3">
          <label className="form-label small fw-semibold text-secondary">Structure</label>
          <select className="form-select form-select-sm" value={filters.structure || ''} onChange={(e) => handleChange('structure', e.target.value)}>
            <option value="">Toutes les structures</option>
          </select>
        </div>
        
        {/* DATES */}
        <div className="mb-3">
          <label className="form-label small fw-semibold text-secondary"><i className="bi bi-calendar-check me-1"></i>Publié le</label>
          <input type="date" className="form-control form-control-sm" value={filters.date_publication} onChange={(e) => handleChange('date_publication', e.target.value)} />
        </div>
        <div className="mb-4">
          <label className="form-label small fw-semibold text-secondary"><i className="bi bi-clock-history me-1"></i>Expire dans</label>
          <select className="form-select form-select-sm" value={filters.max_days} onChange={(e) => handleChange('max_days', e.target.value)}>
            <option value="">Toutes</option>
            <option value="7">7 jours</option><option value="14">14 jours</option>
            <option value="30">30 jours</option><option value="60">60 jours</option>
          </select>
        </div>

        <button className="btn btn-outline-secondary btn-sm w-100 mb-2" onClick={handleReset} style={{ borderRadius: 'var(--radius-pill)' }}>
          <i className="bi bi-arrow-counterclockwise me-1"></i>Réinitialiser les filtres
        </button>
      </div>
    </div>
  );
};

export default VerticalFilters;