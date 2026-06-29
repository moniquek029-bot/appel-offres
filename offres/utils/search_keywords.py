# offres/utils/search_keywords.py
"""
Système de recherche et détection centralisé
"""

# =============================================================================
# DOMAINES - Liste officielle
# =============================================================================
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

# =============================================================================
# DOMAINES - Mots-clés avec poids (plus le poids est élevé, plus c'est fort)
# =============================================================================
MOTS_CLES_DOMAINES = {
    'IT & Digital': {
        'forts': [
            'informatique', 'informatiques', 'logiciel', 'logiciels', 'software',
            'laptop', 'laptops', 'ordinateur', 'ordinateurs', 'computer',
            'développement logiciel', 'programmation', 'programming',
            'base de données', 'database', 'système d\'information',
            'cybersécurité', 'cybersecurity', 'serveur', 'server',
            'cloud', 'infrastructure informatique', 'site web', 'website',
            'internet', 'web', 'hardware', 'matériel informatique',
            'digital', 'numérique', 'ERP', 'SAP', 'CRM',
            'intelligence artificielle', 'blockchain', 'IoT',
            'IT', 'tech', 'technology', 'data', 'données',
            'licence de logiciel', 'licences de logiciels',
            'matériel informatique', 'materiel informatique',
            'équipement informatique', 'equipement informatique',
            'plateforme', 'platform', 'digital platform',
            'information technology', 'coding', 'programming',
            'application', 'applications', 'réseau', 'network',
            'développeur', 'developer', 'site internet'
        ],
        'faibles': [
            'tech', 'digital', 'data',
        ],
    },
    
    'Ingénierie & Construction': {
        'forts': [
            'construction', 'bâtiment', 'batiment', 'travaux publics',
            'infrastructure', 'route', 'routes', 'pont', 'ponts',
            'autoroute', 'génie civil', 'architecture', 'urbanisme',
            'béton', 'ciment', 'immobilier', 'logement', 'BTP',
            'chantier', 'réhabilitation', 'réhabilitation du bâtiment',
            'construction works', 'civil works', 'building',
            'engineering', 'génie', 'génie rural', 'road', 'bridge',
            'architecte'
        ],
        'faibles': [
            'engineering', 'building', 'public works', 'civil engineering',
        ],
    },
    
    'Santé & Médical': {
        'forts': [
            'santé', 'sante', 'médical', 'medical', 'médecine', 'medicine',
            'hôpital', 'hopital', 'clinique', 'pharmacie', 'pharmaceutique',
            'médicament', 'vaccin', 'épidémie', 'maladie', 'patient',
            'soin', 'soins', 'traitement', 'santé publique', 'nutrition',
            'hygiène', 'health', 'healthcare', 'hospital',
            'santé mentale', 'mental health', 'santé reproductive',
            'sexual and reproductive health', 'SRAJ',
            'kits de santé', 'health kits', 'kit sanitaire',
            'production 110 kits', 'kits de sante',
            'asbc', 'association de santé', 'médical', 'laboratoire',
            'covid', 'virus', 'infirmier', 'urgence'
        ],
        'faibles': [
            'OMS', 'WHO', 'UNICEF', 'MSF',
        ],
    },
    
    'Éducation & Formation': {
        'forts': [
            'éducation', 'education', 'école', 'ecole', 'université', 'universite',
            'formation', 'enseignant', 'professeur', 'pédagogie', 'apprentissage',
            'étudiant', 'etudiant', 'curriculum', 'alphabétisation',
            'enseignement', 'collège', 'lycée', 'scientifique', 'recherche',
            'training', 'school', 'university', 'teacher', 'learning',
            'jeunesse', 'youth', 'projets d\'apprentissage',
            'vocational skills', 'skills training', 'formation professionnelle',
            'workshop', 'seminar', 'conférence', 'capacity building'
        ],
        'faibles': [
            'UNESCO', 'pedagogy', 'student',
        ],
    },
    
    'Environnement & Climat': {
        'forts': [
            'environnement', 'environnemental', 'écologie', 'ecologie',
            'climat', 'climatique', 'biodiversité', 'développement durable',
            'renouvelable', 'énergie', 'energie', 'solaire', 'éolien',
            'forêt', 'foret', 'pollution', 'recyclage', 'vert', 'green',
            'environment', 'ecology', 'climate', 'biodiversity',
            'sustainable development', 'renewable', 'forest',
            'changement climatique', 'climate change',
            'climate smart', 'smart agriculture', 'environnemental'
        ],
        'faibles': [
            'recycling', 'green',
        ],
    },
    
    'Finance & Comptabilité': {
        'forts': [
            'finance', 'financier', 'financière', 'banque', 'bancaire',
            'investissement', 'comptabilité', 'audit', 'fiscal', 'budget',
            'trésorerie', 'microfinance', 'crédit', 'épargne', 'assurance',
            'financial', 'bank', 'banking', 'investment', 'accounting',
            'verification', 'vérification', 'spot checks', 'contrôle',
            'paiement', 'facture', 'comptable', 'revenue', 'tax'
        ],
        'faibles': [
            'treasury', 'credit', 'savings', 'insurance',
        ],
    },
    
    'Management & Administration': {
        'forts': [
            'administration', 'administratif', 'management', 'gestion',
            'gouvernance', 'stratégie', 'planning', 'coordination',
            'operations', 'project management', 'programme', 'policy',
            'mobilisation des ressources', 'resource mobilization',
            'expertise', 'renforcement des capacités',
        ],
        'faibles': [
            'governance', 'strategy',
        ],
    },
    
    'Transport & Logistique': {
        'forts': [
            'transport', 'transports', 'logistique', 'mobilité',
            'aéroport', 'aviation', 'maritime', 'ferroviaire',
            'train', 'véhicule', 'véhicules', 'vehicle', 'vehicles',
            'motocyclette', 'motocyclettes', 'motorcycle', 'motorcycles',
            'supply chain', 'procurement', 'purchasing',
            'logistics', 'mobility', 'airport', 'car sale',
            'automobile', 'conducteur', 'chauffeur', 'taxi',
            'livraison', 'camion', 'bus', 'car', 'fret'
        ],
        'faibles': [
            'transportation', 'railway',
        ],
    },
    
    'Agriculture & Alimentation': {
        'forts': [
            'agriculture', 'agricole', 'agronomie', 'élevage', 'cultures',
            'irrigation', 'semence', 'engrais', 'récolte', 'production agricole',
            'sécurité alimentaire', 'rural', 'paysan', 'agroalimentaire',
            'farming', 'livestock', 'food security', 'agricultural',
            'value chain', 'agribusiness', 'pêche', 'poisson',
            'alimentation', 'nourriture', 'céréale', 'riz',
            'maraîcher', 'bétail', 'semences', 'crops', 'food'
        ],
        'faibles': [
            'agricultural', 'agronomy', 'crops', 'seed', 'fertilizer',
        ],
    },
    
    'Eau & Assainissement': {
        'forts': [
            'eau', 'water', 'assainissement', 'sanitation', 'WASH',
            'hydraulique', 'hydrologie', 'potable', 'traitement des eaux',
        ],
        'faibles': [
            'hydraulic', 'hydrology', 'drinking water',
        ],
    },
    
    'Communication & Médias': {
        'forts': [
            'communication', 'média', 'media', 'information publique',
            'journalisme', 'journalistic', 'journalistique',
            'relations publiques', 'marketing', 'social media',
            'couverture journalistique', 'journalistic coverage',
            'correspondants', 'correspondents', 'prix de journalisme',
            'vidéo', 'video', 'documentaire', 'documentary',
            'publicité', 'journal', 'radio', 'tv', 'presse',
            'audiovisuel', 'photo', 'interview', 'reportage'
        ],
        'faibles': [
            'public information', 'public relations',
        ],
    },
    
    'Juridique & Droit': {
        'forts': [
            'juridique', 'legal', 'law', 'judicial', 'court', 'justice',
            'droits humains', 'human rights', 'anti-corruption',
            'droit', 'loi', 'réglementation', 'légal',
            'contrat', 'avocat', 'contentieux', 'regulatory', 'compliance'
        ],
        'faibles': [
            'droit', 'loi',
        ],
    },
    
    'Ressources Humaines': {
        'forts': [
            'ressources humaines', 'human resources', 'HR', 'RH',
            'recrutement', 'recruitment', 'staff', 'personnel',
            'capacity building', 'embauche', 'employé', 'carrière',
            'talent', 'hiring', 'gestion du personnel', 'paie', 'salaire'
        ],
        'faibles': [],
    },
    
    'Sécurité & Protection': {
        'forts': [
            'sécurité', 'securite', 'security', 'safety', 'protection',
            'urgence', 'emergency', 'catastrophe', 'disaster', 'risque', 'risk',
            'boîtiers de sécurité', 'security devices', 'défense', 'armée',
            'militaire', 'garde', 'sûreté', 'police', 'surveillance',
            'vigile', 'sécuritaire', 'protection civile'
        ],
        'faibles': [],
    },
    
    'Social & Égalité': {
        'forts': [
            'genre', 'gender', 'égalité', 'equality', 'femmes', 'women',
            'jeunesse', 'youth', 'enfant', 'child', 'handicap', 'disability',
            'social', 'communauté', 'community', 'pauvreté', 'poverty',
            'inclusion', 'résilience', 'resilience', 'social protection',
            'protection sociale', 'équité', 'masculin', 'féminin',
            'personne âgée', 'enfant', 'mère', 'femmes',
            'égalité homme femme', 'un women', 'social gap',
            'inclusion sociale', 'pauvre', 'vulnerable', 'minority',
            'employment', 'social gap', 'social protection'
        ],
        'faibles': [],
    },
    
    'Biens & Équipements': {
        'forts': [
            'biens', 'goods', 'équipement', 'equipment', 'supplies', 'material',
            'furniture', 'mobilier', 'fourniture', 'produits d\'entretien',
            'produits de nettoyage', 'cleaning products', 'acquisition',
            'achat de produits', 'nettoyage', 'entretien',
            'matériel de bureau', 'équipement de protection',
            'consommables', 'fournitures'
        ],
        'faibles': [],
    },
    
    'Services & Conseil': {
        'forts': [
            'services', 'conseil', 'consultancy', 'consulting', 'advisory',
            'expertise', 'prestation', 'bureau d\'études', 'bureau d\'etudes',
            'recrutement', 'service', 'étude', 'évaluation',
            'assistance', 'support', 'consultant'
        ],
        'faibles': [],
    },
}


# =============================================================================
# FONCTION AMÉLIORÉE DE DÉTECTION DE DOMAINE
# =============================================================================

def detecter_domaine(titre, description=""):
    """
    Détection automatique du domaine d'une offre
    Utilise un système de score pour déterminer le domaine le plus probable
    """
    if not titre:
        return 'Autres'
    
    texte = (titre + " " + (description or "")).lower()
    titre_lower = titre.lower()
    
    scores = {}
    
    for domaine, data in MOTS_CLES_DOMAINES.items():
        score = 0
        
        # Mots-clés forts (poids = 3, ou 6 si dans le titre)
        for mot in data.get('forts', []):
            if mot.lower() in titre_lower:
                score += 6  # Double poids si dans le titre
            elif mot.lower() in texte:
                score += 3
        
        # Mots-clés faibles (poids = 1, ou 2 si dans le titre)
        for mot in data.get('faibles', []):
            if mot.lower() in titre_lower:
                score += 2
            elif mot.lower() in texte:
                score += 1
        
        if score > 0:
            scores[domaine] = score
    
    if scores:
        # Retourner le domaine avec le score le plus élevé
        return max(scores, key=scores.get)
    
    # Si aucun score, vérifier les termes génériques
    if any(mot in texte for mot in ['achat', 'fourniture', 'purchase', 'supply', 'acquisition']):
        return 'Biens & Équipements'
    
    if any(mot in texte for mot in ['étude', 'consultant', 'consultancy', 'advisory', 'expertise']):
        return 'Services & Conseil'
    
    if any(mot in texte for mot in ['appel d\'offres', 'tender', 'bid', 'appel d\'offre']):
        return 'Services & Conseil'
    
    return 'Autres'


# =============================================================================
# PAYS - Codes ISO et noms
# =============================================================================
COUNTRIES = {
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
}


# =============================================================================
# AUTRES FONCTIONS UTILITAIRES
# =============================================================================

def get_domain_keywords(domain: str) -> list:
    """Retourne tous les mots-clés associés à un domaine"""
    if not domain:
        return []
    
    if domain in MOTS_CLES_DOMAINES:
        data = MOTS_CLES_DOMAINES[domain]
        return data.get('forts', []) + data.get('faibles', [])
    
    for key, data in MOTS_CLES_DOMAINES.items():
        if key.lower() == domain.lower():
            return data.get('forts', []) + data.get('faibles', [])
    
    return [domain]
# offres/utils/search_keywords.py - Ajouter à la fin du fichier

# =============================================================================
# DÉTECTION DU TYPE D'OFFRE
# =============================================================================

def detecter_type_offre(titre, description=""):
    """
    Détecte le type d'offre (Appel d'offres, Appel à projets, etc.)
    """
    if not titre:
        return 'APPEL_D_OFFRES'
    
    texte = (titre + " " + (description or "")).lower()
    
    # ✅ 1. Appel d'offres (RFQ/RFP)
    mots_cles_appel_offres = [
        'rfq', 'request for quotation', 'demande de cotation',
        'rfp', 'request for proposal', 'demande de proposition',
        'tender', 'appel d\'offres', 'appel d\'offre', 'call for tender',
        'procurement', 'marché public', 'marchés publics',
        'acquisition', 'achat', 'fourniture', 'travaux', 'prestation',
        'demande de prix', 'price request', 'invitation à soumissionner'
    ]
    if any(mot in texte for mot in mots_cles_appel_offres):
        return 'APPEL_D_OFFRES'
    
    # ✅ 2. Appel à projets
    mots_cles_appel_projets = [
        'call for proposal', 'appel à projets', 'appel à projet',
        'call for projects', 'proposal call', 'project call',
        'biodiversity credit', 'pilot project', 'community project'
    ]
    if any(mot in texte for mot in mots_cles_appel_projets):
        return 'APPEL_A_PROJETS'
    
    # ✅ 3. Manifestation d'intérêt
    mots_cles_eoi = [
        'expression of interest', 'manifestation d\'intérêt', 'manifestation d\'interet',
        'eoi', 'call for expression', 'appel à manifestation d\'intérêt'
    ]
    if any(mot in texte for mot in mots_cles_eoi):
        return 'MANIFESTATION_INTERET'
    
    # ✅ 4. Vente aux enchères
    mots_cles_vente = [
        'car sale', 'vehicle sale', 'vente de voiture', 'vente de véhicule',
        'auction', 'enchères', 'enchère', 'sale of', 'for sale'
    ]
    if any(mot in texte for mot in mots_cles_vente):
        return 'VENTE_AUX_ENCHERES'
    
    # ✅ 5. Recrutement / Consultant
    mots_cles_recrutement = [
        'recrutement', 'recruitment', 'consultant', 'hiring', 'embauche',
        'expert', 'consultancy', 'consulting', 'auditeur', 'auditeur externe',
        'bureau d\'études', 'bureau d\'etudes', 'prestation de services'
    ]
    if any(mot in texte for mot in mots_cles_recrutement):
        return 'RECRUTEMENT'
    
    # ✅ Par défaut : Appel d'offres
    return 'APPEL_D_OFFRES'

# offres/utils/search_keywords.py - Ajouter à la fin

def est_appel_offres(titre, description=""):
    """
    Vérifie si une offre est un VRAI appel d'offres (RFQ/RFP)
    Retourne True si c'est un appel d'offres, False sinon
    """
    if not titre:
        return False
    
    texte = (titre + " " + (description or "")).lower()
    
    # ✅ MOTS-CLÉS QUI INDIQUENT UN APPEL D'OFFRES
    mots_cles_appel_offres = [
        # Français
        'rfq', 'rpf', 'appel d\'offres', 'appel d\'offre', 'demande de cotation',
        'demande de proposition', 'marché public', 'marchés publics',
        'avis d\'appel d\'offres', 'avis d\'appel d\'offre',
        'invitation à soumissionner', 'invitation à soumissionner',
        'cotation', 'fourniture', 'acquisition', 'travaux', 'prestation',
        'demande de prix', 'appel à concurrence',
        
        # Anglais
        'request for quotation', 'request for proposal', 'request for tender',
        'call for tender', 'invitation to tender', 'tender notice',
        'procurement notice', 'bidding', 'bid notice',
        'supply', 'procurement', 'purchase', 'acquisition',
        
        # Types d'appels d'offres (UNDP, UNFPA, etc.)
        'rfq_', 'rfp_', 'ref no', 'procurement', 'tender',
    ]
    
    # Vérifier si des mots-clés d'appel d'offres sont présents
    for mot in mots_cles_appel_offres:
        if mot in texte:
            return True
    
    # ✅ MOTS-CLÉS QUI EXCLUENT (ne sont PAS des appels d'offres)
    mots_cles_exclusion = [
        # Recrutement
        'recrutement', 'recruitment', 'consultant', 'hiring', 'embauche',
        'bureau d\'études', 'bureau d\'etudes', 'expertise',
        
        # Vente
        'car sale', 'vehicle sale', 'vente de voiture', 'vente de véhicule',
        'auction', 'enchères', 'for sale', 'à vendre',
        
        # Appels à projets
        'call for proposal', 'appel à projets', 'appel à projet',
        'call for projects', 'project call', 'biodiversity credit',
        'pilot project', 'community project',
        
        # Manifestations d'intérêt
        'expression of interest', 'manifestation d\'intérêt', 'manifestation d\'interet',
        'eoi', 'call for expression',
        
        # Autres
        'job', 'emploi', 'stage', 'internship', 'volunteer', 'bénévolat',
        'fellowship', 'poste', 'position', 'vacancy', 'recrutement',
        'formation', 'training', 'workshop', 'seminar', 'conférence',
    ]
    
    # Si un mot d'exclusion est présent, ce n'est PAS un appel d'offres
    for mot in mots_cles_exclusion:
        if mot in texte:
            return False
    
    return False   

def get_country_codes(country_query: str) -> list:
    """Retourne les codes pays correspondant à une requête"""
    if not country_query:
        return []
    
    query_lower = country_query.lower().strip()
    matching_codes = []
    
    for code, names in COUNTRIES.items():
        if code.lower() == query_lower:
            matching_codes.append(code)
            continue
        
        for name in names:
            if query_lower in name.lower() or name.lower() in query_lower:
                matching_codes.append(code)
                break
    
    return list(set(matching_codes))



# À la fin de offres/utils/search_keywords.py

def est_appel_offres(titre: str, description: str = "") -> bool:
    """
    Vérifie si un texte correspond à un VRAI appel d'offres (RFQ/RFP)
    Exclut : actualités, résultats, prix, guides, etc.
    """
    if not titre:
        return False
    
    texte = (titre + ' ' + description).lower()
    
    # ✅ MOTS-CLÉS QUI CONFIRMENT un appel d'offres
    mots_cles_confirmation = [
        'rfq', 'rfp', 'eoi', 'iti', 'itt', 'sdp',
        'demande de cotation', 'demande de proposition',
        'appel d\'offres', 'avis de recrutement',
        'avis à manifestation', 'manifestation d\'intérêt',
        'achat de', 'acquisition de', 'fourniture de',
        'travaux de', 'recrutement d\'un bureau',
        'bureau d\'études', 'cotation pour',
        'request for quotation', 'request for proposal',
        'expression of interest', 'invitation to bid',
    ]
    
    # ❌ MOTS-CLÉS QUI EXCLUENT un appel d'offres
    mots_cles_exclusion = [
        'résultats des appels', 'attribution du marché',
        'actualité', 'après niamey', 'met le cap sur',
        'déploie son expertise', 'prix de l\'association',
        'prix de la meilleure', 'récompense', 'award',
        'défi d\'innovation', 'concours', 'challenge',
        '#creatives', 'appel à projets', 'appel ouvert pour',
        'programme de leadership', 'candidatures ouvertes',
        'formation des organisations', 'session intensive',
        'comment s\'enregistrer', 'trouver des offres',
        'guide', 'tutoriel', 'live notices', 'showing 1 to',
    ]
    
    # Vérifier les exclusions en priorité
    for mot in mots_cles_exclusion:
        if mot in texte:
            return False
    
    # Vérifier les confirmations
    for mot in mots_cles_confirmation:
        if mot in texte:
            return True
    
    # Si aucun mot-clé trouvé, rejeter par défaut
    return False