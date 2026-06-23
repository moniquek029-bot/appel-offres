// src/pages/ExpertCriteres.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

const ExpertCriteres = () => {
  const [criteres, setCriteres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newCritere, setNewCritere] = useState({ mots_cles: '', pays: '' });

  useEffect(() => {
    fetchCriteres();
  }, []);

  const fetchCriteres = async () => {
    try {
      const res = await api.get('/expert/criteres/');
      setCriteres(res.data.results || res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newCritere.mots_cles?.trim()) return;
    try {
      await api.post('/expert/criteres/', newCritere);
      setNewCritere({ mots_cles: '', pays: '' });
      fetchCriteres();
    } catch (err) {
      console.error(err);
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

  if (loading) return <div className="container py-5 text-center">Chargement...</div>;

  return (
    <div className="container py-4">
      <div className="row mb-4">
        <div className="col-12">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/expert/dashboard">Dashboard</Link></li>
              <li className="breadcrumb-item active">
                <i className="bi bi-funnel-fill me-1"></i>
                Critères de recherche
              </li>
            </ol>
          </nav>
          <h2> Mes critères de recherche</h2>
        </div>
      </div>

      <div className="card border-0 shadow-sm mb-4">
        <div className="card-body">
          <h5 className="card-title mb-3">
            <i className="bi bi-funnel-fill me-1"></i>
             Ajouter un critère</h5>
          <form onSubmit={handleSubmit} className="row g-3">
            <div className="col-md-8">
              <input type="text" className="form-control" placeholder="Mots-clés (ex: informatique, audit...)" value={newCritere.mots_cles} onChange={e => setNewCritere({...newCritere, mots_cles: e.target.value})} required />
            </div>
            <div className="col-md-2">
              <select className="form-select" value={newCritere.pays} onChange={e => setNewCritere({...newCritere, pays: e.target.value})}>
                <option value="">Tous pays</option>
                <option value="BF">🇧🇫 Burkina</option>
                <option value="CI">🇨🇮 Côte d'Ivoire</option>
                <option value="SN">🇸🇳 Sénégal</option>
                <option value="ML">🇲🇱 Mali</option>
                <option value="NE">🇳🇪 Niger</option>
                <option value="TG">🇹🇬 Togo</option>
                <option value="BJ">🇧🇯 Bénin</option>
                <option value="GM">🇬🇲 Gambie</option>
                <option value="LR">🇱🇷 Libéria</option>
                <option value="SL">🇸🇱 Sierra Leone</option>
                <option value="GW">🇬🇼 Guinée-Bissau</option>
                <option value="CV">🇨🇻 Cap-Vert</option>
                <option value="NA">🇳🇦 Nigeria</option>
              </select>
            </div>
            <div className="col-md-2">
              <button type="submit" className="btn btn-primary w-100">+ Ajouter</button>
            </div>
          </form>
        </div>
      </div>

      <h5 className="mb-3"> Vos critères actifs</h5>
      {criteres.length > 0 ? (
        <div className="list-group">
          {criteres.map(c => (
            <div key={c.id} className="list-group-item d-flex justify-content-between align-items-center">
              <div>
                <strong>{c.mots_cles}</strong>
                {c.pays && <span className="badge bg-info ms-2">{c.pays}</span>}
              </div>
              <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(c.id)}>✕</button>
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