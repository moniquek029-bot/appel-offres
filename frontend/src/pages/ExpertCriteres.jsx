// src/pages/ExpertCriteres.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

const ExpertCriteres = () => {
  const [criteres, setCriteres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newCritere, setNewCritere] = useState({ mots_cles: '', domaine: '', pays: '' });

  const domaines = ['Informatique', 'BTP', 'Santé', 'Éducation', 'Agriculture', 'Consulting', 'Autre'];
  const pays = [
    { code: 'BF', name: 'Burkina Faso' },
    { code: 'CI', name: 'Côte d\'Ivoire' },
    { code: 'SN', name: 'Sénégal' },
    { code: 'ML', name: 'Mali' },
  ];

  useEffect(() => {
    fetchCriteres();
  }, []);

  const fetchCriteres = async () => {
    try {
      const res = await api.get('/expert/criteres/');
      setCriteres(res.data.results || res.data);
    } catch (err) {
      console.error('Erreur chargement critères:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newCritere.mots_cles?.trim()) return;
    
    try {
      await api.post('/expert/criteres/', newCritere);
      setNewCritere({ mots_cles: '', domaine: '', pays: '' });
      fetchCriteres();
    } catch (err) {
      console.error('Erreur ajout critère:', err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Supprimer ce critère ?')) return;
    try {
      await api.delete(`/expert/criteres/${id}/`);
      fetchCriteres();
    } catch (err) {
      console.error('Erreur suppression:', err);
    }
  };

  if (loading) return <div className="container py-5 text-center">Chargement...</div>;

  return (
    <div className="container py-4">
      <div className="row mb-4">
        <div className="col-12">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/expert/dashboard">Dashboard</Link></li>
              <li className="breadcrumb-item active">Critères de recherche</li>
            </ol>
          </nav>
          <h2>🎯 Mes critères de recherche</h2>
          <p className="text-muted">Recevez des alertes pour les offres correspondant à vos préférences</p>
        </div>
      </div>

      {/* Formulaire d'ajout */}
      <div className="card border-0 shadow-sm mb-4">
        <div className="card-body">
          <h5 className="card-title mb-3">➕ Ajouter un critère</h5>
          <form onSubmit={handleSubmit} className="row g-3">
            <div className="col-md-5">
              <label className="form-label">Mots-clés *</label>
              <input 
                type="text" 
                className="form-control" 
                placeholder="Ex: développement web, audit..."
                value={newCritere.mots_cles}
                onChange={e => setNewCritere({...newCritere, mots_cles: e.target.value})}
                required
              />
            </div>
            <div className="col-md-3">
              <label className="form-label">Domaine</label>
              <select 
                className="form-select"
                value={newCritere.domaine}
                onChange={e => setNewCritere({...newCritere, domaine: e.target.value})}
              >
                <option value="">Tous</option>
                {domaines.map(d => <option key={d} value={d}>{d}</option>)}
              </select>
            </div>
            <div className="col-md-3">
              <label className="form-label">Pays</label>
              <select 
                className="form-select"
                value={newCritere.pays}
                onChange={e => setNewCritere({...newCritere, pays: e.target.value})}
              >
                <option value="">Tous</option>
                {pays.map(p => <option key={p.code} value={p.code}>{p.name}</option>)}
              </select>
            </div>
            <div className="col-md-1 d-flex align-items-end">
              <button type="submit" className="btn btn-primary w-100">+</button>
            </div>
          </form>
        </div>
      </div>

      {/* Liste des critères */}
      <h5 className="mb-3">📋 Vos critères actifs</h5>
      {criteres.length > 0 ? (
        <div className="list-group">
          {criteres.map(c => (
            <div key={c.id} className="list-group-item d-flex justify-content-between align-items-center">
              <div>
                <strong>{c.mots_cles}</strong>
                {c.domaine && <span className="badge bg-secondary ms-2">{c.domaine}</span>}
                {c.pays && <span className="badge bg-info ms-1">{c.pays}</span>}
              </div>
              <button 
                className="btn btn-sm btn-outline-danger"
                onClick={() => handleDelete(c.id)}
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-muted">Aucun critère défini. Ajoutez-en un ci-dessus !</p>
      )}

      <div className="mt-4">
        <Link to="/expert/dashboard" className="btn btn-outline-secondary">← Retour au dashboard</Link>
      </div>
    </div>
  );
};

export default ExpertCriteres;