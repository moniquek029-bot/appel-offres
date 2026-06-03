// src/pages/ChooseRole.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';

const ChooseRole = () => {
  const navigate = useNavigate();

  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-md-8 col-lg-7">
          
          {/* En-tête */}
          <div className="text-center mb-4">
            <div className="bg-primary bg-opacity-10 rounded-circle d-inline-flex p-3 mb-2">
              <span className="display-6"></span>
            </div>
            <h1 className="display-6 fw-bold text-primary">S'inscrire</h1>
            <p className="text-muted mt-2">
              Bénéficiez de tous les services de Marchés Online
            </p>
          </div>
          
          {/* Cartes de choix */}
          <div className="row g-4 mb-4">
            
            {/* Carte Expert */}
            <div className="col-md-6">
              <div 
                className="card border-0 shadow-lg rounded-4 h-100 text-center p-4"
                style={{ cursor: 'pointer', transition: 'transform 0.2s' }}
                onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
                onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                onClick={() => navigate('/register/expert')}
              >
                <div className="card-body">
                  <div className="display-1 mb-3"></div>
                  <h3 className="card-title fw-bold">Je suis un expert</h3>
                  <p className="card-text text-muted mt-3">
                    Consultant, freelance, expert indépendant<br />
                    <span className="small">Je souhaite consulter les appels d'offres et postuler</span>
                  </p>
                  <button className="btn btn-outline-primary mt-3 px-4">
                    Choisir cette option →
                  </button>
                </div>
              </div>
            </div>
            
            {/* Carte Bureau */}
            <div className="col-md-6">
              <div 
                className="card border-0 shadow-lg rounded-4 h-100 text-center p-4"
                style={{ cursor: 'pointer', transition: 'transform 0.2s' }}
                onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
                onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                onClick={() => navigate('/register/bureau')}
              >
                <div className="card-body">
                  <div className="display-1 mb-3"></div>
                  <h3 className="card-title fw-bold">Je suis un bureau</h3>
                  <p className="card-text text-muted mt-3">
                    Bureau d'étude, entreprise, institution<br />
                    <span className="small">Je souhaite consulter des appels d'offres</span>
                  </p>
                  <button className="btn btn-outline-primary mt-3 px-4">
                    Choisir cette option →
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          {/* Lien connexion */}
          <div className="text-center mt-4">
            <p className="text-muted">
              J'ai déjà un compte{' '}
              <a href="/login" className="text-decoration-none fw-semibold text-primary">
              Me connecter
              </a>
            </p>
          </div>
          
          {/* Avantages */}
          <div className="card border-0 bg-light mt-4 rounded-4">
            <div className="card-body p-4">
              <h6 className="text-primary fw-bold mb-3">Ce que nous vous offrons</h6>
              <div className="row">
                <div className="col-md-4 mb-2">
                  <small className="text-muted">✓ Accès centralisé à tous les appels d'offres</small>
                </div>
                <div className="col-md-4 mb-2">
                  <small className="text-muted">✓ Alertes email personnalisées</small>
                </div>
                <div className="col-md-4 mb-2">
                  <small className="text-muted">✓ Suivi de publication en temps réel</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChooseRole;