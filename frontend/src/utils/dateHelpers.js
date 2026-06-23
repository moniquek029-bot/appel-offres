// src/utils/dateHelpers.js

/**
 * Calcule et formate le temps écoulé depuis le scraping d'une offre
 * @param {string} dateString - Date ISO renvoyée par Django
 * @returns {string} Texte lisible (ex: "Il y a 5 min")
 */
export const formatTimeElapsed = (dateString) => {
  if (!dateString) return '';

  const maintenant = new Date();
  const dateScraping = new Date(dateString);
  const differenceEnMs = maintenant - dateScraping;
  
  const minutes = Math.floor(differenceEnMs / (1000 * 60));
  const heures = Math.floor(differenceEnMs / (1000 * 60 * 60));
  const jours = Math.floor(differenceEnMs / (1000 * 60 * 60 * 24));

  if (minutes < 1) return "Vient d'être scrappée";
  if (minutes < 60) return `Il y a ${minutes} min`;
  if (heures < 24) return `Il y a ${heures} h`;
  return `Il y a ${jours} jour${jours > 1 ? 's' : ''}`;
};