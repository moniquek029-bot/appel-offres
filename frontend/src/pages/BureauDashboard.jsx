import React from 'react';

const BureauDashboard = () => {
  return (
    <div className="container py-5">
      <h2 className="mb-4">Bienvenue sur votre espace Bureau d'étude</h2>
      <div className="alert alert-info">
        Cette page est dédiée aux utilisateurs de type <b>Bureau</b>.<br/>
        Vous pourrez bientôt y retrouver vos offres, statistiques, et outils de gestion spécifiques.
      </div>
    </div>
  );
};

export default BureauDashboard;
