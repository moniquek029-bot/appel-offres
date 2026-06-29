# offres/scraping/constantes.py
"""
Constantes partagées entre frontend et backend
"""

# ✅ DOMAINES STANDARDS (doit correspondre au frontend React)
DOMAINES_STANDARDS = [
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
]

# ✅ MAPPING DES MOTS-CLÉS VERS DOMAINES
MOTS_CLES_DOMAINES = {
    'IT & Digital': [
        'informatique', 'informatiques', 'logiciel', 'logiciels', 'software',
        'application', 'applications', 'développement logiciel', 'programmation',
        'base de données', 'database', 'système d\'information', 'cybersécurité',
        'serveur', 'server', 'cloud', 'infrastructure informatique', 'site web',
        'website', 'internet', 'web', 'ordinateur', 'computer', 'hardware',
        'digital', 'numérique', 'ERP', 'SAP', 'CRM', 'intelligence artificielle',
        'blockchain', 'IoT', 'internet des objets', 'IT', 'tech', 'technology',
        'ups', 'electrical', 'data center', 'processing',
    ],
    
    'Ingénierie & Construction': [
        'ingénierie', 'engineering', 'construction', 'bâtiment', 'batiment',
        'travaux publics', 'infrastructure', 'infrastructures', 'route', 'routes',
        'pont', 'ponts', 'autoroute', 'génie civil', 'architecture', 'urbanisme',
        'aménagement', 'béton', 'ciment', 'matériaux', 'immobilier', 'logement',
        'habitat', 'BTP', 'civil works', 'building',
    ],
    
    'Santé & Médical': [
        'santé', 'sante', 'médical', 'medical', 'médecine', 'medecine',
        'hôpital', 'hopital', 'clinique', 'pharmacie', 'pharmaceutique',
        'médicament', 'medicament', 'vaccin', 'épidémie', 'epidemie',
        'maladie', 'patient', 'soin', 'soins', 'traitement', 'santé publique',
        'nutrition', 'hygiène', 'hygiene', 'health', 'OMS', 'WHO',
    ],
    
    'Éducation & Formation': [
        'éducation', 'education', 'école', 'ecole', 'université', 'universite',
        'formation', 'enseignant', 'professeur', 'pédagogie', 'pedagogie',
        'apprentissage', 'étudiant', 'etudiant', 'curriculum', 'alphabétisation',
        'enseignement', 'collège', 'lycée', 'training', 'learning',
        'scientifique', 'scientific', 'tecnológico', 'research', 'recherche',
    ],
    
    'Environnement & Climat': [
        'environnement', 'environnemental', 'environnementale', 'écologie',
        'ecologie', 'écologique', 'ecologique', 'climat', 'climatique',
        'biodiversité', 'biodiversite', 'développement durable', 'durable',
        'renouvelable', 'énergie', 'energie', 'solaire', 'éolien', 'eolien',
        'forêt', 'foret', 'déforestation', 'pollution', 'recyclage', 'environment',
        'climate', 'green', 'sustainable',
    ],
    
    'Finance & Comptabilité': [
        'finance', 'financier', 'financière', 'banque', 'bancaire',
        'investissement', 'comptabilité', 'comptabilite', 'audit', 'fiscal',
        'budget', 'trésorerie', 'tresorerie', 'microfinance', 'crédit', 'credit',
        'épargne', 'epargne', 'assurance', 'bourse', 'marché financier',
        'finance', 'accounting', 'banking',
    ],
    
    'Management & Administration': [
        'administration', 'administratif', 'management', 'gestion', 'gouvernance',
        'policy', 'stratégie', 'strategy', 'planning', 'coordination',
        'operations', 'project management', 'programme', 'coordination',
    ],
    
    'Transport & Logistique': [
        'transport', 'transports', 'logistique', 'mobilité', 'mobilite',
        'aéroport', 'aeroport', 'aérien', 'aerien', 'aviation', 'maritime',
        'portuaire', 'ferroviaire', 'train', 'rail', 'routier', 'véhicule',
        'vehicule', 'automobile', 'supply chain', 'procurement', 'purchasing',
    ],
    
    'Agriculture & Alimentation': [
        'agriculture', 'agricole', 'agricoles', 'agronomie', 'agronome',
        'élevage', 'elevage', 'cultures', 'irrigation', 'semence', 'semences',
        'engrais', 'pesticide', 'récolte', 'recolte', 'production agricole',
        'sécurité alimentaire', 'famine', 'rural', 'paysan', 'agroalimentaire',
        'farming', 'livestock', 'crops', 'food security',
    ],
    
    'Eau & Assainissement': [
        'eau', 'water', 'assainissement', 'sanitation', 'WASH', 'hygiène',
        'hygiene', 'drinking', 'sewerage', 'hydraulique', 'hydrologie',
    ],
    
    'Communication & Médias': [
        'communication', 'média', 'media', 'public information', 'journalism',
        'public relations', 'marketing', 'branding', 'social media', 'content',
        'faith-based', 'media', 'engaging',
    ],
    
    'Juridique & Droit': [
        'juridique', 'legal', 'law', 'judicial', 'court', 'justice',
        'human rights', 'anti-corruption', 'droit', 'loi',
    ],
    
    'Ressources Humaines': [
        'ressources humaines', 'human resources', 'HR', 'recrutement',
        'recruitment', 'staff', 'personnel', 'capacity building',
    ],
    
    'Sécurité & Protection': [
        'sécurité', 'securite', 'security', 'safety', 'protection',
        'emergency', 'disaster', 'risk', 'crisis',
    ],
    
    'Social & Égalité': [
        'genre', 'gender', 'equality', 'women', 'youth', 'child',
        'disability', 'indigenous', 'social', 'community', 'poverty', 'inclusion',
    ],
    
    'Biens & Équipements': [
        'biens', 'goods', 'equipment', 'supplies', 'material', 'furniture',
        'office', 'fourniture', 'équipement',
    ],
    
    'Services & Conseil': [
        'services', 'consultancy', 'consulting', 'advisory', 'expertise',
        'conseil', 'prestation',
    ],
}


def detecter_domaine(texte: str) -> str:
    """
    Détecte le domaine à partir d'un texte
    Retourne le domaine standard ou 'Autres'
    """
    if not texte:
        return 'Autres'
    
    texte_lower = texte.lower()
    
    # Compter les occurrences pour chaque domaine
    scores = {}
    for domaine, mots_cles in MOTS_CLES_DOMAINES.items():
        score = 0
        for mot in mots_cles:
            if mot.lower() in texte_lower:
                score += 1
        if score > 0:
            scores[domaine] = score
    
    # Retourner le domaine avec le score le plus élevé
    if scores:
        return max(scores, key=scores.get)
    
    return 'Autres'