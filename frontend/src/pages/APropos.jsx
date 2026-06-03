// src/pages/APropos.jsx
import React from 'react';

const APropos = () => {
  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-lg-8">
          <div className="card border-0 shadow-sm">
            <div className="card-body p-4 p-lg-5">
              <h2 className="mb-4 text-primary">📌 À Propos de la Plateforme</h2>
              
              <p className="lead">
                Une plateforme qui centralise les appels d'offres des pays et des entreprises, 
                facilitant la recherche et la candidature pour les marchés publics et privés.
              </p>
              
              <hr className="my-4" />
              
              <h5>🎯 Notre Mission</h5>
              <p>
                Faciliter l'accès aux opportunités d'affaires en centralisant et en organisant 
                les appels d'offres provenant de multiples sources.
              </p>
              
              <h5>🔧 Technologies utilisées</h5>
              <ul>
                <li>Backend : Django (Python)</li>
                <li>Base de données : MySQL</li>
                <li>Frontend : React + Bootstrap</li>
                <li>Web Scraping : BeautifulSoup, Selenium</li>
              </ul>
              
              <h5>📞 Contact</h5>
              <p>
                Pour toute question ou suggestion :<br />
                📧 Email : contact@plateforme-offres.com
              </p>
              
              <hr className="my-4" />
              
              <p className="text-muted small text-center">
                © 2026 Plateforme Appels d'Offres • Expertise-ID
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default APropos;