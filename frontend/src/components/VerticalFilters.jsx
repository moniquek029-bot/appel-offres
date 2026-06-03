// src/components/VerticalFilters.jsx
import React, { useState } from 'react';

const VerticalFilters = ({ onFilterChange }) => {
  const [filters, setFilters] = useState({
    domaine: '',
    localite: '',
    structure: '',
    secteur: '',
    date_debut: '',
    date_fin: '',
    max_days: ''
  });

  const domaines = [
    'Informatique',
    'BTP',
    'Santé',
    'Finance',
    'Construction',
    'Fourniture',
    'Transport',
    'Environnement',
    'Agriculture',
    'Éducation',
    'Énergie',
    'Télécommunications',
    'Logistique',
    'Autre'
  ];

  const secteurs = [
    'Public',
    'Privé',
    'Associatif',
    'International'
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

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const handleApplyFilters = () => {
    if (typeof onFilterChange === 'function') {
      onFilterChange({
        domaine: filters.domaine,
        pays: filters.localite,
        structure: filters.structure,
        secteur: filters.secteur,
        date_debut: filters.date_debut,
        date_fin: filters.date_fin,
        max_days: filters.max_days
      });
    }
  };

  const handleReset = () => {
    const resetFilters = {
      domaine: '',
      localite: '',
      structure: '',
      secteur: '',
      date_debut: '',
      date_fin: '',
      max_days: ''
    };
    setFilters(resetFilters);
    if (typeof onFilterChange === 'function') {
      onFilterChange({});
    }
  };

  return (
    <div className="card border-0 shadow-sm">
      <div className="card-header bg-white border-0 pt-3 pb-0">
        <h5 className="mb-0 fw-bold">🔍 Filtre</h5>
      </div>
      
      <div className="card-body pt-3">
        
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

        {/* Localité */}
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

        {/* Structure */}
        <div className="mb-3">
          <label className="form-label small fw-semibold text-secondary">
            Structure
          </label>
          <input
            type="text"
            name="structure"
            className="form-control form-control-sm"
            placeholder="Nom de l'organisme"
            value={filters.structure}
            onChange={handleChange}
          />
        </div>

        {/* Secteur d'activité */}
        <div className="mb-3">
          <label className="form-label small fw-semibold text-secondary">
            Secteur d'activité de la structure
          </label>
          <select
            name="secteur"
            className="form-select form-select-sm"
            value={filters.secteur}
            onChange={handleChange}
          >
            <option value="">Tous</option>
            {secteurs.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        {/* Budget Prévisionnel */}
        {/*<div className="mb-3">
          <label className="form-label small fw-semibold text-secondary">
          </label>
          <div className="row g-1">
            <div className="col-6">
              <input
                type="number"
                name="budget_min"
                className="form-control form-control-sm"
                placeholder="Min"
                value={filters.budget_min}
                onChange={handleChange}
              />
            </div>
            <div className="col-6">
              <input
                type="number"
                name="budget_max"
                className="form-control form-control-sm"
                placeholder="Max"
                value={filters.budget_max}
                onChange={handleChange}
              />
            </div>
          </div>
        </div>*/}

        {/* Date de publication */}
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
                placeholder="Du"
                value={filters.date_debut}
                onChange={handleChange}
              />
            </div>
            <div className="col-6">
              <input
                type="date"
                name="date_fin"
                className="form-control form-control-sm"
                placeholder="Au"
                value={filters.date_fin}
                onChange={handleChange}
              />
            </div>
          </div>
        </div>

        {/* Date d'expiration */}
        <div className="mb-4">
          <label className="form-label small fw-semibold text-secondary">
            Date d'expiration
          </label>
          <select
            name="max_days"
            className="form-select form-select-sm"
            value={filters.max_days || ''}
            onChange={(e) => setFilters(prev => ({ ...prev, max_days: e.target.value }))}
          >
            <option value="">Toutes</option>
            <option value="4">Dans 4 jours</option>
            <option value="2">Dans 2 jours</option>
            <option value="5">Dans 5 jours</option>
            <option value="7">Dans 7 jours</option>
            <option value="14">Dans 14 jours</option>
            <option value="30">Dans 30 jours</option>
            <option value="60">Dans 60 jours</option>
          </select>
        </div>

        <hr className="my-3" />

        <button 
          className="btn btn-primary btn-sm w-100 mb-2"
          onClick={handleApplyFilters}
        >
          🔍 Appliquer les filtres
        </button>
        
        <button 
          className="btn btn-outline-secondary btn-sm w-100"
          onClick={handleReset}
        >
          ✕ Réinitialiser
        </button>
      </div>
    </div>
  );
};

export default VerticalFilters;