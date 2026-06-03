// src/pages/ExpertCriteres.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

const ExpertCriteres = () => {
  const { user } = useAuth();
  const [criteres, setCriteres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newCritere, setNewCritere] = useState({
    nom_critere: '',
    mots_cles: '',
    pays: 'BF',
    domaines: '',
    alerte_active: true,
    frequence: 'daily'
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const paysList = [
    { code: 'BF', name: '🇧🇫 Burkina Faso' },
    { code: 'CI', name: '🇨🇮 Côte d\'Ivoire' },
    { code: 'SN', name: '🇸🇳 Sénégal' },
    { code: 'ML', name: '🇲🇱 Mali' },
    { code: 'NE', name: '🇳🇪 Niger' },
    { code: 'TG', name: '🇹🇬 Togo' },
    { code: 'BJ', name: '🇧🇯 Bénin' },
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
    setError('');
    setSuccess('');
    
    if (!newCritere.mots_cles?.trim()) {
      setError('Veuillez entrer des mots-clés');
      return;
    }
    
    try {
      await api.post('/expert/criteres/', newCritere);
      setSuccess('✅ Critère ajouté avec succès');
      setNewCritere({
        nom_critere: '',
        mots_cles: '',
        pays: 'BF',
        domaines: '',
        alerte_active: true,
        frequence: 'daily'
      });
      fetchCriteres();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error(err);
      setError('Erreur lors de l\'ajout');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Supprimer ce critère ?')) return;
    try {
      await api.delete(`/expert/criteres/${id}/`);
      fetchCriteres();
    } catch (err) {
      console.error(err);
    }
  };

  const toggleAlerte = async (id, currentStatus) => {
    try {
      await api.patch(`/expert/criteres/${id}/`, { alerte_active: !currentStatus });
      fetchCriteres();
    } catch (err) {
      console.error(err);
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
          <p className="text-muted">Recevez des alertes pour les offres correspondant à vos critères</p>
        </div>
      </div>

      {/* Formulaire d'ajout */}
      <div className="card border-0 shadow-sm mb-4">
        <div className="card-body">
          <h5 className="card-title mb-3">➕ Ajouter un critère de recherche</h5>
          <form onSubmit={handleSubmit}>
            <div className="row g-3">
              <div className="col-md-4">
                <label className="form-label">Nom du critère</label>
                <input 
                  type="text" 
                  className="form-control" 
                  placeholder="Ex: Offres IT Burkina"
                  value={newCritere.nom_critere}
                  onChange={(e) => setNewCritere({...newCritere, nom_critere: e.target.value})}
                />
              </div>
              <div className="col-md-4">
                <label className="form-label">Mots-clés *</label>
                <input 
                  type="text" 
                  className="form-control" 
                  placeholder="informatique, développement, audit"
                  value={newCritere.mots_cles}
                  onChange={(e) => setNewCritere({...newCritere, mots_cles: e.target.value})}
                  required
                />
              </div>
              <div className="col-md-2">
                <label className="form-label">Pays</label>
                <select 
                  className="form-select"
                  value={newCritere.pays}
                  onChange={(e) => setNewCritere({...newCritere, pays: e.target.value})}
                >
                  {paysList.map(p => <option key={p.code} value={p.code}>{p.name}</option>)}
                </select>
              </div>
              <div className="col-md-2">
                <label className="form-label">Fréquence</label>
                <select 
                  className="form-select"
                  value={newCritere.frequence}
                  onChange={(e) => setNewCritere({...newCritere, frequence: e.target.value})}
                >
                  <option value="daily">📅 Quotidien</option>
                  <option value="weekly">📆 Hebdomadaire</option>
                </select>
              </div>
              <div className="col-md-12">
                <label className="form-label">Domaines recherchés</label>
                <input 
                  type="text" 
                  className="form-control" 
                  placeholder="Informatique, BTP, Santé, Finance..."
                  value={newCritere.domaines}
                  onChange={(e) => setNewCritere({...newCritere, domaines: e.target.value})}
                />
              </div>
              <div className="col-12">
                <div className="form-check form-switch">
                  <input 
                    className="form-check-input" 
                    type="checkbox" 
                    id="alerteActive"
                    checked={newCritere.alerte_active}
                    onChange={(e) => setNewCritere({...newCritere, alerte_active: e.target.checked})}
                  />
                  <label className="form-check-label" htmlFor="alerteActive">
                    🔔 Activer les alertes email pour ce critère
                  </label>
                </div>
              </div>
              <div className="col-12">
                {error && <div className="alert alert-danger small">{error}</div>}
                {success && <div className="alert alert-success small">{success}</div>}
                <button type="submit" className="btn btn-primary">➕ Ajouter</button>
              </div>
            </div>
          </form>
        </div>
      </div>

      {/* Liste des critères */}
      <h5 className="mb-3">📋 Mes critères actifs</h5>
      {criteres.length > 0 ? (
        <div className="list-group">
          {criteres.map(c => (
            <div key={c.id} className="list-group-item">
              <div className="d-flex justify-content-between align-items-start">
                <div className="flex-grow-1">
                  <div className="d-flex align-items-center gap-2 mb-1">
                    <strong>{c.nom_critere || c.mots_cles}</strong>
                    <span className={`badge ${c.alerte_active ? 'bg-success' : 'bg-secondary'}`}>
                      {c.alerte_active ? '🔔 Alertes actives' : '🔕 Alertes désactivées'}
                    </span>
                    <span className="badge bg-info">{c.frequence === 'daily' ? '📅 Quotidien' : '📆 Hebdomadaire'}</span>
                  </div>
                  <p className="mb-1 small">
                    <strong>Mots-clés:</strong> {c.mots_cles}
                  </p>
                  {c.pays && <p className="mb-1 small"><strong>Pays:</strong> {paysList.find(p => p.code === c.pays)?.name || c.pays}</p>}
                  {c.domaines && <p className="mb-0 small"><strong>Domaines:</strong> {c.domaines}</p>}
                </div>
                <div className="d-flex gap-2">
                  <button 
                    className={`btn btn-sm ${c.alerte_active ? 'btn-outline-warning' : 'btn-outline-success'}`}
                    onClick={() => toggleAlerte(c.id, c.alerte_active)}
                    title={c.alerte_active ? 'Désactiver les alertes' : 'Activer les alertes'}
                  >
                    {c.alerte_active ? '🔕' : '🔔'}
                  </button>
                  <button 
                    className="btn btn-sm btn-outline-danger"
                    onClick={() => handleDelete(c.id)}
                  >
                    ✕
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="alert alert-info">
          Aucun critère défini. Ajoutez-en un ci-dessus !
        </div>
      )}

      <div className="mt-4">
        <Link to="/expert/dashboard" className="btn btn-outline-secondary">← Retour au dashboard</Link>
      </div>
    </div>
  );
};

export default ExpertCriteres;