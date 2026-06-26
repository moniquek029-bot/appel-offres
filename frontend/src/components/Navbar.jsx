// src/components/Navbar.jsx
import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import NotificationBell from './NotificationBell';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [logoutHovered, setLogoutHovered] = useState(false);
  const [connectionHovered, setConnectionHovered] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const profileDropdownRef = useRef(null);

  // ✅ État pour les notifications
  const [notificationsEnabled, setNotificationsEnabled] = useState(() => {
    const saved = localStorage.getItem('notifications_enabled');
    return saved !== 'false'; // true par défaut
  });

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  // Fermer le dropdown si on clique ailleurs
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (profileDropdownRef.current && !profileDropdownRef.current.contains(event.target)) {
        setProfileDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // ✅ Toggle notifications
  const toggleNotifications = () => {
    const newValue = !notificationsEnabled;
    setNotificationsEnabled(newValue);
    localStorage.setItem('notifications_enabled', newValue);
    
    if (newValue && 'Notification' in window) {
      Notification.requestPermission();
    }
  };

  const isActive = (path) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  const activeLinkStyle = (path) => ({
    color: isActive(path) ? '#F59E0B' : 'rgba(255, 255, 255, 0.9)',
    borderBottom: isActive(path) ? '3px solid #F59E0B' : '3px solid transparent',
    paddingBottom: '4px',
    transition: 'all 0.3s ease',
    display: 'inline-flex',
    alignItems: 'center',
    gap: '6px',
    fontWeight: '500'
  });

  const getUserInitials = () => {
    if (!user) return 'U';
    const firstName = user.first_name || user.email?.[0] || 'U';
    const lastName = user.last_name || '';
    return `${firstName[0]}${lastName[0] || ''}`.toUpperCase();
  };

  return (
    <nav 
      className="text-white py-3 px-4 shadow-sm sticky-top"
      style={{
        background: 'linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%)',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
        zIndex: 1030
      }}
    >
      <div className="container-fluid d-flex justify-content-between align-items-center">
        
        {/* LOGO */}
        <Link to="/" className="text-white text-decoration-none d-flex align-items-center gap-2">
          <div style={{
            width: '36px',
            height: '36px',
            background: 'linear-gradient(135deg, #F59E0B, #1E3A8A)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 2px 8px rgba(245, 158, 11, 0.3)'
          }}>
            <span style={{ color: 'white', fontWeight: 'bold', fontSize: '1rem' }}>E</span>
          </div>
          <span className="fs-4 fw-bold">AppelsOffres</span>
        </Link>

        {/* MENU */}
        <div className="d-flex align-items-center gap-3">
          
          {/* Liens Publics */}
          <Link to="/" className="text-decoration-none" style={activeLinkStyle('/')}>
            <i className="bi bi-house-fill"></i>
            <span className="d-none d-md-inline">Accueil</span>
          </Link>
          
          <Link to="/offres" className="text-decoration-none" style={activeLinkStyle('/offres')}>
            <i className="bi bi-briefcase-fill"></i>
            <span className="d-none d-md-inline">Offres</span>
          </Link>
          
          <Link to="/a-propos" className="text-decoration-none" style={activeLinkStyle('/a-propos')}>
            <i className="bi bi-info-circle-fill"></i>
            <span className="d-none d-md-inline">À propos</span>
          </Link>

          {user ? (
            <>
              <span className="text-white opacity-25 mx-1">|</span>
              
              {/* Cloche notifications */}
              <NotificationBell enabled={notificationsEnabled} />
              
              <span className="text-white opacity-25 mx-1">|</span>
              
              {/* Bouton Tableau de bord (reste dans la navbar) */}
              <Link 
                to="/dashboard" 
                className="btn btn-outline-light btn-sm d-inline-flex align-items-center gap-2"
                style={{
                  background: 'transparent',
                  color: 'white',
                  border: '2px solid rgba(255, 255, 255, 0.5)',
                  borderRadius: '25px',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = '#F59E0B';
                  e.currentTarget.style.borderColor = '#F59E0B';
                  e.currentTarget.style.color = '#1E3A8A';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.5)';
                  e.currentTarget.style.color = 'white';
                }}
              >
                <i className="bi bi-speedometer2"></i>
                <span className="d-none d-lg-inline">Tableau de bord</span>
              </Link>
              
              {/* Dropdown Profil */}
              <div className="position-relative" ref={profileDropdownRef}>
                <button
                  className="btn btn-sm d-flex align-items-center gap-2 text-white"
                  onClick={() => setProfileDropdownOpen(!profileDropdownOpen)}
                  style={{
                    background: 'rgba(255, 255, 255, 0.1)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: '25px',
                    padding: '4px 12px 4px 4px',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                  }}
                >
                  <div style={{
                    width: '32px',
                    height: '32px',
                    background: 'linear-gradient(135deg, #F59E0B, #D97706)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    fontWeight: 'bold',
                    fontSize: '0.85rem'
                  }}>
                    {getUserInitials()}
                  </div>
                  
                  <span className="d-none d-lg-inline" style={{ fontSize: '0.9rem' }}>
                    {user.first_name || user.email?.split('@')[0] || 'Profil'}
                  </span>
                  
                  <i className="bi bi-chevron-down" style={{ fontSize: '0.75rem' }}></i>
                </button>

                {/* Dropdown Menu */}
                {profileDropdownOpen && (
                  <div 
                    className="position-absolute end-0 mt-2 shadow-lg"
                    style={{ 
                      minWidth: '240px',
                      borderRadius: '8px',
                      overflow: 'hidden',
                      border: '1px solid #E5E7EB',
                      zIndex: 1050,
                      backgroundColor: 'white'
                    }}
                  >
                    {/* En-tête */}
                    <div 
                      className="p-3"
                      style={{ 
                        background: 'linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%)',
                        color: 'white'
                      }}
                    >
                      <div className="d-flex align-items-center gap-2">
                        <div style={{
                          width: '40px',
                          height: '40px',
                          background: 'rgba(255, 255, 255, 0.2)',
                          borderRadius: '50%',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: 'bold'
                        }}>
                          {getUserInitials()}
                        </div>
                        <div>
                          <div className="fw-bold" style={{ fontSize: '0.95rem' }}>
                            {user.first_name} {user.last_name}
                          </div>
                          <div style={{ fontSize: '0.75rem', opacity: 0.9 }}>
                            {user.email}
                          </div>
                          <span className="badge bg-warning text-dark mt-1" style={{ fontSize: '0.65rem' }}>
                            {user.role || 'UTILISATEUR'}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Liens du dropdown */}
                    <div className="py-2">
                      {/* Mon Profil */}
                      <Link 
                        to="/profil" 
                        className="dropdown-item d-flex align-items-center gap-2 py-2"
                        onClick={() => setProfileDropdownOpen(false)}
                        style={{ 
                          color: '#1F2937',
                          transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.backgroundColor = '#FEF3C7';
                          e.currentTarget.style.color = '#D97706';
                          e.currentTarget.style.paddingLeft = '20px';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.backgroundColor = 'transparent';
                          e.currentTarget.style.color = '#1F2937';
                          e.currentTarget.style.paddingLeft = '16px';
                        }}
                      >
                        <i className="bi bi-person-fill" style={{ color: '#F59E0B' }}></i>
                        <span>Mon profil</span>
                      </Link>

                      {/* Paramètres */}
                      <Link 
                        to="/settings" 
                        className="dropdown-item d-flex align-items-center gap-2 py-2"
                        onClick={() => setProfileDropdownOpen(false)}
                        style={{ 
                          color: '#1F2937',
                          transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.backgroundColor = '#FEF3C7';
                          e.currentTarget.style.color = '#D97706';
                          e.currentTarget.style.paddingLeft = '20px';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.backgroundColor = 'transparent';
                          e.currentTarget.style.color = '#1F2937';
                          e.currentTarget.style.paddingLeft = '16px';
                        }}
                      >
                        <i className="bi bi-gear-fill" style={{ color: '#F59E0B' }}></i>
                        <span>Paramètres</span>
                      </Link>

                      <hr className="my-1" />

                      {/* Toggle Notifications */}
                      <div 
                        className="dropdown-item d-flex justify-content-between align-items-center py-2"
                        style={{ 
                          color: '#1F2937',
                          cursor: 'pointer'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.backgroundColor = '#FEF3C7';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.backgroundColor = 'transparent';
                        }}
                      >
                        <span className="d-flex align-items-center gap-2">
                          <i 
                            className={`bi ${notificationsEnabled ? 'bi-bell-fill' : 'bi-bell-slash-fill'}`}
                            style={{ color: notificationsEnabled ? '#F59E0B' : '#9CA3AF' }}
                          ></i>
                          <span>Notifications</span>
                        </span>
                        
                        <div 
                          className="form-check form-switch mb-0"
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleNotifications();
                          }}
                        >
                          <input 
                            className="form-check-input"
                            type="checkbox"
                            role="switch"
                            checked={notificationsEnabled}
                            onChange={toggleNotifications}
                            style={{ 
                              cursor: 'pointer',
                              width: '2.5rem',
                              height: '1.25rem'
                            }}
                          />
                        </div>
                      </div>

                      <hr className="my-1" />

                      {/* ✅ Déconnexion - Même style orange que Connexion */}
                      <button 
                        onClick={() => {
                          setProfileDropdownOpen(false);
                          handleLogout();
                        }}
                        className="d-flex align-items-center gap-2 border-0 w-100 text-start"
                        style={{ 
                          background: logoutHovered 
                            ? 'linear-gradient(135deg, #D97706 0%, #B45309 100%)' 
                            : 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)',
                          color: 'white',
                          borderRadius: '6px',
                          margin: '8px 12px 12px 12px',
                          padding: '10px 16px',
                          fontWeight: '600',
                          transition: 'all 0.3s ease',
                          cursor: 'pointer',
                          boxShadow: logoutHovered 
                            ? '0 4px 12px rgba(245, 158, 11, 0.5)' 
                            : '0 2px 8px rgba(245, 158, 11, 0.3)',
                          transform: logoutHovered ? 'translateY(-2px)' : 'none',
                          width: 'calc(100% - 24px)'
                        }}
                        onMouseEnter={() => setLogoutHovered(true)}
                        onMouseLeave={() => setLogoutHovered(false)}
                      >
                        <i className="bi bi-box-arrow-right"></i>
                        <span>Déconnexion</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </>
          ) : (
            <Link 
              to="/login" 
              className="btn btn-sm text-nowrap"
              onMouseEnter={() => setConnectionHovered(true)}
              onMouseLeave={() => setConnectionHovered(false)}
              style={{
                background: connectionHovered 
                  ? 'linear-gradient(135deg, #D97706 0%, #B45309 100%)' 
                  : 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)',
                color: 'white',
                border: 'none',
                textDecoration: 'none',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                transition: 'all 0.3s ease',
                boxShadow: '0 2px 8px rgba(245, 158, 11, 0.3)',
                transform: connectionHovered ? 'translateY(-2px)' : 'none'
              }}
            >
              <i className="bi bi-box-arrow-in-right"></i>
              Connexion
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;