// src/pages/Notifications.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const Notifications = () => {
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [confirmDeleteAll, setConfirmDeleteAll] = useState(false);

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    try {
      const res = await api.get('/notifications/');
      console.log('📬 Notifications reçues:', res.data);
      
      if (res.data.results) {
        setNotifications(res.data.results);
      } else if (Array.isArray(res.data)) {
        setNotifications(res.data);
      } else {
        setNotifications([]);
      }
    } catch (err) {
      console.error('❌ Erreur chargement notifications:', err);
      setNotifications([]);
    } finally {
      setLoading(false);
    }
  };

  const marquerLue = async (id) => {
    try {
      await api.post(`/notifications/${id}/marquer-lue/`);
      fetchNotifications();
    } catch (err) {
      console.error(err);
    }
  };

  const marquerToutesLues = async () => {
    try {
      const nonLues = notifications.filter(n => !n.est_lue);
      for (const notif of nonLues) {
        await api.post(`/notifications/${notif.id}/marquer-lue/`);
      }
      fetchNotifications();
    } catch (err) {
      console.error(err);
    }
  };

  //  : Supprimer une notification
  const supprimerNotification = async (id) => {
    if (!window.confirm('Supprimer cette notification ?')) return;
    
    try {
      await api.delete(`/notifications/${id}/supprimer/`);
      setNotifications(notifications.filter(n => n.id !== id));
    } catch (err) {
      console.error('❌ Erreur suppression:', err);
    }
  };

  //  Tout supprimer
  const toutSupprimer = async () => {
    if (!confirmDeleteAll) {
      setConfirmDeleteAll(true);
      setTimeout(() => setConfirmDeleteAll(false), 5000);
      return;
    }

    try {
      await api.delete('/notifications/tout-supprimer/');
      setNotifications([]);
      setConfirmDeleteAll(false);
    } catch (err) {
      console.error('❌ Erreur suppression totale:', err);
    }
  };

  const getTypeIcon = (objet) => {
    if (objet?.toLowerCase().includes('message')) {
      return { icon: 'bi-chat-dots-fill', color: '#3B82F6' };
    }
    if (objet?.toLowerCase().includes('suggestion')) {
      return { icon: 'bi-lightbulb-fill', color: '#F59E0B' };
    }
    if (objet?.toLowerCase().includes('offre')) {
      return { icon: 'bi-briefcase-fill', color: '#10B981' };
    }
    return { icon: 'bi-bell-fill', color: '#6B7280' };
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const nonLuesCount = notifications.filter(n => !n.est_lue).length;

  if (loading) {
    return (
      <div className="container py-5 text-center">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Chargement...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container py-4">
      {/* En-tête avec boutons */}
      <div className="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
        <h3 className="mb-0">
          <i className="bi bi-bell me-2"></i>
          Mes notifications
          {notifications.length > 0 && (
            <span className="badge bg-primary ms-2" style={{ fontSize: '0.9rem' }}>
              {notifications.length}
            </span>
          )}
        </h3>
        
        <div className="d-flex gap-2 flex-wrap">
          {nonLuesCount > 0 && (
            <button 
              className="btn btn-outline-primary btn-sm"
              onClick={marquerToutesLues}
            >
              <i className="bi bi-check2-all me-1"></i>
              Tout marquer comme lu ({nonLuesCount})
            </button>
          )}
          
          {/* ✅ BOUTON TOUT SUPPRIMER */}
          {notifications.length > 0 && (
            <button 
              className={`btn btn-sm ${confirmDeleteAll ? 'btn-danger' : 'btn-outline-danger'}`}
              onClick={toutSupprimer}
            >
              <i className="bi bi-trash me-1"></i>
              {confirmDeleteAll ? 'Confirmer la suppression ?' : 'Tout supprimer'}
            </button>
          )}
          
          {/* BOUTON FERMER */}
          <button 
            className="btn btn-outline-secondary btn-sm"
            onClick={() => navigate(-1)}
            title="Retour"
          >
            <i className="bi bi-x-lg me-1"></i>
            Fermer
          </button>
        </div>
      </div>

      <div className="card border-0 shadow-sm">
        <div className="card-body">
          {notifications.length === 0 ? (
            <div className="text-center py-5">
              <i className="bi bi-bell-slash text-muted" style={{ fontSize: '4rem' }}></i>
              <p className="text-muted mt-3 mb-0">Aucune notification pour le moment</p>
            </div>
          ) : (
            <div className="list-group list-group-flush">
              {notifications.map(notif => {
                const { icon, color } = getTypeIcon(notif.objet);
                return (
                  <div 
                    key={notif.id} 
                    className={`list-group-item border-0 ${!notif.est_lue ? 'bg-light' : ''}`}
                    style={{ 
                      transition: 'all 0.2s',
                      borderRadius: '8px',
                      marginBottom: '8px'
                    }}
                  >
                    <div className="d-flex align-items-start gap-3">
                      {/* Icône cliquable pour marquer comme lu */}
                      <div 
                        className="d-flex align-items-center justify-content-center rounded-circle flex-shrink-0"
                        style={{ 
                          width: '45px',
                          height: '45px',
                          backgroundColor: `${color}20`,
                          color: color,
                          cursor: !notif.est_lue ? 'pointer' : 'default'
                        }}
                        onClick={() => !notif.est_lue && marquerLue(notif.id)}
                        title={!notif.est_lue ? 'Marquer comme lu' : ''}
                      >
                        <i className={`bi ${icon}`} style={{ fontSize: '1.25rem' }}></i>
                      </div>
                      
                      {/* Contenu de la notification */}
                      <div className="flex-grow-1">
                        <div className="d-flex justify-content-between align-items-start mb-1">
                          <h6 className="mb-0 fw-bold" style={{ fontSize: '0.95rem' }}>
                            {!notif.est_lue && (
                              <span 
                                className="d-inline-block rounded-circle me-2"
                                style={{ 
                                  width: '8px',
                                  height: '8px',
                                  backgroundColor: '#3B82F6'
                                }}
                              />
                            )}
                            {notif.objet}
                          </h6>
                          <small className="text-muted ms-2" style={{ fontSize: '0.8rem' }}>
                            {formatDate(notif.date_envoi)}
                          </small>
                        </div>
                        <p className="mb-2 text-muted" style={{ fontSize: '0.9rem' }}>
                          {notif.message}
                        </p>
                        
                        {/* Actions */}
                        <div className="d-flex gap-2 align-items-center flex-wrap">
                          {notif.offre_liee && (
                            <button 
                              className="btn btn-sm btn-link p-0"
                              onClick={(e) => {
                                e.stopPropagation();
                                navigate(`/offres/${notif.offre_liee}`);
                              }}
                              style={{
                                color: '#1E3A8A',
                                textDecoration: 'none',
                                fontWeight: '500'
                              }}
                              onMouseEnter={(e) => {
                                e.currentTarget.style.color = '#F59E0B';
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.color = '#1E3A8A';
                              }}
                            >
                              <i className="bi bi-arrow-right me-1"></i>
                              Voir l'offre concernée
                            </button>
                          )}
                          
                          {/* ✅ BOUTON SUPPRIMER INDIVIDUEL */}
                          <button 
                            className="btn btn-sm btn-outline-danger ms-auto"
                            onClick={(e) => {
                              e.stopPropagation();
                              supprimerNotification(notif.id);
                            }}
                            style={{ fontSize: '0.75rem', padding: '2px 8px' }}
                            title="Supprimer cette notification"
                          >
                            <i className="bi bi-trash me-1"></i>
                            Supprimer
                          </button>
                        </div>
                      </div>
                      
                      {/* Badge Nouveau */}
                      {!notif.est_lue && (
                        <span className="badge bg-primary rounded-pill">
                          Nouveau
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Notifications;