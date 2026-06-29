// src/utils/searchKeywords.js
/**
 * Système de recherche multilingue centralisé
 * Contient : domaines, pays, dates
 */

// =============================================================================
// DOMAINES - Liste officielle (doit correspondre au backend)
// =============================================================================
export const DOMAINES_STANDARDS = [
  'IT & Digital',
  'Ingénierie & Construction',
  'Santé & Médical',
  'Éducation & Formation',
  'Environnement & Climat',
  'Finance & Comptabilité',
  'Management & Administration',
  'Transport & Logistique',
  'Agriculture & Alimentation',
  'Eau & Assainissement',
  'Communication & Médias',
  'Juridique & Droit',
  'Ressources Humaines',
  'Sécurité & Protection',
  'Social & Égalité',
  'Biens & Équipements',
  'Services & Conseil',
  'Autres',
];

// =============================================================================
// DOMAINES - Mots-clés multilingues
// =============================================================================
export const DOMAIN_KEYWORDS = {
  'IT & Digital': [
    'informatique', 'logiciel', 'software', 'application', 'développement',
    'programmation', 'base de données', 'database', 'système d\'information',
    'cybersécurité', 'serveur', 'cloud', 'site web', 'website',
    'ordinateur', 'computer', 'hardware', 'digital', 'numérique',
    'ERP', 'SAP', 'CRM', 'intelligence artificielle', 'blockchain', 'IoT',
    'IT', 'tech', 'technology', 'data', 'données', 'développeur', 'developer',
    'réseau', 'network', 'web', 'ups', 'electrical', 'data center',
  ],
  
  'Ingénierie & Construction': [
    'ingénierie', 'engineering', 'construction', 'bâtiment', 'building',
    'travaux publics', 'public works', 'infrastructure', 'route', 'road',
    'pont', 'bridge', 'autoroute', 'highway', 'génie civil', 'civil engineering',
    'architecture', 'urbanisme', 'urban planning', 'béton', 'concrete',
    'ciment', 'immobilier', 'real estate', 'logement', 'BTP', 'chantier',
  ],
  
  'Santé & Médical': [
    'santé', 'sante', 'health', 'médical', 'medical', 'médecine', 'medicine',
    'hôpital', 'hospital', 'clinique', 'clinic', 'pharmacie', 'pharmacy',
    'pharmaceutique', 'pharmaceutical', 'médicament', 'drug', 'vaccin', 'vaccine',
    'épidémie', 'epidemic', 'maladie', 'disease', 'patient', 'soin', 'care',
    'soins', 'traitement', 'treatment', 'santé publique', 'public health',
    'nutrition', 'hygiène', 'hygiene', 'OMS', 'WHO', 'UNICEF', 'MSF',
  ],
  
  'Éducation & Formation': [
    'éducation', 'education', 'école', 'school', 'université', 'university',
    'formation', 'training', 'enseignant', 'teacher', 'professeur', 'professor',
    'pédagogie', 'pedagogy', 'apprentissage', 'learning', 'étudiant', 'student',
    'curriculum', 'alphabétisation', 'literacy', 'enseignement', 'teaching',
    'collège', 'college', 'lycée', 'scientifique', 'scientific', 'recherche',
    'research', 'UNESCO',
  ],
  
  'Environnement & Climat': [
    'environnement', 'environment', 'environnemental', 'environmental',
    'écologie', 'ecology', 'écologique', 'ecological', 'climat', 'climate',
    'climatique', 'climatic', 'biodiversité', 'biodiversity',
    'développement durable', 'sustainable development', 'renouvelable', 'renewable',
    'énergie', 'energy', 'solaire', 'solar', 'éolien', 'wind',
    'forêt', 'forest', 'pollution', 'recyclage', 'recycling', 'vert', 'green',
  ],
  
  'Finance & Comptabilité': [
    'finance', 'financial', 'financier', 'banque', 'bank', 'bancaire', 'banking',
    'investissement', 'investment', 'comptabilité', 'accounting', 'audit',
    'fiscal', 'budget', 'trésorerie', 'treasury', 'microfinance',
    'crédit', 'credit', 'épargne', 'savings', 'assurance', 'insurance',
  ],
  
  'Management & Administration': [
    'administration', 'administrative', 'administratif', 'management',
    'gestion', 'gouvernance', 'governance', 'stratégie', 'strategy',
    'planning', 'coordination', 'operations', 'project management', 'programme',
  ],
  
  'Transport & Logistique': [
    'transport', 'logistique', 'logistics', 'mobilité', 'mobility',
    'aéroport', 'airport', 'aviation', 'maritime', 'ferroviaire', 'railway',
    'train', 'véhicule', 'vehicle', 'supply chain', 'procurement', 'purchasing',
  ],
  
  'Agriculture & Alimentation': [
    'agriculture', 'agricultural', 'agricole', 'agronomie', 'agronomy',
    'élevage', 'livestock', 'cultures', 'crops', 'irrigation',
    'semence', 'seed', 'engrais', 'fertilizer', 'récolte', 'harvest',
    'production agricole', 'agricultural production', 'sécurité alimentaire',
    'food security', 'rural', 'paysan', 'farmer', 'agroalimentaire', 'agro-food',
    'farming',
  ],
  
  'Eau & Assainissement': [
    'eau', 'water', 'assainissement', 'sanitation', 'WASH', 'hydraulique',
    'hydraulic', 'hydrologie', 'hydrology', 'potable', 'drinking water',
    'traitement des eaux', 'water treatment',
  ],
  
  'Communication & Médias': [
    'communication', 'média', 'media', 'information publique', 'public information',
    'journalisme', 'journalism', 'relations publiques', 'public relations',
    'marketing', 'social media',
  ],
  
  'Juridique & Droit': [
    'juridique', 'legal', 'droit', 'law', 'justice', 'rights',
    'droits humains', 'human rights', 'anti-corruption',
  ],
  
  'Ressources Humaines': [
    'ressources humaines', 'human resources', 'HR', 'recrutement', 'recruitment',
    'personnel', 'staff', 'capacity building',
  ],
  
  'Sécurité & Protection': [
    'sécurité', 'security', 'protection', 'urgence', 'emergency',
    'catastrophe', 'disaster', 'risque', 'risk',
  ],
  
  'Social & Égalité': [
    'genre', 'gender', 'égalité', 'equality', 'femmes', 'women',
    'jeunesse', 'youth', 'enfant', 'child', 'handicap', 'disability',
    'social', 'communauté', 'community', 'pauvreté', 'poverty', 'inclusion',
  ],
  
  'Biens & Équipements': [
    'biens', 'goods', 'équipement', 'equipment', 'fourniture', 'supplies',
    'matériel', 'material', 'mobilier', 'furniture',
  ],
  
  'Services & Conseil': [
    'services', 'conseil', 'consultancy', 'consulting', 'advisory',
    'expertise', 'prestation',
  ],
};

// =============================================================================
// PAYS - Codes ISO et noms
// =============================================================================
export const COUNTRIES = {
  'BF': ['Burkina Faso', 'Burkina', 'BF'],
  'BJ': ['Bénin', 'Benin', 'BJ'],
  'CI': ['Côte d\'Ivoire', 'Cote d\'Ivoire', 'Ivory Coast', 'CI'],
  'SN': ['Sénégal', 'Senegal', 'SN'],
  'ML': ['Mali', 'ML'],
  'NE': ['Niger', 'NE'],
  'TG': ['Togo', 'TG'],
  'CM': ['Cameroun', 'Cameroon', 'CM'],
  'GA': ['Gabon', 'GA'],
  'NG': ['Nigeria', 'NG'],
  'RW': ['Rwanda', 'RW'],
  'GH': ['Ghana', 'GH'],
  'AR': ['Argentine', 'Argentina', 'AR'],
  'ID': ['Indonésie', 'Indonesia', 'ID'],
  'BA': ['Bosnie-Herzégovine', 'Bosnia', 'BA'],
  'US': ['États-Unis', 'United States', 'USA', 'US'],
  'GB': ['Royaume-Uni', 'United Kingdom', 'UK', 'GB'],
  'FR': ['France', 'FR'],
  'DE': ['Allemagne', 'Germany', 'DE'],
  // ... (ajouter les autres pays si nécessaire)
};

// =============================================================================
// FONCTIONS UTILITAIRES
// =============================================================================

/**
 * Obtient tous les mots-clés associés à un domaine
 */
export const getDomainKeywords = (domain) => {
  if (!domain) return [];
  
  const domainNormalized = domain.trim();
  
  // Recherche directe
  if (DOMAIN_KEYWORDS[domainNormalized]) {
    return DOMAIN_KEYWORDS[domainNormalized];
  }
  
  // Recherche insensible à la casse
  for (const [key, values] of Object.entries(DOMAIN_KEYWORDS)) {
    if (key.toLowerCase() === domainNormalized.toLowerCase()) {
      return values;
    }
  }
  
  return [domainNormalized];
};

/**
 * Obtient les codes pays correspondant à une requête
 */
export const getCountryCodes = (countryQuery) => {
  if (!countryQuery) return [];
  
  const queryLower = countryQuery.toLowerCase().trim();
  const matchingCodes = [];
  
  for (const [code, names] of Object.entries(COUNTRIES)) {
    if (code.toLowerCase() === queryLower) {
      matchingCodes.push(code);
      continue;
    }
    
    for (const name of names) {
      if (queryLower.includes(name.toLowerCase()) || name.toLowerCase().includes(queryLower)) {
        matchingCodes.push(code);
        break;
      }
    }
  }
  
  return [...new Set(matchingCodes)];
};

/**
 * Obtient tous les mots-clés associés à un mot-clé
 */
export const getRelatedKeywords = (keyword) => {
  if (!keyword) return [];
  
  const keywordLower = keyword.toLowerCase().trim();
  const related = new Set([keywordLower]);
  
  for (const [domain, keywords] of Object.entries(DOMAIN_KEYWORDS)) {
    for (const kw of keywords) {
      if (kw.toLowerCase() === keywordLower || keywordLower.includes(kw.toLowerCase())) {
        keywords.forEach(k => related.add(k.toLowerCase()));
        break;
      }
    }
  }
  
  return Array.from(related);
};

/**
 * Crée une requête de recherche multilingue
 */
export const buildMultilingualSearch = (keyword) => {
  if (!keyword || keyword.trim() === '') return '';
  
  const relatedKeywords = getRelatedKeywords(keyword);
  return relatedKeywords.join(' | ');
};

export default {
  DOMAINES_STANDARDS,
  DOMAIN_KEYWORDS,
  COUNTRIES,
  getDomainKeywords,
  getCountryCodes,
  getRelatedKeywords,
  buildMultilingualSearch,
};