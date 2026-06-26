import React, { useState } from 'react';

const VerticalFilters = ({ onFilterChange }) => {
  // =============================================================================
  // ÉTAT 1: Stocker les valeurs des filtres
  // =============================================================================
  const [filters, setFilters] = useState({
    domaine: '',
    localite: '',
    structure: '',
    date_publication: '',     
    //date_cloture: '',         
    max_days: ''
  });

  // =============================================================================
  // LISTES POUR LES SELECTS
  // =============================================================================
  const domaines = [
    'Informatique', 'BTP', 'Santé', 'Finance', 'Construction',
    'Fourniture', 'Transport', 'Environnement', 'Agriculture',
    'Éducation', 'Énergie', 'Télécommunications', 'Logistique', 'Autre'
  ];

  const paysList = [
    { code: 'BF', name: 'Burkina Faso' },
    { code: 'CI', name: 'Côte d\'Ivoire' },
    { code: 'SN', name: 'Sénégal' },
    { code: 'ML', name: 'Mali' },
    { code: 'NE', name: 'Niger' },
    { code: 'TG', name: 'Togo' },
    { code: 'BJ', name: 'Bénin' },
    { code: 'CM', name: 'Cameroun' },
    { code: 'CD', name: 'Congo' },
    { code: 'RW', name: 'Rwanda' }, 
    { code: 'GA', name: 'Gabon' },
    { code: 'NG', name: 'Nigeria' },
    { code: 'LR', name: 'Liberia' }
  ];

  const structuresList = [
    'UNFPA - Fonds des Nations Unies pour la Population',
    'UNDP - Programme des Nations Unies pour le Développement',
    'UEMOA - Union Économique et Monétaire Ouest Africaine',
    'AGETIB - Agence d\'Exécution des Travaux d\'Intérêt Public',
    'SONABEL - Société Nationale d\'Électricité du Burkina',
    'Banque Mondiale',
    'Banque Africaine de Développement',
    'Union Européenne',
    'Gouvernement du Burkina Faso',
    'Ministères',
    'Collectivités locales',
    'Entreprises privées',
    'ONG',
    'Autre'
  ];

  // =============================================================================
  // FONCTION 1: Gérer le changement d'un champ + AUTO-UPDATE immédiat
  // =============================================================================
  const handleChange = (e) => {
    const { name, value } = e.target;
    
    const updatedFilters = { ...filters, [name]: value };
    setFilters(updatedFilters);
    
    if (typeof onFilterChange === 'function') {
      // ✅ Envoi des paramètres avec les BONS NOMS attendus par le backend
      onFilterChange({
        domaine: updatedFilters.domaine,
        pays: updatedFilters.localite,
        structure: updatedFilters.structure,
        date_publication: updatedFilters.date_publication,  // ✅ Nom correct
        //date_cloture: updatedFilters.date_cloture,          // ✅ Nom correct
        max_days: updatedFilters.max_days
      });
    }
  };

  // =============================================================================
  // FONCTION 2: Réinitialiser TOUS les filtres
  // =============================================================================
  const handleReset = () => {
    const resetFilters = {
      domaine: '',
      localite: '',
      structure: '',
      date_publication: '',
      //date_cloture: '',
      max_days: ''
    };
    setFilters(resetFilters);
    
    if (typeof onFilterChange === 'function') {
      onFilterChange({});
    }
  };

  return (
    <div className="card border-0 shadow-sm" style={{ borderRadius: 'var(--radius-lg)' }}>
      
      <div className="card-header bg-white border-0 pt-3 pb-0">
        <h5 className="mb-0 fw-bold">
          <i className="bi bi-funnel me-2"></i>
          Filtres
        </h5>
      </div>
      
      <div className="card-body pt-3">

        {/* Domaine */}
        <div className="mb-3">
          <label className="form-label small fw-semibold text-secondary">
            Domaine de l'appel d'offre
          </label>
          <select name="domaine" className="form-select form-select-sm" value={filters.domaine} onChange={handleChange}>
            <option value="">Tous</option>
            {domaines.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
        </div>

        {/* Localité / Pays */}
        <div className="mb-3">
          <label className="form-label small fw-semibold text-secondary">Localité</label>
          <select name="localite" className="form-select form-select-sm" value={filters.localite} onChange={handleChange}>
            <option value="">Toutes</option>
            {paysList.map(p => <option key={p.code} value={p.code}>{p.name}</option>)}
          </select>
        </div>

        {/* Structure - Champ texte libre */}
        <div className="mb-3">
          <label className="form-label small fw-semibold text-secondary">Structure</label>
          <input 
            type="text" 
            className="form-control form-control-sm" 
            placeholder="Toutes"
            name="structure"
            value={filters.structure}
            onChange={handleChange}
          />
          <small className="text-muted">Laissez vide pour toutes les structures</small>
        </div>

        {/* ✅ Date de publication (filtre sur le jour exact) */}
        <div className="mb-3">
          <label className="form-label small fw-semibold text-secondary">
            <i className="bi bi-calendar-check me-1"></i>
            Publié le
          </label>
          <input
            type="date"
            name="date_publication"
            className="form-control form-control-sm"
            value={filters.date_publication}
            onChange={handleChange}
          />
          {/*<small className="text-muted">Filtrer par date exacte de publication</small>*/}
        </div>

        {/* ✅ NOUVEAU : Date de clôture spécifique */}
        {/*<div className="mb-3">
          <label className="form-label small fw-semibold text-secondary">
            <i className="bi bi-calendar-event me-1"></i>
            Clôture avant le
          </label>
          <input
            type="date"
            name="date_cloture"
            className="form-control form-control-sm"
            value={filters.date_cloture}
            onChange={handleChange}
          />
          <small className="text-muted">Offres qui expirent avant cette date</small>
        </div>*/}

        {/* Date d'expiration (dans X jours) */}
        <div className="mb-4">
          <label className="form-label small fw-semibold text-secondary">
            <i className="bi bi-clock-history me-1"></i>
            Expire dans
          </label>
          <select name="max_days" className="form-select form-select-sm" value={filters.max_days} onChange={handleChange}>
            <option value="">Toutes</option>
            <option value="2">2 jours</option>
            <option value="4">4 jours</option>
            <option value="5">5 jours</option>
            <option value="7">7 jours</option>
            <option value="14">14 jours</option>
            <option value="30">30 jours</option>
            <option value="60">60 jours</option>
          </select>
          {/*<small className="text-muted">Offres expirant dans X jours</small>*/}
        </div>

        {/* Bouton Réinitialiser */}
        <button 
          className="btn btn-outline-secondary btn-sm w-100 mb-2"
          onClick={handleReset}
          style={{ borderRadius: 'var(--radius-pill)' }}
        >
          <i className="bi bi-arrow-counterclockwise me-1"></i>
          Réinitialiser les filtres
        </button>
      </div>
    </div>
  );
};

export default VerticalFilters;