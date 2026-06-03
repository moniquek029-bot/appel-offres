// src/components/Navbar.jsx

import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext'; // Assure-toi que l'import est correct

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="bg-primary text-white py-3 px-4 shadow-sm">
      <div className="container-fluid d-flex justify-content-between align-items-center">
        
        {/* 1. LOGO / TITRE (À Gauche) */}
        <Link to="/" className="text-white text-decoration-none fs-4 fw-bold">
          AppelsOffres
        </Link>

        {/* 2. MENU HORIZONTAL (À Droite) */}
        <div className="d-flex align-items-center gap-3">
          
          {/* Liens Publics */}
          <Link to="/" className="text-white text-decoration-none fw-medium">
            Accueil
          </Link>
          <Link to="/offres" className="text-white text-decoration-none fw-medium">
            Offres
          </Link>
          <Link to="/a-propos" className="text-white text-decoration-none fw-medium">
            À propos
          </Link>

          {/* Liens Connectés (si utilisateur connecté) */}
          {user ? (
            <>
              {/* Séparateur vertical */}
              <span className="text-white opacity-50">|</span>
              
              <Link to="/dashboard" className="btn btn-outline-light btn-sm">
                Tableau de bord
              </Link>
              
              <button 
                onClick={handleLogout} 
                className="btn btn-warning btn-sm fw-bold"
              >
                Déconnexion
              </button>
            </>
          ) : (
            <Link to="/login" className="btn btn-light btn-sm">
              Connexion
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;