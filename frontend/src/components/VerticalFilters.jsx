// =============================================================================
// FICHIER: src/components/VerticalFilters.jsx
// MODIFICATION: Toggle "Voir plus/moins" + Scroll fluide vers filtres avancés
// ENTREPRISE: EXPERTISE-ID
// =============================================================================

import React, { useState, useEffect, useRef } from 'react';

const VerticalFilters = ({ onFilterChange }) => {
  // =============================================================================
  // ÉTAT 1: Contrôler l'affichage des FILTRES AVANCÉS (toggle "Voir plus")
  // =============================================================================
  const [showAdvanced, setShowAdvanced] = useState(false); // false = masqués par défaut
  
  // =============================================================================
  // ÉTAT 2: Référence pour le scroll fluide vers la section avancée
  // =============================================================================
  const advancedSectionRef = useRef(null);

  // =============================================================================
  // ÉTAT 3: Stocker les valeurs des filtres (inchangé)
  // =============================================================================
  const [filters, setFilters] = useState({
    domaine: '',
    localite: '',      // Correspond au champ "pays" dans l'API
    structure: '',
    /*secteur: ''*/
    date_debut: '',
    date_fin: '',
    max_days: ''
  });

  // =============================================================================
  // LISTES POUR LES SELECTS (inchangées)
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
  // FONCTION 1: Gérer le changement d'un champ + AUTO-UPDATE immédiat (inchangé)
  // =============================================================================
  const handleChange = (e) => {
    const { name, value } = e.target;
    
    // 1. Mettre à jour l'état local
    setFilters(prev => ({ ...prev, [name]: value }));
    
    // 2. ✅ AUTO-UPDATE: Appeler immédiatement le parent avec les nouveaux filtres
    if (typeof onFilterChange === 'function') {
      const newFilters = {
        domaine: name === 'domaine' ? value : filters.domaine,
        pays: name === 'localite' ? value : filters.localite,  // ⚠️ "localite" → "pays" pour l'API
        structure: name === 'structure' ? value : filters.structure,
        date_debut: name === 'date_debut' ? value : filters.date_debut,
        date_fin: name === 'date_fin' ? value : filters.date_fin,
        max_days: name === 'max_days' ? value : filters.max_days
      };
      onFilterChange(newFilters);
    }
  };

  // =============================================================================
  // FONCTION 2: Réinitialiser TOUS les filtres + recharger automatiquement (inchangé)
  // =============================================================================
  const handleReset = () => {
    // 1. Réinitialiser l'état local
    const resetFilters = {
      domaine: '',
      localite: '',
      structure: '',
      date_debut: '',
      date_fin: '',
      max_days: ''
    };
    setFilters(resetFilters);
    
    // 2. ✅ AUTO-UPDATE: Appeler le parent avec des filtres vides (recharge tout)
    if (typeof onFilterChange === 'function') {
      onFilterChange({}); // Objet vide = tous les filtres désactivés
    }
  };

  // =============================================================================
  // ✅ NOUVELLE FONCTION: Toggle "Voir plus/moins" + Scroll fluide vers section avancée
  // =============================================================================
  const toggleAdvanced = () => {
    const newState = !showAdvanced;
    setShowAdvanced(newState);
    
    // ✅ Si on OUVRE la section avancée → scroll fluide vers elle
    if (newState && advancedSectionRef.current) {
      // Petit délai pour que l'animation CSS commence avant le scroll
      setTimeout(() => {
        advancedSectionRef.current.scrollIntoView({ 
          behavior: 'smooth',  // ✅ Scroll fluide (comme ton exemple rouge)
          block: 'nearest'     // Scroll minimal pour amener la section en vue
        });
      }, 150);
    }
  };

  // =============================================================================
  // RENDU DU COMPOSANT
  // =============================================================================
  return (
    <div className="card border-0 shadow-sm" style={{ borderRadius: 'var(--radius-lg)' }}>
      
      {/* =============================================================================
          EN-TÊTE: Titre (inchangé)
          ============================================================================= */}
      <div className="card-header bg-white border-0 pt-3 pb-0">
        <h5 className="mb-0 fw-bold"> Filtres</h5>
      </div>
      
      <div className="card-body pt-3">


        
        
        {/* =============================================================================
            SECTION 1: FILTRES DE BASE (toujours visibles - comme ton exemple vert)
            ============================================================================= */}
        
        {/* Domaine */}
        <div className="mb-3">
          <label className="form-label small fw-semibold text-secondary">
            Domaine de l'appel d'offre
          </label>
          <select
            name="domaine"
            className="form-select form-select-sm"
            value={filters.domaine}
            onChange={handleChange}
          >
            <option value="">Tous</option>
            {domaines.map(d => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </div>

        {/* Localité / Pays */}
        <div className="mb-3">
          <label className="form-label small fw-semibold text-secondary">
            Localité
          </label>
          <select
            name="localite"
            className="form-select form-select-sm"
            value={filters.localite}
            onChange={handleChange}
          >
            <option value="">Toutes</option>
            {paysList.map(p => (
              <option key={p.code} value={p.code}>{p.name}</option>
            ))}
          </select>
        </div>

         <div className="mb-3">
          <label className="form-label small fw-semibold text-secondary">
            Structure
          </label>
          <select
            name="structure"
            className="form-select form-select-sm"
            value={filters.structure}
            onChange={handleChange}
          >
            <option value="">Toutes</option>
            {structuresList.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>


        
         {/* Dates de publication */}
          <div className="mb-3">
            <label className="form-label small fw-semibold text-secondary">
              Date de publication
            </label>
            <div className="row g-1">
              <div className="col-6">
                <input
                  type="date"
                  name="date_debut"
                  className="form-control form-control-sm"
                  value={filters.date_debut}
                  onChange={handleChange}  // ✅ Auto-update
                />
              </div>
              <div className="col-6">
                <input
                  type="date"
                  name="date_fin"
                  className="form-control form-control-sm"
                  value={filters.date_fin}
                  onChange={handleChange}  // ✅ Auto-update
                />
              </div>
            </div>
          </div>


            {/* Date d'expiration (délai max) */}
          <div className="mb-4">
            <label className="form-label small fw-semibold text-secondary">
              Date d'expiration
            </label>
            <select
              name="max_days"
              className="form-select form-select-sm"
              value={filters.max_days}
              onChange={handleChange}  // ✅ Auto-update
            >
              <option value="">Toutes</option>
              <option value="2">Dans 2 jours</option>
              <option value="4">Dans 4 jours</option>
              <option value="5">Dans 5 jours</option>
              <option value="7">Dans 7 jours</option>
              <option value="14">Dans 14 jours</option>
              <option value="30">Dans 30 jours</option>
              <option value="60">Dans 60 jours</option>
            </select>
          </div>

         {/* <hr className="my-3" />
        

        <hr className="my-3" />*/}

        {/* =============================================================================
            BOUTONS D'ACTION (inchangés)
            ============================================================================= */}
        
        {/* ✅ Bouton Réinitialiser: vide les filtres ET recharge automatiquement */}
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