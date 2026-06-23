// src/components/Footer.jsx
import React from 'react';
import Newsletter from './Newsletter';

const Footer = () => {
  return (
    <footer className="py-4 mt-5" 
            style={{ 
              background: `linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%)`,
              color: 'rgba(255, 255, 255, 0.85)'
            }}>
      <div className="container">
        <div className="row g-4">
          
          {/* À propos */}
          <div className="col-md-4">
            <h6 className="fw-bold mb-3" style={{ color: '#e94560', fontSize: '1rem' }}>
              <i className="bi bi-info-circle-fill me-2"></i>  {/* ✅ Icône ajoutée */}
              À PROPOS
            </h6>
            <p className="small mb-0" style={{ color: '#ffffff', opacity: 0.9, lineHeight: 1.6 }}>
              Plateforme de veille des appels d'offres du Burkina Faso et d'Afrique de l'Ouest. 
              Nous connectons experts et opportunités.
            </p>
          </div>
          
          {/* Contact */}
          <div className="col-md-4">
            <h6 className="fw-bold mb-3" style={{ color: '#e94560', fontSize: '1rem' }}>
              <i className="bi bi-envelope-paper-fill me-2"></i>  {/* ✅ Icône ajoutée */}
              CONTACT
            </h6>
            <ul className="list-unstyled small mb-0" style={{ color: '#ffffff', opacity: 0.9, lineHeight: 1.8 }}>
              <li className="mb-1">
                <i className="bi bi-geo-alt-fill me-2" style={{ color: '#e94560' }}></i>  {/* ✅ Icône ajoutée */}
                Ouagadougou, Burkina Faso
              </li>
              <li className="mb-1">
                <i className="bi bi-envelope-fill me-2" style={{ color: '#e94560' }}></i>  {/* ✅ Icône ajoutée */}
                contact@expertise-id.com
              </li>
              <li className="mb-1">
                <i className="bi bi-telephone-fill me-2" style={{ color: '#e94560' }}></i>  {/* ✅ Icône ajoutée */}
                +226 25 65 84 75
              </li>
            </ul>
          </div>
          
          {/* Newsletter */}
          <div className="col-md-4">
            <h6 className="fw-bold mb-3" style={{ color: '#e94560', fontSize: '1rem' }}>
              <i className="bi bi-envelope-plus-fill me-2"></i>  {/* ✅ Icône ajoutée */}
              NEWSLETTER
            </h6>
            <Newsletter variant="footer" />
          </div>
        </div>
        
        <hr className="my-4" style={{ borderColor: 'rgba(255, 255, 255, 0.15)' }} />
        
        {/* Copyright */}
        <div className="text-center small" style={{ opacity: 0.7 }}>
          <div className="d-flex justify-content-center gap-3 flex-wrap mb-2">
            <a href="#" className="text-decoration-none" 
               style={{ color: 'rgba(255, 255, 255, 0.85)', transition: 'color 0.2s' }}
               onMouseOver={(e) => e.target.style.color = '#F59E0B'}
               onMouseOut={(e) => e.target.style.color = 'rgba(255, 255, 255, 0.85)'}>
              <i className="bi bi-file-text-fill me-1"></i>  {/* ✅ Icône ajoutée */}
              Mentions légales
            </a>
            <span style={{ opacity: 0.5 }}>•</span>
            <a href="#" className="text-decoration-none"
               style={{ color: 'rgba(255, 255, 255, 0.85)', transition: 'color 0.2s' }}
               onMouseOver={(e) => e.target.style.color = '#F59E0B'}
               onMouseOut={(e) => e.target.style.color = 'rgba(255, 255, 255, 0.85)'}>
              <i className="bi bi-shield-lock-fill me-1"></i>  {/* ✅ Icône ajoutée */}
              Confidentialité
            </a>
          </div>
          <div>
            <i className="bi bi-c-circle me-1"></i>  {/* ✅ Icône ajoutée */}
            2026 Plateforme Appels d'Offres • <strong style={{ color: '#F59E0B' }}>EXPERTISE-ID</strong>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;