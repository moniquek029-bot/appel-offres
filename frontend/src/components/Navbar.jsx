// src/components/Navbar.jsx
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
// ✅ CORRECTION 1 : Chemin correct vers AuthContext (pas AuthentContext)
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { user, logout } = useAuth(); // ✅ Récupère user et logout du contexte
  const navigate = useNavigate();

  // Fermer le menu mobile après un clic
  const closeMenu = () => setIsMenuOpen(false);

  // Gestion de la déconnexion
  const handleLogout = () => {
    logout(); // Supprime le token
    closeMenu();
    navigate('/'); // Redirige vers l'accueil
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm sticky-top">
      <div className="container">
        
        {/* Logo */}
        <Link className="navbar-brand fw-bold" to="/" onClick={closeMenu}>
          🎯 AppelsOffres
        </Link>

        {/* Bouton hamburger (3 traits) */}
        <button
          className="navbar-toggler"
          type="button"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          aria-controls="navbarNav"
          aria-expanded={isMenuOpen}
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        {/* Menu collapsible */}
        <div className={`collapse navbar-collapse ${isMenuOpen ? 'show' : ''}`} id="navbarNav">
          <ul className="navbar-nav ms-auto mb-2 mb-lg-0 align-items-lg-center">
            
            {/* Liens publics */}
            <li className="nav-item">
              <Link className="nav-link" to="/" onClick={closeMenu}>Accueil</Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/offres" onClick={closeMenu}>Offres</Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/a-propos" onClick={closeMenu}>À propos</Link>
            </li>

            {/* 🔹 SECTION AUTH : Dynamique selon l'état CDC */}
            {user ? (
              // 👤 Utilisateur CONNECTÉ (Expert/Admin)
              <>
                <li className="nav-item">
                  <span className="nav-link text-light">
                    👋 Bonjour, {user.email?.split('@')[0] || 'Expert'}
                  </span>
                </li>
                <li className="nav-item ms-lg-2">
                  <Link className="btn btn-outline-light btn-sm" to="/dashboard" onClick={closeMenu}>
                    Mon Espace
                  </Link>
                </li>
                <li className="nav-item ms-lg-2">
                  <button className="btn btn-warning btn-sm text-dark" onClick={handleLogout}>
                    Déconnexion
                  </button>
                </li>
              </>
            ) : (
              // 🔐 Utilisateur NON CONNECTÉ (Visiteur)
              <>
                <li className="nav-item ms-lg-2">
                  <Link className="btn btn-outline-light btn-sm" to="/login" onClick={closeMenu}>
                    Se connecter
                  </Link>
                </li>
                <li className="nav-item ms-lg-2 mt-2 mt-lg-0">
                  <Link className="btn btn-warning btn-sm text-dark" to="/register" onClick={closeMenu}>
                    S'inscrire
                  </Link>
                </li>
              </>
            )}
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;