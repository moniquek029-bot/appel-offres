// src/components/Footer.jsx
import React from 'react';
import Newsletter from './Newsletter';

const Footer = () => {
  return (
    <footer className="bg-dark text-white py-4 mt-4">
      <div className="container">
        <div className="row">
          {/* À propos */}
          <div className="col-md-4 mb-3 mb-md-0">
            <h6 className="fw-bold mb-2">À PROPOS</h6>
            <p className="small text-white-50 mb-0">
              Plateforme de veille des appels d'offres du Burkina Faso et d'Afrique.
            </p>
          </div>
          
          {/* Contact */}
          <div className="col-md-4 mb-3 mb-md-0">
            <h6 className="fw-bold mb-2">CONTACT</h6>
            <ul className="list-unstyled small text-white-50 mb-0">
              <li className="mb-1">📍 Ouagadougou, Burkina Faso</li>
              <li className="mb-1">✉️ contact@expertise_id.com</li>
              <li className="mb-1">📞 +226 25 65 84 75 / +226 75 64 77 91</li>
            </ul>
          </div>
          
          {/* Newsletter */}
          <div className="col-md-4">
            <h6 className="fw-bold mb-2">NEWSLETTER</h6>
            <Newsletter variant="footer" />
          </div>
        </div>
        
        <hr className="my-3 border-secondary" />
        
        <div className="text-center small text-white-50">
          <div className="d-flex justify-content-center gap-3 flex-wrap mb-2">
            <a href="#" className="text-white-50 text-decoration-none">Mentions légales</a>
            <span className="text-white-50">•</span>
            <a href="#" className="text-white-50 text-decoration-none">Confidentialité</a>
            <span className="text-white-50">•</span>
            <a href="#" className="text-white-50 text-decoration-none"></a>
          </div>
          © 2026 Plateforme Appels d'Offres • Expertise-ID
        </div>
      </div>
    </footer>
  );
};

export default Footer;