// frontend/src/pages/ChooseRole.jsx
import React from 'react';
import { Link } from 'react-router-dom';

const ChooseRole = () => {
  return (
    <div className="container d-flex justify-content-center align-items-center" style={{ minHeight: '80vh' }}>
      <div className="card border-0 shadow-lg" style={{ width: '100%', maxWidth: '550px', borderRadius: '16px' }}>
        <div className="card-body p-4 p-md-5">
          
          {/* En-tête avec icône - Même style que login */}
          <div className="text-center mb-4">
            <div className="bg-primary bg-opacity-10 rounded-circle d-inline-flex p-3 mb-3">
              <i className="bi bi-person-plus-fill fs-1 text-primary"></i>
            </div>
            <h2 className="h3 mb-2 fw-bold" style={{ color: '#1a1a2e' }}>S'inscrire</h2>
            <p className="text-muted small mb-0">Bénéficiez de tous les services de Marchés Online</p>
          </div>

          {/* Message d'information */}
          <div className="alert alert-info bg-light border-0 text-center py-2 mb-4" style={{ borderRadius: '10px' }}>
            <i className="bi bi-info-circle-fill text-primary me-2"></i>
            <span className="small">Choisissez votre profil pour commencer</span>
          </div>

          {/* Carte Expert */}
          <div className="card mb-3 border-0 shadow-sm" style={{ borderRadius: '12px', transition: 'all 0.2s ease' }}>
            <div className="card-body p-3 p-md-4">
              <div className="d-flex align-items-start">
                <div className="bg-primary bg-opacity-10 rounded-circle p-2 me-3" style={{ width: '48px', height: '48px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <i className="bi bi-briefcase-fill fs-4 text-primary"></i>
                </div>
                <div className="flex-grow-1">
                  <div className="d-flex justify-content-between align-items-center flex-wrap">
                    <h5 className="mb-1 fw-bold" style={{ color: '#1a1a2e' }}>
                      {/* <i className="bi bi-star-fill text-warning me-1" style={{ fontSize: '0.8rem' }}></i> */}
                      Je suis un expert
                    </h5>
                    <Link to="/register/expert" className="btn btn-outline-primary btn-sm" style={{ borderRadius: '20px', padding: '5px 16px' }}>
                      Choisir <i className="bi bi-arrow-right ms-1"></i>
                    </Link>
                  </div>
                  <p className="text-muted small mb-0 mt-2">
                    Consultant, freelance, expert indépendant.<br />
                    Je souhaite consulter les appels d'offres et postuler.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Carte Bureau d'études */}
          <div className="card mb-4 border-0 shadow-sm" style={{ borderRadius: '12px', transition: 'all 0.2s ease' }}>
            <div className="card-body p-3 p-md-4">
              <div className="d-flex align-items-start">
                <div className="bg-primary bg-opacity-10 rounded-circle p-2 me-3" style={{ width: '48px', height: '48px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <i className="bi bi-building-fill fs-4 text-primary"></i>
                </div>
                <div className="flex-grow-1">
                  <div className="d-flex justify-content-between align-items-center flex-wrap">
                    <h5 className="mb-1 fw-bold" style={{ color: '#1a1a2e' }}>
                      {/* <i className="bi bi-building-check text-success me-1"></i> */}
                      Je suis un bureau d'études
                    </h5>
                    <Link to="/register/bureau" className="btn btn-outline-primary btn-sm" style={{ borderRadius: '20px', padding: '5px 16px' }}>
                      Choisir <i className="bi bi-arrow-right ms-1"></i>
                    </Link>
                  </div>
                  <p className="text-muted small mb-0 mt-2">
                    Bureau d'étude, entreprise, institution.<br />
                    Je souhaite consulter des appels d'offres.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Lien vers connexion */}
          <div className="text-center mt-2 pt-2 border-top">
            <p className="small text-muted mb-0">
              J'ai déjà un compte ?{' '}
              <Link to="/login" className="text-primary fw-semibold text-decoration-none">
                <i className="bi bi-box-arrow-in-right me-1"></i>
            Se connecter
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChooseRole;