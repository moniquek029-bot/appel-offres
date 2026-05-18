import React from 'react';

const Offres = () => {
  return (
    <div className="container py-5">
      <h2 className="mb-4"> Liste des Offres</h2>
      <div className="alert alert-info">
         Les offres scrapées s'afficheront ici. 
        <br/>Prochaine étape : intégration du composant <code>JobList</code> connecté à l'API Django.
      </div>
    </div>
  );
};

export default Offres;