import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';

const JobDetail = () => {
  const { id } = useParams();
  const [offre, setOffre] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get(`/offres/${id}/`).then(res => setOffre(res.data)).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="container py-5 text-center"><div className="spinner-border" /></div>;
  if (!offre) return <div className="container py-5 text-danger">Offre non trouvée</div>;

  return (
    <div className="container py-4">
      <Link to="/" className="btn btn-outline-secondary mb-3">← Retour aux offres</Link>
      <div className="card shadow-sm">
        <div className="card-header bg-primary text-white">
          <h3>{offre.titre}</h3>
        </div>
        <div className="card-body">
          <div className="row mb-3">
            <div className="col-md-6"><p><strong>Organisme :</strong> {offre.organisme}</p></div>
            <div className="col-md-6"><p><strong>Clôture :</strong> {new Date(offre.date_cloture).toLocaleDateString('fr-FR')}</p></div>
          </div>
          <h5>Description</h5>
          <p style={{ whiteSpace: 'pre-line' }}>{offre.description}</p>
          <hr/>
          <div className="d-flex gap-3">
            {offre.url_tdr && (
              <a href={offre.url_tdr} target="_blank" rel="noopener noreferrer" className="btn btn-lg btn-primary">🔗 Voir le TDR officiel</a>
            )}
            <button className="btn btn-lg btn-outline-primary">💾 Sauvegarder l'offre</button>
          </div>
        </div>
        <div className="card-footer text-muted small">Conforme CDC Section IV.3 : Métadonnées uniquement • Redirection vers source officielle</div>
      </div>
    </div>
  );
};

export default JobDetail;