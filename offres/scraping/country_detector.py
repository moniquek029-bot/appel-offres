"""
Détecteur de pays intelligent
✅ VERSION FINALE : Évite les faux positifs (de, et, etc.)
✅ Retourne None si aucun pays détecté (pas de valeur par défaut)
"""
import re
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# =============================================================================
# MAPPING URL → PAYS (le plus fiable)
# =============================================================================
# MAPPING URL → PAYS (le plus fiable)
# =============================================================================
URL_TO_PAYS = {
    'jaoguinee.com': 'GN',
    'lesannonces224.com': 'SN',  # ✅ 224 = Sénégal
    'cdiscussion.com': 'BJ',
    'psimali.ml': 'ML',
    'sonabel.bf': 'BF',
    'agetib.bf': 'BF',
    'uemoa.int': 'BF',
    'abfburkina.org': 'BF',
    'burkinafaso.unfpa.org': 'BF',
    'intercontactservices.com': 'BI',  # ✅ Bujumbura = Burundi
    'procurement-notices.undp.org': None,  # Pays détecté dans le contenu
}

# =============================================================================
# BASE DE DONNÉES DES PAYS
# ✅ Noms COMPLETS uniquement (>= 5 caractères)
# =============================================================================
PAYS_DATA = {
    'BF': {
        'noms': ['burkina faso', 'burkina'],
        'villes': ['ouagadougou', 'ouaga', 'bobo-dioulasso'],
        'organismes': ['sonabel', 'sonabhy', 'onetel', 'coris bank', 'agetib', 'abf burkina'],
    },
    'ML': {
        'noms': ['mali'],
        'villes': ['bamako'],
        'organismes': ['psimali', 'projet sikan', 'miracle mnch'],
    },
    'NE': {
        'noms': ['niger'],
        'villes': ['niamey'],
        'organismes': [],
    },
    'SN': {
        'noms': ['sénégal', 'senegal'],
        'villes': ['dakar', 'thiès'],
        'organismes': ['lesannonces224'],  # ✅ 224 = indicatif Sénégal
    },
    'CI': {
        'noms': ['côte d\'ivoire', 'cote d\'ivoire', 'ivory coast'],
        'villes': ['abidjan', 'yamoussoukro'],
        'organismes': [],
    },
    'BJ': {
        'noms': ['bénin', 'benin'],
        'villes': ['cotonou'],
        'organismes': ['counterpart international'],
    },
    'TG': {
        'noms': ['togo'],
        'villes': ['lomé', 'lome'],
        'organismes': [],
    },
    'GN': {
        'noms': ['guinée', 'guinea'],
        'villes': ['conakry'],
        'organismes': ['chalco guinea', 'chalco', 'ogpnrf'],  # ✅ Retiré jaoguinee
    },
    'CM': {
        'noms': ['cameroun', 'cameroon'],
        'villes': ['yaoundé', 'douala'],
        'organismes': [],
    },
    'GA': {
        'noms': ['gabon'],
        'villes': ['libreville'],
        'organismes': [],
    },
    'CD': {
        'noms': ['rd congo', 'congo-kinshasa', 'congo démocratique'],
        'villes': ['kinshasa'],
        'organismes': [],  # ✅ Retiré intercontactservices
    },
    'BI': {
        'noms': ['burundi'],
        'villes': ['bujumbura'],
        'organismes': ['icap bureau'],
    },
    'CG': {
        'noms': ['congo-brazzaville', 'congo brazzaville'],
        'villes': ['brazzaville'],
        'organismes': [],
    },
    'TD': {
        'noms': ['tchad', 'chad'],
        'villes': ['n\'djamena'],
        'organismes': [],
    },
    'CF': {
        'noms': ['centrafrique', 'république centrafricaine'],
        'villes': ['bangui'],
        'organismes': [],
    },
    'RW': {
        'noms': ['rwanda'],
        'villes': ['kigali'],
        'organismes': [],
    },
    'ET': {
        'noms': ['éthiopie', 'ethiopia'],
        'villes': ['addis-abeba'],
        'organismes': [],
    },
    'KE': {
        'noms': ['kenya'],
        'villes': ['nairobi'],
        'organismes': [],
    },
    'UG': {
        'noms': ['ouganda', 'uganda'],
        'villes': ['kampala'],
        'organismes': [],
    },
    'MA': {
        'noms': ['maroc', 'morocco'],
        'villes': ['rabat', 'casablanca'],
        'organismes': [],
    },
    'DZ': {
        'noms': ['algérie', 'algeria'],
        'villes': ['alger'],
        'organismes': [],
    },
    'TN': {
        'noms': ['tunisie', 'tunisia'],
        'villes': ['tunis'],
        'organismes': [],
    },
    'EG': {
        'noms': ['égypte', 'egypt'],
        'villes': ['le caire', 'cairo'],
        'organismes': [],
    },
    'ZA': {
        'noms': ['afrique du sud', 'south africa'],
        'villes': ['pretoria', 'johannesburg'],
        'organismes': [],
    },
    'AR': {
        'noms': ['argentine', 'argentina', 'buenos aires'],
        'villes': ['buenos aires'],
        'organismes': ['arba', 'provincia de buenos aires'],
    },
    'ID': {
        'noms': ['indonésie', 'indonesia'],
        'villes': ['jakarta'],
        'organismes': [],
    },
    'BA': {
        'noms': ['bosnie-herzégovine', 'bosnia'],
        'villes': ['sarajevo'],
        'organismes': [],
    },
    'US': {
        'noms': ['états-unis', 'united states', 'usa'],
        'villes': ['washington'],
        'organismes': [],
    },
    'GB': {
        'noms': ['royaume-uni', 'united kingdom', 'great britain'],
        'villes': ['london', 'londres'],
        'organismes': [],
    },
    'FR': {
        'noms': ['france'],
        'villes': ['paris'],
        'organismes': [],
    },
    'DE': {
        'noms': ['allemagne', 'germany'],  # ❌ PAS "de" !
        'villes': ['berlin'],
        'organismes': [],
    },
    'BE': {
        'noms': ['belgique', 'belgium'],
        'villes': ['bruxelles'],
        'organismes': ['enabel'],
    },
    'JO': {
        'noms': ['jordanie', 'jordan'],
        'villes': ['amman'],
        'organismes': [],
    },
    'SO': {
        'noms': ['somalie', 'somalia'],
        'villes': ['mogadiscio'],
        'organismes': [],
    },
    'NG': {
        'noms': ['nigeria'],
        'villes': ['abuja', 'lagos'],
        'organismes': [],
    },
    'GH': {
        'noms': ['ghana'],
        'villes': ['accra'],
        'organismes': [],
    },
    'GLOBAL': {
        'noms': ['international', 'global', 'mondial', 'worldwide'],
        'villes': [],
        'organismes': ['unicef', 'who', 'world bank', 'banque mondiale'],
    },
}

TLD_MAPPING = {
    '.bf': 'BF', '.ci': 'CI', '.sn': 'SN', '.ml': 'ML',
    '.ne': 'NE', '.tg': 'TG', '.bj': 'BJ', '.gh': 'GH',
    '.ng': 'NG', '.cm': 'CM', '.ga': 'GA', '.cd': 'CD',
    '.rw': 'RW', '.ke': 'KE', '.ma': 'MA', '.dz': 'DZ',
    '.gn': 'GN', '.cg': 'CG', '.tn': 'TN', '.et': 'ET',
    '.ug': 'UG', '.cf': 'CF', '.td': 'TD', '.eg': 'EG',
    '.za': 'ZA', '.ar': 'AR', '.id': 'ID', '.ba': 'BA',
    '.us': 'US', '.uk': 'GB', '.gb': 'GB', '.fr': 'FR',
    '.de': 'DE', '.be': 'BE', '.jo': 'JO', '.so': 'SO',
    '.bi': 'BI',
}


def detecter_pays_smart(texte: str, url: str = None, pays_defaut: str = None) -> str | None:
    """
    ✅ Détecte le pays - Retourne None si aucun pays trouvé
    """
    texte_lower = (texte or '').lower()
    
    # ÉTAPE 1 : MAPPING URL DIRECT
    if url:
        for domain, pays in URL_TO_PAYS.items():
            if domain in url.lower():
                logger.info(f"🌍 Pays (URL '{domain}'): → {pays}")
                return pays
    
    # ÉTAPE 2 : TLD
    if url:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            for tld, code in TLD_MAPPING.items():
                if domain.endswith(tld):
                    logger.info(f"🌍 Pays (TLD {tld}): → {code}")
                    return code
        except Exception:
            pass
    
    # ÉTAPE 3 : ORGANISMES CONNUS
    for code, data in PAYS_DATA.items():
        for org in data.get('organismes', []):
            if org in texte_lower or (url and org in url.lower()):
                logger.info(f"🌍 Pays (organisme '{org}'): → {code}")
                return code
    
    # ÉTAPE 4 : NOMS DE PAYS (longs uniquement)
    pays_tries = []
    for code, data in PAYS_DATA.items():
        for nom in data['noms']:
            if len(nom) >= 5:
                pays_tries.append((len(nom), nom, code))
    
    pays_tries.sort(key=lambda x: x[0], reverse=True)
    
    for longueur, nom_pays, code in pays_tries:
        pattern = r'\b' + re.escape(nom_pays) + r'\b'
        if re.search(pattern, texte_lower):
            logger.info(f"🌍 Pays (nom '{nom_pays}'): → {code}")
            return code
    
    # ÉTAPE 5 : VILLES
    for code, data in PAYS_DATA.items():
        for ville in data.get('villes', []):
            if len(ville) >= 4:
                pattern = r'\b' + re.escape(ville) + r'\b'
                if re.search(pattern, texte_lower):
                    logger.info(f"🌍 Pays (ville '{ville}'): → {code}")
                    return code
    
    # FALLBACK : pays_defaut ou None
    if pays_defaut:
        logger.info(f"🌍 Pays par défaut: → {pays_defaut}")
    else:
        logger.warning(f"⚠️ Aucun pays détecté")
    
    return None


def detecter_pays_undp(texte: str, url: str = None) -> str | None:
    """
    ✅ Détection spécifique pour UNDP avec analyse du contenu
    """
    if not url or 'undp.org' not in url.lower():
        return None
    
    texte_lower = (texte or '').lower()
    
    # Patterns UNDP spécifiques
    patterns_pays = [
        (r'country[:\s/]+([a-z]+)', None),  # "Country/Argentina"
        (r'office/country[:\s/]+([a-z]+)', None),
        (r'undp\s+office[:\s/]+([a-z]+)', None),
    ]
    
    for pattern, _ in patterns_pays:
        match = re.search(pattern, texte_lower)
        if match:
            pays_str = match.group(1).strip().lower()
            
            # Mapping des pays UNDP
            undp_pays = {
                'argentina': 'AR', 'argentine': 'AR',
                'burkina faso': 'BF', 'burkina': 'BF',
                'senegal': 'SN', 'sénégal': 'SN',
                'mali': 'ML',
                'niger': 'NE',
                'togo': 'TG',
                'benin': 'BJ', 'bénin': 'BJ',
                'guinea': 'GN', 'guinée': 'GN',
                'cameroon': 'CM', 'cameroun': 'CM',
                'nigeria': 'NG',
                'ghana': 'GH',
                'kenya': 'KE',
                'ethiopia': 'ET', 'éthiopie': 'ET',
                'rwanda': 'RW',
                'uganda': 'UG', 'ouganda': 'UG',
                'tanzania': 'TZ', 'tanzanie': 'TZ',
                'congo': 'CD',
                'morocco': 'MA', 'maroc': 'MA',
                'algeria': 'DZ', 'algérie': 'DZ',
                'tunisia': 'TN', 'tunisie': 'TN',
                'egypt': 'EG', 'égypte': 'EG',
                'south africa': 'ZA',
                'indonesia': 'ID', 'indonésie': 'ID',
                'france': 'FR',
                'germany': 'DE', 'allemagne': 'DE',
                'united kingdom': 'GB', 'royaume-uni': 'GB',
                'united states': 'US', 'états-unis': 'US',
            }
            
            if pays_str in undp_pays:
                logger.info(f"🌍 UNDP Pays détecté: {pays_str} → {undp_pays[pays_str]}")
                return undp_pays[pays_str]
    
    return None