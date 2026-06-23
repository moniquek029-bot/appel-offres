// src/pages/APropos.jsx
import React from 'react';

const APropos = () => {
  return (
    <div className="container py-5" style={{ backgroundColor: 'var(--gray-50)', minHeight: '100vh' }}>
      <div className="row justify-content-center">
        <div className="col-lg-8">
          <div className="card border-0 shadow-sm" 
               style={{ borderRadius: 'var(--radius-xl)' }}>
            <div className="card-body p-4 p-lg-5">
              
              {/* Header avec icône */}
              <div className="text-center mb-4">
                <div className="d-inline-flex align-items-center justify-content-center" 
                     style={{ 
                       width: '70px', 
                       height: '70px', 
                       borderRadius: '50%',
                       background: 'linear-gradient(135deg, var(--primary), var(--primary-dark))',
                       color: 'white',
                       fontSize: '1.8rem',
                       marginBottom: '1rem'
                     }}>
                  <i className="bi bi-info-circle-fill"></i>
                </div>
                <h2 className="mb-2 fw-bold" style={{ color: 'var(--primary)', fontSize: '1.8rem' }}>
                  À Propos
                </h2>
                <p className="text-muted" style={{ fontSize: '1.1rem' }}>
                  Plateforme Appels d'Offres • EXPERTISE-ID
                </p>
              </div>
              
              <p className="lead" style={{ color: 'var(--gray-700)' }}>
                Une plateforme qui centralise les appels d'offres du Burkina Faso et d'Afrique, 
                facilitant la recherche et la candidature pour les marchés publics et privés.
              </p>
              
              <hr className="my-4" style={{ borderColor: 'var(--gray-300)' }} />
              
              {/* Mission */}
              <div className="mb-4">
                <h5 className="fw-semibold mb-3" style={{ color: 'var(--primary)' }}>
                  <i className="bi bi-bullseye me-2"></i>Notre Mission
                </h5>
                <p style={{ color: 'var(--gray-700)', lineHeight: 1.7 }}>
                  Faciliter l'accès aux opportunités d'affaires en centralisant et en organisant 
                  les appels d'offres provenant de multiples sources officielles. Notre objectif est 
                  de connecter les experts et bureaux d'études avec les opportunités qui correspondent 
                  à leurs compétences.
                </p>
              </div>
              
              {/* Technologies */}
              {/* <div className="mb-4">
                <h5 className="fw-semibold mb-3" style={{ color: 'var(--primary)' }}>
                  <i className="bi bi-code-slash me-2"></i>Technologies
                </h5>
                <div className="row g-2">
                  {[
                    { icon: '🐍', label: 'Backend: Django (Python)' },
                    { icon: '🗄️', label: 'Base de données: MySQL' },
                    { icon: '⚛️', label: 'Frontend: React + Bootstrap' },
                    { icon: '🕷️', label: 'Scraping: BeautifulSoup, Selenium' }
                  ].map((tech, i) => (
                    <div className="col-md-6" key={i}>
                      <div className="d-flex align-items-center p-2" 
                           style={{ 
                             backgroundColor: 'var(--gray-100)',
                             borderRadius: 'var(--radius)',
                             fontSize: '0.9rem'
                           }}>
                        <span className="me-2 fs-5">{tech.icon}</span>
                        <span style={{ color: 'var(--gray-800)' }}>{tech.label}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>*/}
              
              {/* Contact */}
              <div className="mb-4">
                <h5 className="fw-semibold mb-3" style={{ color: 'var(--primary)' }}>
                  <i className="bi bi-envelope me-2"></i>Contact
                </h5>
                <div className="p-3" 
                     style={{ 
                       backgroundColor: 'var(--primary-bg)',
                       borderRadius: 'var(--radius-lg)',
                       borderLeft: '4px solid var(--primary)'
                     }}>
                  <p className="mb-2" style={{ color: 'var(--gray-800)' }}>
                    <strong>Email:</strong> contact@expertise-id.com
                  </p>
                  <p className="mb-0" style={{ color: 'var(--gray-800)' }}>
                    <strong>Adresse:</strong> Ouagadougou, Burkina Faso
                  </p>
                </div>
              </div>
              
              <hr className="my-4" style={{ borderColor: 'var(--gray-300)' }} />
              
              {/* Footer */}
              <p className="text-muted small text-center mb-0">
                © 2026 Plateforme Appels d'Offres • <strong>EXPERTISE-ID</strong>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default APropos;