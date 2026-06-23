// src/components/Navbar.jsx
import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext'; // Assure-toi que l'import est correct

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [logoutHovered, setLogoutHovered] = React.useState(false);
  const [connectionHovered, setConnectionHovered] = React.useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  // ✅ Fonction pour déterminer si une route est active
  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  // ✅ Style pour les liens actifs - orange foncé
  const activeLinkStyle = (path) => ({
    color: isActive(path) ? '#E67E22' : 'white',
    borderBottom: isActive(path) ? '3px solid #E67E22' : 'none',
    paddingBottom: isActive(path) ? '2px' : '0',
    transition: 'all 0.3s ease'
  });

  // ✅ Style pour le bouton orange foncé au clic/hover
  const orangeButtonStyle = {
    background: 'linear-gradient(135deg, var(--primary) 0%, #D35400 100%)',
    color: 'white',
    border: 'none',
    transition: 'all 0.3s ease',
    cursor: 'pointer',
    boxShadow: '0 2px 8px rgba(211, 84, 0, 0.15)'
  };

  const orangeButtonHoverStyle = {
    background: 'linear-gradient(135deg, #D35400 0%, var(--primary-dark) 100%)',
    color: 'white',
    border: 'none',
    transition: 'all 0.3s ease',
    cursor: 'pointer',
    boxShadow: '0 4px 12px rgba(211, 84, 0, 0.3)',
    transform: 'translateY(-2px)'
  };

  return (
    <nav 
      className="text-white py-3 px-4 shadow-sm"
      style={{
        background: 'linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%)',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'
      }}
    >
      <div className="container-fluid d-flex justify-content-between align-items-center">
        
        {/* 1. LOGO / TITRE (À Gauche) - AVEC LE "E" */}
        <Link to="/" className="text-white text-decoration-none d-flex align-items-center gap-2">
          {/* ✅ AJOUT DU LOGO "E" (comme dans le footer) */}
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

        {/* 2. MENU HORIZONTAL (À Droite) */}
        <div className="d-flex align-items-center gap-3">
          
          {/* Liens Publics */}
          <Link 
            to="/" 
            className="text-decoration-none fw-medium"
            style={activeLinkStyle('/')}
          >
            Accueil
          </Link>
          <Link 
            to="/offres" 
            className="text-decoration-none fw-medium"
            style={activeLinkStyle('/offres')}
          >
            Offres
          </Link>
          <Link 
            to="/a-propos" 
            className="text-decoration-none fw-medium"
            style={activeLinkStyle('/a-propos')}
          >
            À propos
          </Link>

          {/* Liens Connectés (si utilisateur connecté) */}
          {user ? (
            <>
              {/* Séparateur vertical */}
              <span className="text-white opacity-50">|</span>
              
              <Link 
                to="/dashboard" 
                className="btn btn-outline-light btn-sm"
                style={{ 
                  borderRadius: '25px',
                  transition: 'all 0.2s ease',
                  backgroundColor: 'transparent',
                  borderColor: 'rgba(255, 255, 255, 0.5)',
                  color: 'white'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#F59E0B';
                  e.currentTarget.style.borderColor = '#F59E0B';
                  e.currentTarget.style.color = '#1E3A8A';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.5)';
                  e.currentTarget.style.color = 'white';
                }}
              >
                Tableau de bord
              </Link>
              
              <button 
                onClick={handleLogout}
                onMouseEnter={() => setLogoutHovered(true)}
                onMouseLeave={() => setLogoutHovered(false)}
                className="btn btn-sm fw-bold"
                style={logoutHovered ? orangeButtonHoverStyle : orangeButtonStyle}
              >
                Déconnexion
              </button>
            </>
          ) : (
            <Link to="/login" 
              className="btn btn-sm text-nowrap"
              onMouseEnter={() => setConnectionHovered(true)}
              onMouseLeave={() => setConnectionHovered(false)}
              style={connectionHovered ? { ...orangeButtonHoverStyle, textDecoration: 'none' } : { ...orangeButtonStyle, textDecoration: 'none' }}>
              Connexion
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;