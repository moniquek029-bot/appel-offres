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
# DOMAINES - Mots-clés avec poids
# =============================================================================
MOTS_CLES_DOMAINES = {
    'IT & Digital': {
        'forts': [
            'informatique', 'logiciel', 'ordinateur', 'laptop', 'computer',
            'développement logiciel', 'programmation', 'base de données',
            'cybersécurité', 'serveur', 'cloud', 'infrastructure informatique',
            'site web', 'internet', 'hardware', 'matériel informatique',
            'digital', 'numérique', 'ERP', 'SAP', 'CRM', 'data', 'données',
            'licence logiciel', 'équipement informatique', 'plateforme',
            'digital platform', 'information technology', 'coding',
            'application', 'réseau', 'network', 'développeur'
        ],
        'faibles': ['tech', 'digital', 'data'],
    },
    
    'Ingénierie & Construction': {
        'forts': [
            'construction', 'bâtiment', 'travaux publics', 'infrastructure',
            'route', 'pont', 'autoroute', 'génie civil', 'architecture',
            'urbanisme', 'béton', 'ciment', 'immobilier', 'BTP', 'chantier',
            'réhabilitation', 'génie rural', 'engineering', 'civil works'
        ],
        'faibles': ['engineering', 'building', 'public works'],
    },
    
    'Santé & Médical': {
        'forts': [
            'santé', 'médical', 'hôpital', 'clinique', 'pharmacie',
            'pharmaceutique', 'médicament', 'vaccin', 'patient', 'soins',
            'médecine', 'urgence', 'laboratoire', 'health', 'healthcare',
            'SRAJ', 'kits de santé', 'matériel médical', 'infirmier'
        ],
        'faibles': ['OMS', 'WHO', 'UNICEF'],
    },
    
    'Éducation & Formation': {
        'forts': [
            'éducation', 'formation', 'école', 'université', 'enseignement',
            'apprentissage', 'pédagogie', 'étudiant', 'curriculum',
            'training', 'school', 'university', 'teacher', 'learning',
            'vocational skills', 'skills training', 'formation professionnelle',
            'workshop', 'seminar', 'capacity building'
        ],
        'faibles': ['UNESCO', 'pedagogy'],
    },
    
    'Environnement & Climat': {
        'forts': [
            'environnement', 'écologie', 'climat', 'biodiversité',
            'développement durable', 'renouvelable', 'énergie', 'solaire',
            'éolien', 'recyclage', 'vert', 'environment', 'climate',
            'energy', 'renewable', 'sustainable', 'green',
            'changement climatique', 'climate smart'
        ],
        'faibles': ['recycling', 'green'],
    },
    
    'Finance & Comptabilité': {
        'forts': [
            'finance', 'financier', 'banque', 'investissement', 'comptabilité',
            'audit', 'fiscal', 'budget', 'trésorerie', 'microfinance',
            'crédit', 'assurance', 'financial', 'accounting', 'audit',
            'verification', 'vérification', 'spot checks', 'contrôle',
            'paiement', 'facture', 'comptable'
        ],
        'faibles': ['treasury', 'credit', 'savings'],
    },
    
    'Management & Administration': {
        'forts': [
            'administration', 'management', 'gestion', 'gouvernance',
            'stratégie', 'planning', 'coordination', 'project management',
            'programme', 'policy', 'mobilisation des ressources',
            'expertise', 'renforcement des capacités'
        ],
        'faibles': ['governance', 'strategy'],
    },
    
    'Transport & Logistique': {
        'forts': [
            'transport', 'logistique', 'mobilité', 'véhicule', 'motocyclette',
            'livraison', 'camion', 'bus', 'car', 'fret', 'logistics',
            'delivery', 'vehicle', 'motorcycle', 'car sale', 'automobile',
            'supply chain', 'procurement'
        ],
        'faibles': ['transportation', 'railway'],
    },
    
    'Agriculture & Alimentation': {
        'forts': [
            'agriculture', 'agronomie', 'élevage', 'cultures', 'irrigation',
            'semence', 'engrais', 'récolte', 'production agricole',
            'sécurité alimentaire', 'rural', 'paysan', 'agroalimentaire',
            'farming', 'livestock', 'food security', 'agricultural',
            'value chain', 'agribusiness', 'alimentation', 'nourriture'
        ],
        'faibles': ['agricultural', 'agronomy', 'crops', 'seed'],
    },
    
    'Eau & Assainissement': {
        'forts': [
            'eau', 'water', 'assainissement', 'sanitation', 'WASH',
            'hydraulique', 'hydrologie', 'potable', 'traitement des eaux'
        ],
        'faibles': ['hydraulic', 'hydrology'],
    },
    
    'Communication & Médias': {
        'forts': [
            'communication', 'média', 'information publique', 'journalisme',
            'relations publiques', 'marketing', 'social media', 'vidéo',
            'documentaire', 'publicité', 'journal', 'radio', 'tv', 'presse',
            'audiovisuel', 'media', 'video', 'documentary', 'photo'
        ],
        'faibles': ['public information', 'public relations'],
    },
    
    'Juridique & Droit': {
        'forts': [
            'juridique', 'droit', 'loi', 'réglementation', 'légal',
            'contrat', 'avocat', 'justice', 'contentieux', 'legal',
            'law', 'contract', 'regulatory', 'compliance'
        ],
        'faibles': ['droit', 'loi'],
    },
    
    'Ressources Humaines': {
        'forts': [
            'ressources humaines', 'rh', 'recrutement', 'embauche',
            'personnel', 'staff', 'employé', 'carrière', 'talent',
            'human resources', 'hr', 'recruitment', 'hiring'
        ],
        'faibles': [],
    },
    
    'Sécurité & Protection': {
        'forts': [
            'sécurité', 'protection', 'défense', 'armée', 'militaire',
            'garde', 'sûreté', 'police', 'security', 'protection',
            'safety', 'military', 'surveillance', 'vigile'
        ],
        'faibles': [],
    },
    
    'Social & Égalité': {
        'forts': [
            'social', 'égalité', 'femme', 'jeune', 'égalité des genres',
            'pauvreté', 'humanitaire', 'inclusion', 'solidarité',
            'social protection', 'women', 'gender', 'youth', 'empowerment',
            'vulnerable', 'minority', 'un women', 'social gap',
            'inclusion sociale', 'protection sociale'
        ],
        'faibles': [],
    },
    
    'Biens & Équipements': {
        'forts': [
            'biens', 'équipement', 'matériel', 'fourniture', 'achat',
            'acquisition', 'livraison', 'fournitures', 'consommables',
            'equipment', 'supplies', 'procurement', 'purchase', 'goods',
            'matériel de bureau', 'mobilier', 'équipement de protection'
        ],
        'faibles': [],
    },
    
    'Services & Conseil': {
        'forts': [
            'service', 'conseil', 'consulting', 'consultant', 'étude',
            'expertise', 'évaluation', 'assistance', 'support',
            'services', 'consultancy', 'advisory'
        ],
        'faibles': [],
    },
}

# =============================================================================
# FONCTION DE DÉTECTION DE DOMAINE
# =============================================================================

def detecter_domaine(titre, description=""):
    """
    Détection automatique du domaine d'une offre
    """
    if not titre:
        return 'Autres'
    
    texte = (titre + " " + (description or "")).lower()
    titre_lower = titre.lower()
    
    scores = {}
    
    for domaine, data in MOTS_CLES_DOMAINES.items():
        score = 0
        
        for mot in data.get('forts', []):
            if mot.lower() in titre_lower:
                score += 6
            elif mot.lower() in texte:
                score += 3
        
        for mot in data.get('faibles', []):
            if mot.lower() in titre_lower:
                score += 2
            elif mot.lower() in texte:
                score += 1
        
        if score > 0:
            scores[domaine] = score
    
    if scores:
        return max(scores, key=scores.get)
    
    if any(mot in texte for mot in ['achat', 'fourniture', 'purchase', 'supply', 'acquisition']):
        return 'Biens & Équipements'
    if any(mot in texte for mot in ['étude', 'consultant', 'consultancy', 'advisory', 'expertise']):
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
# DÉTECTION DU TYPE D'OFFRE
# =============================================================================

def detecter_type_offre(titre, description=""):
    """
    Détecte le type d'offre (Appel d'offres, Appel à projets, etc.)
    """
    if not titre:
        return 'APPEL_D_OFFRES'
    
    texte = (titre + " " + (description or "")).lower()
    
    mots_cles_appel_offres = [
        'rfq', 'request for quotation', 'demande de cotation',
        'rfp', 'request for proposal', 'demande de proposition',
        'tender', 'appel d\'offres', 'call for tender',
        'procurement', 'marché public', 'acquisition',
        'achat', 'fourniture', 'travaux', 'prestation',
        'demande de prix', 'invitation à soumissionner'
    ]
    if any(mot in texte for mot in mots_cles_appel_offres):
        return 'APPEL_D_OFFRES'
    
    mots_cles_appel_projets = [
        'call for proposal', 'appel à projets', 'call for projects',
        'biodiversity credit', 'pilot project', 'community project'
    ]
    if any(mot in texte for mot in mots_cles_appel_projets):
        return 'APPEL_A_PROJETS'
    
    mots_cles_eoi = [
        'expression of interest', 'manifestation d\'intérêt',
        'eoi', 'call for expression'
    ]
    if any(mot in texte for mot in mots_cles_eoi):
        return 'MANIFESTATION_INTERET'
    
    mots_cles_vente = [
        'car sale', 'vehicle sale', 'vente de voiture',
        'auction', 'enchères', 'for sale'
    ]
    if any(mot in texte for mot in mots_cles_vente):
        return 'VENTE_AUX_ENCHERES'
    
    mots_cles_recrutement = [
        'recrutement', 'recruitment', 'consultant', 'hiring',
        'bureau d\'études', 'bureau d\'etudes', 'prestation de services'
    ]
    if any(mot in texte for mot in mots_cles_recrutement):
        return 'RECRUTEMENT'
    
    return 'APPEL_D_OFFRES'

# =============================================================================
# VÉRIFICATION SI C'EST UN APPEL D'OFFRES
# =============================================================================

def est_appel_offres(titre: str, description: str = "") -> bool:
    """
    Vérifie si une offre est un VRAI appel d'offres (RFQ/RFP)
    Exclut : actualités, résultats, prix, guides, etc.
    """
    if not titre:
        return False
    
    texte = (titre + ' ' + description).lower()
    
    # ✅ MOTS-CLÉS QUI CONFIRMENT un appel d'offres
    mots_cles_confirmation = [
        'rfq', 'rfp', 'eoi', 'iti', 'itt', 'sdp',
        'demande de cotation', 'demande de proposition',
        'appel d\'offres', 'appel d\'offre', 'avis d\'appel d\'offres',
        'avis à manifestation', 'manifestation d\'intérêt',
        'achat de', 'acquisition de', 'fourniture de',
        'travaux de', 'cotation pour',
        'request for quotation', 'request for proposal',
        'expression of interest', 'invitation to bid',
        'marché public', 'procurement notice', 'tender notice'
    ]
    
    # ❌ MOTS-CLÉS QUI EXCLUENT un appel d'offres
    mots_cles_exclusion = [
        'résultats des appels', 'attribution du marché',
        'actualité', 'met le cap sur',
        'déploie son expertise', 'prix de l\'association',
        'prix de la meilleure', 'récompense', 'award',
        'défi d\'innovation', 'concours', 'challenge',
        '#creatives', 'appel à projets', 'appel ouvert pour',
        'programme de leadership', 'candidatures ouvertes',
        'formation des organisations', 'session intensive',
        'comment s\'enregistrer', 'trouver des offres',
        'guide', 'tutoriel', 'live notices', 'showing 1 to',
        'javni poziv', 'poziv', 'programu', 'održivi', 'rast',
        'analysis of social protection', 'social protection gaps',
        'car sale', 'vehicle sale', 'vente de voiture', 'auction'
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

# =============================================================================
# FONCTIONS UTILITAIRES
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