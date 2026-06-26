// src/utils/multilingualKeywords.js

export const multilingualKeywords = {
  // SANTÉ
  'santé': ['health', 'medical', 'healthcare', 'hôpital', 'hospital', 'médecin', 'doctor', 'soins', 'care', 'clinique', 'clinic'],
  'health': ['santé', 'medical', 'healthcare', 'hôpital', 'hospital', 'médecin', 'doctor'],
  'medical': ['santé', 'health', 'médical', 'soins', 'care', 'hôpital', 'hospital'],
  
  // INFORMATIQUE
  'informatique': ['IT', 'information technology', 'computer', 'software', 'développement', 'development', 'programmation', 'programming', 'numérique', 'digital', 'tech', 'technology'],
  'IT': ['informatique', 'technology', 'tech', 'computer', 'software', 'développement', 'development'],
  'technology': ['technologie', 'informatique', 'IT', 'tech', 'numérique', 'digital'],
  
  // BTP / CONSTRUCTION
  'BTP': ['construction', 'building', 'travaux publics', 'public works', 'infrastructure', 'génie civil', 'civil engineering', 'architecture'],
  'construction': ['BTP', 'building', 'travaux', 'works', 'infrastructure', 'bâtiment', 'building'],
  'infrastructure': ['infrastructure', 'BTP', 'construction', 'travaux publics', 'public works'],
  
  // ÉDUCATION
  'éducation': ['education', 'enseignement', 'teaching', 'formation', 'training', 'école', 'school', 'université', 'university', 'apprentissage', 'learning'],
  'education': ['éducation', 'enseignement', 'teaching', 'formation', 'training', 'école', 'school'],
  'formation': ['training', 'éducation', 'education', 'enseignement', 'teaching', 'apprentissage', 'learning'],
  
  // FINANCE
  'finance': ['finance', 'comptabilité', 'accounting', 'banque', 'bank', 'économique', 'economic', 'budget', 'audit'],
  'accounting': ['comptabilité', 'finance', 'audit', 'budget'],
  'economic': ['économique', 'économie', 'economy', 'finance'],
  
  // ENVIRONNEMENT
  'environnement': ['environment', 'écologie', 'ecology', 'développement durable', 'sustainable development', 'climat', 'climate', 'green', 'vert'],
  'environment': ['environnement', 'écologie', 'ecology', 'climate', 'climat', 'green'],
  'ecology': ['écologie', 'environnement', 'environment', 'durable', 'sustainable'],
  
  // AGRICULTURE
  'agriculture': ['agriculture', 'farming', 'agroalimentaire', 'food', 'élevage', 'livestock', 'cultures', 'crops'],
  'farming': ['agriculture', 'élevage', 'livestock', 'cultures', 'crops'],
  
  // TRANSPORT
  'transport': ['transport', 'logistics', 'logistique', 'shipping', 'expédition', 'delivery', 'livraison'],
  'logistics': ['logistique', 'transport', 'shipping', 'supply chain', 'chaîne d\'approvisionnement'],
  
  // ÉNERGIE
  'énergie': ['energy', 'électricité', 'electricity', 'power', 'renouvelable', 'renewable', 'solaire', 'solar', 'éolien', 'wind'],
  'energy': ['énergie', 'power', 'electricity', 'électricité', 'renewable', 'renouvelable'],
  
  // TÉLÉCOMMUNICATIONS
  'télécommunications': ['telecommunications', 'telecom', 'communication', 'réseau', 'network', '5G', '4G', 'internet', 'mobile'],
  'telecommunications': ['télécommunications', 'telecom', 'communication', 'network', 'réseau'],
  
  // RESSOURCES HUMAINES
  'ressources humaines': ['human resources', 'HR', 'RH', 'personnel', 'staff', 'recrutement', 'recruitment'],
  'human resources': ['ressources humaines', 'RH', 'HR', 'personnel', 'staff'],
  
  // JURIDIQUE
  'juridique': ['legal', 'law', 'droit', 'justice', 'avocat', 'lawyer', 'juridique'],
  'legal': ['juridique', 'law', 'droit', 'justice'],
};

// Fonction pour obtenir tous les mots-clés associés
export const getRelatedKeywords = (keyword) => {
  if (!keyword) return [];
  
  const normalizedKeyword = keyword.toLowerCase().trim();
  const related = new Set([normalizedKeyword]);
  
  // Chercher dans le mapping
  for (const [key, values] of Object.entries(multilingualKeywords)) {
    if (key === normalizedKeyword) {
      values.forEach(v => related.add(v));
    }
    if (values.includes(normalizedKeyword)) {
      related.add(key);
      values.forEach(v => related.add(v));
    }
  }
  
  return Array.from(related);
};

// Fonction pour créer une requête de recherche multilingue
export const buildMultilingualSearch = (keyword) => {
  if (!keyword || keyword.trim() === '') return '';
  
  const relatedKeywords = getRelatedKeywords(keyword);
  return relatedKeywords.join(' OR ');
};

export default {
  multilingualKeywords,
  getRelatedKeywords,
  buildMultilingualSearch
};