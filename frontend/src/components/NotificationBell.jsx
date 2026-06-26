// src/components/NotificationBell.jsx
import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

const NotificationBell = ({ enabled = true }) => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);

  // Fermer le dropdown si on clique ailleurs
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const fetchNotifications = async () => {
    if (!user || !enabled) return;

    try {
      const response = await api.get('/notifications/');
      const notifs = response.data.results || response.data || [];
      
      setNotifications(notifs);
      const unread = notifs.filter(n => !n.est_lue).length;
      setUnreadCount(unread);
      
    } catch (error) {
      console.error('Erreur notifications:', error);
    }
  };

  // ✅ CORRECTIF : useEffect propre sans polling
  useEffect(() => {
    fetchNotifications();
  }, [user, enabled]);

  const markAsRead = async (notifId) => {
    try {
      await api.post(`/notifications/${notifId}/marquer-lue/`);
      
      setNotifications(prev => 
        prev.map(n => n.id === notifId ? {...n, est_lue: true} : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
      
    } catch (error) {
      console.error('Erreur marquage:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      const unreadNotifs = notifications.filter(n => !n.est_lue);
      
      await Promise.all(
        unreadNotifs.map(n => api.post(`/notifications/${n.id}/marquer-lue/`))
      );
      
      setNotifications(prev => prev.map(n => ({...n, est_lue: true})));
      setUnreadCount(0);
      
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'À l\'instant';
    if (diffMins < 60) return `Il y a ${diffMins} min`;
    if (diffHours < 24) return `Il y a ${diffHours}h`;
    if (diffDays < 7) return `Il y a ${diffDays}j`;
    return date.toLocaleDateString('fr-FR');
  };

  const getIcon = (notif) => {
    if (notif.objet?.includes('message')) return 'bi-chat-dots-fill';
    if (notif.objet?.includes('suggestion')) return 'bi-lightbulb-fill';
    if (notif.objet?.includes('offre')) return 'bi-briefcase-fill';
    return 'bi-bell-fill';
  };

  const getColor = (notif) => {
    if (notif.objet?.includes('message')) return '#3B82F6';
    if (notif.objet?.includes('suggestion')) return '#F59E0B';
    if (notif.objet?.includes('offre')) return '#10B981';
    return '#6B7280';
  };

  const goToAllNotifications = () => {
    setShowDropdown(false);
    navigate('/notifications');
  };

  if (!enabled) {
    return (
      <button
        className="btn btn-link position-relative p-2"
        style={{ fontSize: '1.5rem', color: '#9CA3AF', opacity: 0.6 }}
        title="Notifications désactivées"
      >
        <i className="bi bi-bell-slash-fill"></i>
      </button>
    );
  }

  return (
    <div className="position-relative" ref={dropdownRef}>
      {/* Bouton cloche */}
      <button
        className="btn btn-link position-relative p-2"
        onClick={() => setShowDropdown(!showDropdown)}
        style={{ fontSize: '1.5rem', color: '#6B7280' }}
      >
        <i className="bi bi-bell-fill"></i>
        
        {unreadCount > 0 && (
          <span 
            className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger"
            style={{ 
              fontSize: '0.7rem',
              animation: 'pulse 2s infinite'
            }}
          >
            {unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {showDropdown && (
        <>
          <div 
            className="position-fixed top-0 start-0 w-100 h-100"
            style={{ zIndex: 1040 }}
            onClick={() => setShowDropdown(false)}
          />
          
          <div 
            className="position-absolute end-0 mt-2 shadow-lg"
            style={{ 
              zIndex: 1050,
              width: '400px',
              maxHeight: '500px',
              backgroundColor: 'white',
              borderRadius: '8px',
              border: '1px solid #E5E7EB'
            }}
          >
            {/* Header avec croix de fermeture */}
            <div className="d-flex justify-content-between align-items-center p-3 border-bottom"
                 style={{ 
                   background: 'linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%)',
                   color: 'white',
                   borderTopLeftRadius: '8px',
                   borderTopRightRadius: '8px'
                 }}>
              <h6 className="mb-0 fw-bold">
                <i className="bi bi-bell me-2"></i>
                Notifications
                {unreadCount > 0 && (
                  <span className="badge bg-light text-dark ms-2">{unreadCount}</span>
                )}
              </h6>
              
              <div className="d-flex gap-2">
                {unreadCount > 0 && (
                  <button 
                    className="btn btn-sm btn-outline-light"
                    onClick={markAllAsRead}
                    style={{ fontSize: '0.75rem', padding: '2px 8px' }}
                  >
                    Tout lire
                  </button>
                )}
                
                {/* Croix de fermeture */}
                <button 
                  onClick={() => setShowDropdown(false)}
                  className="btn btn-link text-white p-0"
                  style={{
                    fontSize: '1.25rem',
                    lineHeight: 1,
                    opacity: 0.8,
                    transition: 'all 0.2s ease',
                    width: '32px',
                    height: '32px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    borderRadius: '50%',
                    border: '2px solid rgba(255, 255, 255, 0.3)'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.opacity = '1';
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
                    e.currentTarget.style.transform = 'rotate(90deg)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.opacity = '0.8';
                    e.currentTarget.style.background = 'transparent';
                    e.currentTarget.style.transform = 'rotate(0deg)';
                  }}
                  title="Fermer"
                >
                  <i className="bi bi-x-lg"></i>
                </button>
              </div>
            </div>

            {/* Liste des notifications */}
            <div style={{ maxHeight: '400px', overflow: 'auto' }}>
              {notifications.length === 0 ? (
                <div className="text-center py-5 text-muted">
                  <i className="bi bi-bell-slash" style={{ fontSize: '3rem' }}></i>
                  <p className="mt-2 mb-0">Aucune notification</p>
                </div>
              ) : (
                notifications.slice(0, 20).map(notif => (
                  <div
                    key={notif.id}
                    className={`p-3 border-bottom ${!notif.est_lue ? 'bg-light' : ''}`}
                    style={{ 
                      cursor: 'pointer',
                      transition: 'background-color 0.2s'
                    }}
                    onClick={() => markAsRead(notif.id)}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#F9FAFB'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = notif.est_lue ? 'white' : '#F9FAFB'}
                  >
                    <div className="d-flex gap-3">
                      <div 
                        className="d-flex align-items-center justify-content-center rounded-circle flex-shrink-0"
                        style={{ 
                          width: '40px',
                          height: '40px',
                          backgroundColor: `${getColor(notif)}20`,
                          color: getColor(notif)
                        }}
                      >
                        <i className={`bi ${getIcon(notif)}`}></i>
                      </div>

                      <div className="flex-grow-1">
                        <div className="d-flex justify-content-between align-items-start">
                          <h6 className="mb-1" style={{ fontSize: '0.9rem' }}>
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
                          <small className="text-muted" style={{ fontSize: '0.75rem' }}>
                            {formatDate(notif.date_envoi)}
                          </small>
                        </div>
                        <p className="mb-0 text-muted" style={{ fontSize: '0.85rem' }}>
                          {notif.message}
                        </p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Footer */}
            {notifications.length > 0 && (
              <div className="p-2 border-top text-center">
                <button 
                  className="btn btn-sm btn-link text-decoration-none"
                  onClick={goToAllNotifications}
                  style={{
                    color: '#1E3A8A',
                    fontWeight: '600',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.color = '#F59E0B';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.color = '#1E3A8A';
                  }}
                >
                  <i className="bi bi-list-ul me-1"></i>
                  Voir toutes les notifications
                </button>
              </div>
            )}
          </div>
        </>
      )}

      <style>{`
        @keyframes pulse {
          0% {
            box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
          }
          70% {
            box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
          }
          100% {
            box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
          }
        }
      `}</style>
    </div>
  );
};

export default NotificationBell;