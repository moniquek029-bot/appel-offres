// src/components/Notifications.jsx
import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    try {
      // Utilise l'endpoint existant pour les notifications
      const res = await api.get('/notifications/');
      setNotifications(res.data.results || res.data);
    } catch (err) {
      console.error('Erreur chargement notifications:', err);
    } finally {
      setLoading(false);
    }
  };

  const marquerLue = async (id) => {
    try {
      await api.patch(`/notifications/${id}/`, { est_lue: true });
      fetchNotifications();
    } catch (err) {
      console.error(err);
    }
  };

  const marquerToutesLues = async () => {
    try {
      const nonLues = notifications.filter(n => !n.est_lue);
      for (const notif of nonLues) {
        await api.patch(`/notifications/${notif.id}/`, { est_lue: true });
      }
      fetchNotifications();
    } catch (err) {
      console.error(err);
    }
  };

  const getTypeIcon = (objet) => {
    if (objet?.toLowerCase().includes('offre')) return '📄';
    if (objet?.toLowerCase().includes('alerte')) return '🔔';
    if (objet?.toLowerCase().includes('message')) return '💬';
    return 'ℹ️';
  };

  const nonLuesCount = notifications.filter(n => !n.est_lue).length;

  if (loading) return <div className="text-center py-4">Chargement...</div>;

  return (
    <div className="card border-0 shadow-sm">
      <div className="card-header bg-white border-0 py-3 d-flex justify-content-between align-items-center">
        <h5 className="mb-0">🔔 Mes notifications</h5>
        {nonLuesCount > 0 && (
          <button className="btn btn-sm btn-outline-primary" onClick={marquerToutesLues}>
            Tout marquer comme lu ({nonLuesCount})
          </button>
        )}
      </div>
      <div className="card-body">
        {notifications.length === 0 ? (
          <p className="text-muted text-center py-4">Aucune notification pour le moment</p>
        ) : (
          <div className="list-group">
            {notifications.map(notif => (
              <div 
                key={notif.id} 
                className={`list-group-item list-group-item-action ${!notif.est_lue ? 'bg-light' : ''}`}
                onClick={() => !notif.est_lue && marquerLue(notif.id)}
                style={{ cursor: 'pointer' }}
              >
                <div className="d-flex align-items-start">
                  <span className="fs-4 me-3">{getTypeIcon(notif.objet)}</span>
                  <div className="flex-grow-1">
                    <div className="d-flex justify-content-between align-items-center">
                      <strong>{notif.objet}</strong>
                      <small className="text-muted">
                        {new Date(notif.date_envoi).toLocaleString()}
                      </small>
                    </div>
                    <p className="mb-0 small">{notif.message}</p>
                    {notif.offre_liee && (
                      <a href={`/offres/${notif.offre_liee}`} className="small text-primary">
                        Voir l'offre concernée →
                      </a>
                    )}
                  </div>
                  {!notif.est_lue && <span className="badge bg-primary ms-2">Nouveau</span>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Notifications;