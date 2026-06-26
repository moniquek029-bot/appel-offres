# offres/utils/domain_keywords.py

DOMAIN_KEYWORDS = {
    'Santé': [
        'santé', 'sante', 'health', 'medical', 'healthcare', 'medicine',
        'hôpital', 'hospital', 'clinique', 'clinic', 'soins', 'care',
        'médecin', 'doctor', 'pharmacie', 'pharmacy', 'maladie', 'disease',
        'épidémie', 'epidemic', 'pandémie', 'pandemic', 'vaccin', 'vaccine',
        'OMS', 'WHO', 'UNICEF', 'MSF', 'Médecins Sans Frontières',
        'nutrition', 'maternel', 'maternal', 'infant', 'pédiatrie', 'pediatric',
        'santé publique', 'public health', 'hôpital', 'hospital'
    ],
    
    'Informatique': [
        'informatique', 'IT', 'information technology', 'technologie', 'technology',
        'computer', 'software', 'logiciel', 'hardware', 'matériel',
        'développement', 'development', 'programmation', 'programming',
        'numérique', 'digital', 'data', 'données', 'intelligence artificielle',
        'AI', 'artificial intelligence', 'machine learning', 'cybersécurité',
        'cybersecurity', 'cloud', 'réseau', 'network', 'internet', 'web',
        'développeur', 'developer', 'système', 'system', 'base de données',
        'database', 'blockchain', 'IoT', 'internet des objets'
    ],
    
    'BTP': [
        'BTP', 'construction', 'building', 'travaux publics', 'public works',
        'infrastructure', 'génie civil', 'civil engineering', 'architecture',
        'bâtiment', 'chantier', 'site', 'béton', 'concrete',
        'route', 'road', 'highway', 'pont', 'bridge', 'tunnel',
        'urbanisme', 'urban planning', 'immobilier', 'real estate'
    ],
    
    'Éducation': [
        'éducation', 'education', 'enseignement', 'teaching', 'formation',
        'training', 'école', 'school', 'université', 'university', 'collège',
        'college', 'apprentissage', 'learning', 'pédagogie', 'pedagogy',
        'professeur', 'teacher', 'étudiant', 'student', 'curriculum',
        'alphabétisation', 'literacy', 'UNESCO'
    ],
    
    'Finance': [
        'finance', 'comptabilité', 'accounting', 'banque', 'bank', 'banking',
        'économique', 'economic', 'economy', 'économie', 'budget', 'audit',
        'investissement', 'investment', 'marché', 'market', 'bourse', 'stock',
        'assurance', 'insurance', 'fiscal', 'tax', 'monétaire', 'monetary'
    ],
    
    'Environnement': [
        'environnement', 'environment', 'écologie', 'ecology', 'écologique',
        'ecological', 'développement durable', 'sustainable development',
        'climat', 'climate', 'changement climatique', 'climate change',
        'green', 'vert', 'biodiversité', 'biodiversity', 'pollution',
        'recyclage', 'recycling', 'énergie renouvelable', 'renewable energy'
    ],
    
    'Agriculture': [
        'agriculture', 'farming', 'agricole', 'agricultural', 'agroalimentaire',
        'food', 'alimentation', 'élevage', 'livestock', 'cultures', 'crops',
        'pêche', 'fishing', 'aquaculture', 'irrigation', 'semence', 'seed',
        'sécurité alimentaire', 'food security', 'rural', 'agriculteur', 'farmer'
    ],
    
    'Transport': [
        'transport', 'transportation', 'logistique', 'logistics', 'shipping',
        'expédition', 'delivery', 'livraison', 'supply chain',
        'aviation', 'aérien', 'maritime', 'ferroviaire', 'railway',
        'routier', 'road', 'cargo', 'fret', 'freight'
    ],
    
    'Énergie': [
        'énergie', 'energy', 'électricité', 'electricity', 'power',
        'pétrole', 'oil', 'gas', 'gaz', 'charbon', 'coal', 'nucléaire', 'nuclear',
        'solaire', 'solar', 'éolien', 'wind', 'hydraulique', 'hydro',
        'biomasse', 'biomass', 'géothermie', 'geothermal'
    ],
    
    'Télécommunications': [
        'télécommunications', 'telecommunications', 'telecom', 'communication',
        'réseau', 'network', '5G', '4G', '3G', 'mobile', 'téléphonie',
        'satellite', 'fibre optique', 'fiber optic', 'bande passante', 'bandwidth'
    ],
    
    'Fourniture': [
        'fourniture', 'supply', 'équipement', 'equipment', 'matériel',
        'approvisionnement', 'procurement', 'achat', 'purchase', 'marché public',
        'public tender', 'appel d\'offres', 'tender', 'bid', 'fournisseur', 'supplier'
    ]
}

def get_domain_keywords(domain):
    """Retourne tous les mots-clés associés à un domaine (FR + EN)"""
    if not domain:
        return []
    
    domain_normalized = domain.strip()
    
    # Recherche directe
    if domain_normalized in DOMAIN_KEYWORDS:
        return DOMAIN_KEYWORDS[domain_normalized]
    
    # Recherche insensible à la casse
    for key, values in DOMAIN_KEYWORDS.items():
        if key.lower() == domain_normalized.lower():
            return values
    
    # Si le domaine n'est pas trouvé, retourner le domaine lui-même
    return [domain_normalized]