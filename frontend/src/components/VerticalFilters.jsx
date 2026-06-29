// src/components/VerticalFilters.jsx
import React, { useState, useEffect } from 'react';

const VerticalFilters = ({ onFilterChange, initialValues = {} }) => {
  // ✅ Initialiser avec les valeurs de l'URL
  const [filters, setFilters] = useState({
    domaine: initialValues.domaine || '',
    localite: initialValues.pays || '',
    structure: initialValues.structure || '',
    date_publication: initialValues.date_publication || '',
    max_days: initialValues.max_days || '',
  });

  // ✅ Synchroniser quand initialValues change (au retour depuis JobDetail)
  useEffect(() => {
    setFilters({
      domaine: initialValues.domaine || '',
      localite: initialValues.pays || '',
      structure: initialValues.structure || '',
      date_publication: initialValues.date_publication || '',
      max_days: initialValues.max_days || '',
    });
  }, [
    initialValues.domaine, 
    initialValues.pays, 
    initialValues.structure, 
    initialValues.date_publication, 
    initialValues.max_days
  ]);

  const domaines = [
    'IT & Digital',
    'Ingénierie & Construction',
    'Santé & Médical',
    'Éducation & Formation',
    'Environnement & Climat',
    'Finance & Comptabilité',
    'Management & Administration',
    'Transport & Logistique',
    'Agriculture & Alimentation',
    'Eau & Assainissement',
    'Communication & Médias',
    'Juridique & Droit',
    'Ressources Humaines',
    'Sécurité & Protection',
    'Social & Égalité',
    'Biens & Équipements',
    'Services & Conseil',
    'Autres',
  ];

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
    { code: 'AR', name: 'Argentine', flag: '🇦🇷' },
    { code: 'ID', name: 'Indonésie', flag: '🇮🇩' },
    { code: 'BA', name: 'Bosnie-Herzégovine', flag: '🇧🇦' },
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    const updatedFilters = { ...filters, [name]: value };
    setFilters(updatedFilters);
    
    if (typeof onFilterChange === 'function') {
      onFilterChange({
        domaine: updatedFilters.domaine,
        pays: updatedFilters.localite,
        structure: updatedFilters.structure,
        date_publication: updatedFilters.date_publication,
        max_days: updatedFilters.max_days,
        // ✅ IMPORTANT : on préserve le keyword et le pays du SearchFilters
        keyword: initialValues.keyword || '',
      });
    }
  };

  const handleReset = () => {
    const resetFilters = {
      domaine: '',
      localite: '',
      structure: '',
      date_publication: '',
      max_days: '',
      keyword: '',
      pays: '',
    };
    setFilters({
      domaine: '', localite: '', structure: '', date_publication: '', max_days: ''
    });
    if (typeof onFilterChange === 'function') {
      onFilterChange(resetFilters);
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
        <div className="mb-3">
          <label className="form-label small fw-semibold text-secondary">
            Domaine de l'appel d'offre
          </label>
          <select name="domaine" className="form-select form-select-sm" value={filters.domaine} onChange={handleChange}>
            <option value="">Tous</option>
            {domaines.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
        </div>

        <div className="mb-3">
          <label className="form-label small fw-semibold text-secondary">Localité</label>
          <select name="localite" className="form-select form-select-sm" value={filters.localite} onChange={handleChange}>
            <option value="">Toutes</option>
            {paysList.map(p => <option key={p.code} value={p.code}>{p.flag} {p.name}</option>)}
          </select>
        </div>

        <div className="mb-3">
          <label className="form-label small fw-semibold text-secondary">Structure</label>
          <select name="structure" className="form-select form-select-sm" value={filters.structure} onChange={handleChange}>
            <option value="">Toutes</option>
            <option value="nationale">🇫 Nationale</option>
            <option value="internationale">🌍 Internationale</option>
          </select>
        </div>

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
        </div>

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
        </div>

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