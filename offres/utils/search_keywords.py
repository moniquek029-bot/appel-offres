"""
Système de recherche et détection centralisé
✅ Version définitive avec ordre de priorité corrigé pour éviter les conflits
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
# DOMAINES - Mots-clés avec poids (utilisés par le scoring)
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
            'application', 'réseau', 'network', 'développeur', 'accès internet',
            'wifi', 'système d\'information', 'ogpnr', 'ogpnrf',
        ],
        'faibles': ['tech', 'digital', 'data'],
    },
    'Ingénierie & Construction': {
        'forts': [
            'construction', 'bâtiment', 'travaux publics', 'infrastructure',
            'route', 'pont', 'autoroute', 'génie civil', 'architecture',
            'urbanisme', 'béton', 'ciment', 'immobilier', 'BTP', 'chantier',
            'réhabilitation', 'génie rural', 'engineering',
            'civil works', 'travaux de construction', 'travaux de cloisonnement',
            'travaux de réhabilitation', 'cloisonnement', 'centrale solaire', 'solaire', 'énergie'
        ],
        'faibles': ['engineering', 'building', 'public works', 'travaux'],
    },
    'Santé & Médical': {
        'forts': [
            'santé', 'médical', 'hôpital', 'clinique', 'pharmacie',
            'pharmaceutique', 'médicament', 'vaccin', 'patient', 'soins',
            'médecine', 'urgence', 'laboratoire', 'health', 'healthcare',
            'SRAJ', 'kits de santé', 'matériel médical', 'infirmier',
            'centre hospitalier',
        ],
        'faibles': ['OMS', 'WHO', 'UNICEF'],
    },
    'Éducation & Formation': {
        'forts': [
            'éducation', 'formation', 'école', 'université', 'enseignement',
            'apprentissage', 'pédagogie', 'étudiant', 'curriculum',
            'training', 'school', 'university', 'teacher', 'learning',
            'vocational skills', 'skills training', 'formation professionnelle',
            'workshop', 'seminar', 'capacity building',
        ],
        'faibles': ['UNESCO', 'pedagogy'],
    },
    'Environnement & Climat': {
        'forts': [
            'environnement', 'écologie', 'climat', 'biodiversité',
            'développement durable', 'renouvelable', 'énergie', 'solaire',
            'éolien', 'recyclage', 'vert', 'environment', 'climate',
            'energy', 'renewable', 'sustainable', 'green',
            'changement climatique', 'climate smart',
        ],
        'faibles': ['recycling', 'green'],
    },
    'Finance & Comptabilité': {
        'forts': [
            'finance', 'financier', 'banque', 'investissement', 'comptabilité',
            'audit', 'fiscal', 'budget', 'trésorerie', 'microfinance',
            'crédit', 'assurance', 'financial', 'accounting',
            'verification', 'vérification', 'spot checks', 'spot check',
            'contrôle', 'paiement', 'facture', 'comptable', 'shari\'ah',
        ],
        'faibles': ['treasury', 'credit', 'savings'],
    },
    'Management & Administration': {
        'forts': [
            'administration', 'management', 'gestion', 'gouvernance',
            'stratégie', 'planning', 'coordination', 'project management',
            'programme', 'policy', 'mobilisation des ressources',
            'expertise', 'renforcement des capacités', 'portfolio management',
        ],
        'faibles': ['governance', 'strategy'],
    },
    'Transport & Logistique': {
        'forts': [
            'transport', 'logistique', 'mobilité', 'véhicule', 'motocyclette',
            'livraison', 'camion', 'bus', 'car', 'fret', 'logistics',
            'delivery', 'vehicle', 'motorcycle', 'automobile',
            'supply chain', 'carburant', 'fuel', 'combustible', 'essence',
            'diesel', 'station-service', 'carte carburant',
        ],
        'faibles': ['transportation', 'railway'],
    },
    'Agriculture & Alimentation': {
        'forts': [
            'agriculture', 'agronomie', 'élevage', 'cultures', 'irrigation',
            'semence', 'engrais', 'récolte', 'production agricole',
            'sécurité alimentaire', 'rural', 'paysan', 'agroalimentaire',
            'farming', 'livestock', 'food security', 'agricultural',
            'value chain', 'agribusiness', 'alimentation', 'nourriture',
            'pêche', 'fishery', 'fishing', 'blue economy', 'économie bleue',
            'aquaculture',
        ],
        'faibles': ['agricultural', 'agronomy', 'crops', 'seed'],
    },
    'Eau & Assainissement': {
        'forts': [
            'eau potable', 'drinking water', 'water supply',
            'assainissement', 'sanitation', 'WASH', 'wash',
            'hydraulique', 'hydrologie', 'traitement des eaux',
            'forage', 'borehole', 'pompage', 'pumping',
            'infrastructure hydraulique', 'hydraulic infrastructure',
            'adduction d\'eau', 'water distribution', 'système d\'adduction'
        ],
        'faibles': ['hydraulic', 'hydrology'],
    },
    'Communication & Médias': {
        'forts': [
            'communication', 'média', 'information publique', 'journalisme',
            'relations publiques', 'marketing', 'social media', 'vidéo',
            'documentaire', 'publicité', 'journal', 'radio', 'tv', 'presse',
            'audiovisuel', 'media', 'video', 'documentary', 'photo',
        ],
        'faibles': ['public information', 'public relations'],
    },
    'Juridique & Droit': {
        'forts': [
            'juridique', 'droit', 'loi', 'réglementation', 'légal',
            'contrat', 'avocat', 'justice', 'contentieux', 'legal',
            'law', 'contract', 'regulatory', 'compliance',
        ],
        'faibles': ['droit', 'loi'],
    },
    'Ressources Humaines': {
        'forts': [
            'ressources humaines', 'rh', 'personnel', 'staff', 'employé',
            'carrière', 'talent', 'human resources', 'hr',
        ],
        'faibles': [],
    },
    'Sécurité & Protection': {
        'forts': [
            'sécurité', 'protection', 'défense', 'armée', 'militaire',
            'garde', 'sûreté', 'police', 'security', 'protection',
            'safety', 'military', 'surveillance', 'vigile',
        ],
        'faibles': [],
    },
    'Social & Égalité': {
        'forts': [
            'social', 'égalité', 'femme', 'jeune', 'égalité des genres',
            'pauvreté', 'humanitaire', 'inclusion', 'solidarité',
            'social protection', 'women', 'gender', 'youth', 'empowerment',
            'vulnerable', 'minority', 'un women', 'social gap',
            'inclusion sociale', 'protection sociale',
        ],
        'faibles': [],
    },
    'Biens & Équipements': {
        'forts': [
            'meuble', 'furniture', 'mobilier',
            'équipement de bureau', 'office equipment',
            'fourniture de bureau', 'office supply',
            'matériel de bureau', 'bureau equipment',
            'imprimante', 'printer',
            'consommables', 'fournitures de bureau',
        ],
        'faibles': ['equipment', 'supplies', 'goods'],
    },
    'Services & Conseil': {
        'forts': [
            'consultant', 'consultancy', 'consulting',
            'expertise', 'évaluation', 'evaluation', 'assessment',
            'assistance technique', 'technical assistance',
            'recrutement d\'un consultant', 'recrutement d\'un bureau', 'recrutement d\'un cabinet',
        ],
        'faibles': ['advisory', 'support', 'étude', 'study', 'bureau d\'études', 'bureau d\'etudes', 'cabinet de conseil', 'audit', 'enquête', 'survey', 'research', 'investigation', 'mission'],
    },
}

# =============================================================================
# DÉTECTION DE DOMAINE - Système de priorité corrigé
# =============================================================================
def detecter_domaine(titre, description=""):
    """
    ✅ VERSION ULTRA-STRICTE : Détection par mots-clés prioritaires
    Les secteurs physiques spécifiques sont vérifiés AVANT les termes génériques.
    """
    if not titre:
        return 'Autres'
    
    # Combiner titre et description en minuscules
    texte = (titre + " " + (description or "")).lower()
    titre_lower = titre.lower()
    
    # ========================================================================
    # 1. DÉTECTIONS SECTORIELLES SPÉCIFIQUES (Priorité absolue)
    # ========================================================================
    
    # ✅ IT & Digital (Inclut maintenant l'espagnol)
    if any(mot in titre_lower for mot in [
        'matériel informatique', 'materiel informatique', 'équipement informatique',
        'ordinateur', 'laptop', 'logiciel', 'software', 'application',
        'accès internet', 'internet access', 'wifi',
        'système d\'information', 'plateforme digitale', 'cybersécurité',
        'site web', 'website', 'digital platform', 'data integration',
        'analytical capacity', 'capacité analytique', 'plataforma', 'plataforma digital', 
        'integración de datos', 'datos', 'capacidades analíticas', 'capacidades operativas', 
        'sistema de información', 'desarrollo de software'
    ]):
        return 'IT & Digital'

    # ✅ Santé & Médical
    if any(mot in titre_lower for mot in [
        'matériel médical', 'medical equipment', 'santé', 'health', 'hôpital', 'hospital',
        'clinique', 'clinic', 'pharmacie', 'pharmacy', 'pharmaceutique', 'pharmaceutical',
        'médicament', 'drug', 'vaccin', 'vaccine', 'patient', 'soins', 'care',
        'médecine', 'medicine', 'urgence', 'emergency', 'laboratoire', 'laboratory',
        'ipas', 'sraj', 'kits de santé', 'health kits', 'centre hospitalier'
    ]):
        return 'Santé & Médical'

    # ✅ Eau & Assainissement (⬆️ VÉRIFIÉ AVANT "Services & Conseil" pour capturer "étude d'adduction d'eau")
    if any(mot in titre_lower for mot in [
        'eau potable', 'drinking water', 'assainissement', 'sanitation', 'wash',
        'hydraulique', 'hydraulic', 'forage', 'borehole', 'traitement des eaux',
        'water treatment', 'adduction d\'eau', 'water supply', 'système d\'adduction'
    ]):
        return 'Eau & Assainissement'

    # ✅ Ingénierie & Construction (⬆️ Ajout de l'énergie/solaire)
    if any(mot in titre_lower for mot in [
        'travaux', 'works', 'construction', 'building', 'bâtiment', 'infrastructure',
        'route', 'road', 'pont', 'bridge', 'génie civil', 'civil engineering',
        'architecture', 'réhabilitation', 'rehabilitation', 'cloisonnement',
        'maçonnerie', 'masonry', 'chantier', 'site', 'centrale solaire', 'solaire', 'énergie'
    ]):
        return 'Ingénierie & Construction'

    # ✅ Agriculture & Alimentation
    if any(mot in titre_lower for mot in [
        'agriculture', 'agricultural', 'agronomie', 'agronomy', 'élevage', 'livestock',
        'cultures', 'crops', 'irrigation', 'semence', 'seed', 'engrais', 'fertilizer',
        'récolte', 'harvest', 'pêche', 'fishery', 'fishing', 'food security',
        'sécurité alimentaire', 'vivres', 'foodstuff', 'agricole', 'produits agricoles'
    ]):
        return 'Agriculture & Alimentation'

    # ✅ Éducation & Formation
    if any(mot in titre_lower for mot in [
        'formation', 'training', 'éducation', 'education', 'école', 'school',
        'université', 'university', 'enseignement', 'teaching', 'apprentissage',
        'learning', 'pédagogie', 'pedagogy', 'curriculum', 'capacity building'
    ]):
        return 'Éducation & Formation'

    # ✅ Transport & Logistique
    if any(mot in titre_lower for mot in [
        'carburant', 'fuel', 'combustible', 'essence', 'diesel', 'carte carburant',
        'transport', 'logistique', 'logistics', 'véhicule', 'vehicle', 'motocyclette',
        'camion', 'truck', 'bus', 'fret', 'cargo', 'livraison', 'delivery',
        'supply chain', 'chaîne d\'approvisionnement'
    ]):
        return 'Transport & Logistique'

    # ✅ Environnement & Climat
    if any(mot in titre_lower for mot in [
        'environnement', 'environment', 'climat', 'climate', 'biodiversité',
        'biodiversity', 'développement durable', 'sustainable development',
        'renouvelable', 'renewable', 'énergie', 'energy', 'solaire', 'solar',
        'éolien', 'wind', 'recyclage', 'recycling', 'vert', 'green'
    ]):
        return 'Environnement & Climat'

    # ========================================================================
    # 2. DÉTECTIONS FONCTIONNELLES (Vérifiées après les secteurs physiques)
    # ========================================================================

    # ✅ Finance & Comptabilité
    if any(mot in titre_lower for mot in [
        'finance', 'financial', 'banque', 'bank', 'investissement', 'investment',
        'comptabilité', 'accounting', 'audit financier', 'financial audit',
        'budget', 'trésorerie', 'treasury', 'microfinance', 'crédit', 'credit',
        'assurance', 'insurance', 'vérification', 'verification', 'spot check'
    ]):
        return 'Finance & Comptabilité'

    # ✅ Juridique & Droit
    if any(mot in titre_lower for mot in [
        'juridique', 'legal', 'droit', 'law', 'justice', 'droits humains',
        'human rights', 'anti-corruption', 'contrat', 'contract', 'réglementation'
    ]):
        return 'Juridique & Droit'

    # ✅ Sécurité & Protection
    if any(mot in titre_lower for mot in [
        'sécurité', 'security', 'protection', 'safety', 'urgence', 'emergency',
        'catastrophe', 'disaster', 'risque', 'risk', 'défense', 'defense',
        'militaire', 'military', 'surveillance'
    ]):
        return 'Sécurité & Protection'

    # ✅ Social & Égalité
    if any(mot in titre_lower for mot in [
        'social', 'genre', 'gender', 'égalité', 'equality', 'femmes', 'women',
        'jeunesse', 'youth', 'enfant', 'child', 'handicap', 'disability',
        'pauvreté', 'poverty', 'inclusion', 'protection sociale', 'social protection'
    ]):
        return 'Social & Égalité'

    # ✅ Communication & Médias
    if any(mot in titre_lower for mot in [
        'communication', 'média', 'media', 'audiovisuel', 'audio-visual',
        'vidéo', 'video', 'documentaire', 'documentary', 'radio', 'tv', 'presse',
        'press', 'marketing', 'relations publiques', 'public relations',
        'équipements audio-visuels', 'audio visual equipment'
    ]):
        return 'Communication & Médias'

    # ✅ Management & Administration
    if any(mot in titre_lower for mot in [
        'management', 'gestion', 'administration', 'administrative', 'gouvernance',
        'governance', 'stratégie', 'strategy', 'planning', 'coordination',
        'project management', 'programme', 'policy', 'portfolio management'
    ]):
        return 'Management & Administration'

    # ✅ Ressources Humaines
    if any(mot in titre_lower for mot in [
        'ressources humaines', 'human resources', 'hr', 'recrutement', 'recruitment',
        'personnel', 'staff', 'carrière', 'career'
    ]):
        return 'Ressources Humaines'

    # ✅ Biens & Équipements
    if any(mot in titre_lower for mot in [
        'meuble', 'meubles', 'furniture', 'mobilier', 'mobilier de bureau',
        'siège', 'chaise', 'armoire', 'étagère', 'fourniture de bureau'
    ]):
        return 'Biens & Équipements'

    # ✅ Services & Conseil (⬇️ VÉRIFIÉ EN DERNIER pour ne pas voler "étude d'eau" ou "consulting énergie")
    if any(mot in titre_lower for mot in [
        'audit', 'consultant', 'consultancy', 'consulting', 'cabinet', 'firm',
        'étude', 'study', 'expertise', 'évaluation', 'evaluation', 'assessment',
        'assistance technique', 'technical assistance', 'recrutement d\'un cabinet',
        'recrutement d\'une agence', 'recrutement d\'un bureau', 'recruitment of a firm',
        'bureau d\'études', 'bureau d\'etudes', 'design office'
    ]):
        return 'Services & Conseil'

    # ========================================================================
    # 3. FALLBACK GÉNÉRIQUE
    # ========================================================================
    if any(mot in titre_lower for mot in [
        'fourniture', 'acquisition', 'achat', 'purchase', 'supply', 'équipement',
        'equipment', 'matériel', 'material', 'produits', 'products', 'goods',
        'biens', 'marché', 'contract'
    ]):
        # Essayer de distinguer le type de fourniture en dernier recours
        if any(mot in titre_lower for mot in ['informatique', 'ordinateur', 'logiciel', 'digital', 'it']):
            return 'IT & Digital'
        if any(mot in titre_lower for mot in ['carburant', 'véhicule', 'transport', 'logistique']):
            return 'Transport & Logistique'
        if any(mot in titre_lower for mot in ['meuble', 'mobilier', 'bureau']):
            return 'Biens & Équipements'
        if any(mot in titre_lower for mot in ['audio-visuel', 'audiovisuel', 'vidéo']):
            return 'Communication & Médias'
        if any(mot in titre_lower for mot in ['médical', 'santé', 'pharmacie']):
            return 'Santé & Médical'
            
    # ✅ CORRECTION MAJEURE : Si rien ne correspond, retourner 'Autres' au lieu de forcer 'Biens & Équipements'
    return 'Autres'


# =============================================================================
# PAYS - Codes ISO et noms (Mis à jour Afrique de l'Ouest et de l'Est)
# =============================================================================
COUNTRIES = {
    # Afrique de l'Ouest
    'BF': ['Burkina Faso', 'Burkina', 'BF'],
    'BJ': ['Bénin', 'Benin', 'BJ'],
    'CV': ['Cap-Vert', 'Cape Verde', 'CV'],
    'CI': ['Côte d\'Ivoire', 'Cote d\'Ivoire', 'Ivory Coast', 'CI'],
    'GM': ['Gambie', 'Gambia', 'GM'],
    'GH': ['Ghana', 'GH'],
    'GN': ['Guinée', 'Guinea', 'GN'],
    'GW': ['Guinée-Bissau', 'Guinea-Bissau', 'GW'],
    'LR': ['Libéria', 'Liberia', 'LR'],
    'ML': ['Mali', 'ML'],
    'MR': ['Mauritanie', 'Mauritania', 'MR'],
    'NE': ['Niger', 'NE'],
    'NG': ['Nigeria', 'NG'],
    'SN': ['Sénégal', 'Senegal', 'SN'],
    'SL': ['Sierra Leone', 'SL'],
    'TG': ['Togo', 'TG'],
    
    # Afrique de l'Est
    'BI': ['Burundi', 'BI'],
    'DJ': ['Djibouti', 'DJ'],
    'ER': ['Érythrée', 'Eritrea', 'ER'],
    'ET': ['Éthiopie', 'Ethiopia', 'ET'],
    'KE': ['Kenya', 'KE'],
    'RW': ['Rwanda', 'RW'],
    'SC': ['Seychelles', 'SC'],
    'SO': ['Somalie', 'Somalia', 'SO'],
    'SD': ['Soudan', 'Sudan', 'SD'],
    'SS': ['Soudan du Sud', 'South Sudan', 'SS'],
    'TZ': ['Tanzanie', 'Tanzania', 'TZ'],
    'UG': ['Ouganda', 'Uganda', 'UG'],

    # Autres pays africains majeurs
    'DZ': ['Algérie', 'Algeria', 'DZ'],
    'AO': ['Angola', 'AO'],
    'CM': ['Cameroun', 'Cameroon', 'CM'],
    'CF': ['Centrafrique', 'Central African Republic', 'CF'],
    'TD': ['Tchad', 'Chad', 'TD'],
    'KM': ['Comores', 'Comoros', 'KM'],
    'CG': ['Congo', 'CG'],
    'CD': ['RD Congo', 'Congo-Kinshasa', 'CD', 'RDC'],
    'GA': ['Gabon', 'GA'],
    'GQ': ['Guinée équatoriale', 'Equatorial Guinea', 'GQ'],
    'LS': ['Lesotho', 'LS'],
    'MG': ['Madagascar', 'MG'],
    'MW': ['Malawi', 'MW'],
    'MU': ['Maurice', 'Mauritius', 'MU'],
    'MA': ['Maroc', 'Morocco', 'MA'],
    'MZ': ['Mozambique', 'MZ'],
    'NA': ['Namibie', 'Namibia', 'NA'],
    'ZA': ['Afrique du Sud', 'South Africa', 'ZA'],
    'SZ': ['Eswatini', 'Swaziland', 'SZ'],
    'ZM': ['Zambie', 'Zambia', 'ZM'],
    'ZW': ['Zimbabwe', 'ZW'],
    'TN': ['Tunisie', 'Tunisia', 'TN'],
    'EG': ['Égypte', 'Egypt', 'EG'],
    'LY': ['Libye', 'Libya', 'LY'],

    # Pays hors Afrique
    'AR': ['Argentine', 'Argentina', 'AR'],
    'ID': ['Indonésie', 'Indonesia', 'ID'],
    'BA': ['Bosnie-Herzégovine', 'Bosnia', 'BA'],
    'US': ['États-Unis', 'United States', 'USA', 'US'],
    'GB': ['Royaume-Uni', 'United Kingdom', 'UK', 'GB'],
    'FR': ['France', 'FR'],
    'DE': ['Allemagne', 'Germany', 'DE'],
    'BE': ['Belgique', 'Belgium', 'BE'],
    'IT': ['Italie', 'Italy', 'IT'],
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
# VALIDATION APPEL D'OFFRES
# =============================================================================
def est_appel_offres(titre: str, description: str = "") -> bool:
    """
    ✅ Vérifie si c'est un VRAI appel d'offres
    ❌ Rejette les offres d'emploi
    """
    if not titre:
        return False

    texte = (titre + ' ' + description).lower()

    # ========================================================================
    # ❌ EXCLUSIONS FORTES (offres d'emploi)
    # ========================================================================
    exclusions_emploi = [
        'job offer', 'job opening', 'job posting', 'offre d\'emploi',
        'apply now', 'postuler maintenant', 'postulez maintenant',
        'salary', 'salaire', 'rémunération', 'remuneration',
        'full-time', 'temps plein', 'full time',
        'part-time', 'temps partiel', 'part time',
        'send to friend', 'save share', 'view more',
        'benefits package', 'annual leave', 'health insurance',
        'cv required', 'cv requis', 'resume required',
        'cover letter', 'lettre de motivation',
        'work permit', 'permis de travail',
        'software engineer', 'ingénieur logiciel',
        'developer', 'développeur', 'programmer',
        'procurement associate', 'procurement officer',
    ]

    for mot in exclusions_emploi:
        if mot in texte:
            return False

    # ========================================================================
    # ✅ CONFIRMATIONS FORTES (appels d'offres)
    # ========================================================================
    confirmations_fortes = [
        'rfq', 'rfp', 'eoi', 'iti', 'itt', 'sdp', 'dao',
        'demande de cotation', 'demande de proposition',
        'appel d\'offres', 'appel d\'offre', 'avis d\'appel d\'offres',
        'avis à manifestation', 'manifestation d\'intérêt',
        'demande de prix', 'invitation à soumissionner',
        'bureau d\'études', 'bureau d\'etudes',
        'cotation pour', 'cotation n°', 'cotation n-',
        'request for quotation', 'request for proposal',
        'expression of interest', 'invitation to bid',
        'procurement notice', 'tender notice',
        'marché public',
    ]

    for mot in confirmations_fortes:
        if mot in texte:
            return True

    # ========================================================================
    # 🎯 CAS AMBIGUS - "Recrutement"
    # ========================================================================
    if 'recrutement' in texte or 'recruitment' in texte:
        mots_pro_appel_offres = [
            'consultant', 'consultants', 'consultancy',
            'cabinet', 'firm', 'firme', 'entreprise',
            'bureau', 'office', 'société', 'company',
            'évaluation', 'evaluation', 'audit',
            'étude', 'study', 'research',
            'enquête', 'survey', 'investigation',
            'formation', 'training', 'capacity building',
            'assistance technique', 'technical assistance',
            'mission', 'expertise',
        ]

        for mot in mots_pro_appel_offres:
            if mot in texte:
                return True

        # Recrutement sans contexte pro = offre d'emploi
        return False

    # ========================================================================
    # ✅ AUTRES INDICATEURS D'APPELS D'OFFRES
    # ========================================================================
    autres_indicateurs = [
        'travaux de', 'construction de', 'réhabilitation de',
        'fourniture de', 'acquisition de', 'achat de',
        'production de', 'fabrication de',
        'étude de', 'évaluation de', 'audit de',
        'consulting', 'consultancy', 'consulting services',
        'implementation of', 'design of', 'development of',
        'supply of', 'delivery of', 'installation of',
        'procurement of', 'acquisition of',
    ]

    for mot in autres_indicateurs:
        if mot in texte:
            return True

    # Par défaut : rejeter
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