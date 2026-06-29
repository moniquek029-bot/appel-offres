# offres/scraping/country_detector.py
"""
Détecteur de pays intelligent pour le scraping
"""
import re
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Base de données des pays (nom + code ISO + variantes)
PAYS_DATA = {
    'BF': {'noms': ['burkina faso', 'burkina', 'bf'], 'villes': ['ouagadougou', 'ouaga', 'bobo-dioulasso']},
    'CI': {'noms': ['côte d\'ivoire', 'cote d\'ivoire', 'ivory coast', 'ci'], 'villes': ['abidjan', 'yamoussoukro']},
    'SN': {'noms': ['sénégal', 'senegal', 'sn'], 'villes': ['dakar', 'thiès']},
    'ML': {'noms': ['mali', 'ml'], 'villes': ['bamako']},
    'NE': {'noms': ['niger', 'ne'], 'villes': ['niamey']},
    'TG': {'noms': ['togo', 'tg'], 'villes': ['lomé', 'lome']},
    'BJ': {'noms': ['bénin', 'benin', 'bj'], 'villes': ['cotonou']},
    'GH': {'noms': ['ghana', 'gh'], 'villes': ['accra']},
    'NG': {'noms': ['nigeria', 'ng'], 'villes': ['abuja', 'lagos']},
    'GN': {'noms': ['guinée', 'guinea', 'gn'], 'villes': ['conakry']},
    'CM': {'noms': ['cameroun', 'cameroon', 'cm'], 'villes': ['yaoundé', 'douala']},
    'GA': {'noms': ['gabon', 'ga'], 'villes': ['libreville']},
    'CD': {'noms': ['rdc', 'république démocratique du congo', 'congo-kinshasa', 'cd'], 'villes': ['kinshasa']},
    'CG': {'noms': ['congo', 'congo-brazzaville', 'cg'], 'villes': ['brazzaville']},
    'TD': {'noms': ['tchad', 'chad', 'td'], 'villes': ['n\'djamena']},
    'CF': {'noms': ['république centrafricaine', 'centrafrique', 'cf'], 'villes': ['bangui']},
    'RW': {'noms': ['rwanda', 'rw'], 'villes': ['kigali']},
    'ET': {'noms': ['éthiopie', 'ethiopia', 'et'], 'villes': ['addis-abeba']},
    'KE': {'noms': ['kenya', 'ke'], 'villes': ['nairobi']},
    'TZ': {'noms': ['tanzanie', 'tanzania', 'tz'], 'villes': ['dar es salaam']},
    'UG': {'noms': ['ouganda', 'uganda', 'ug'], 'villes': ['kampala']},
    'MA': {'noms': ['maroc', 'morocco', 'ma'], 'villes': ['rabat', 'casablanca']},
    'DZ': {'noms': ['algérie', 'algeria', 'dz'], 'villes': ['alger']},
    'TN': {'noms': ['tunisie', 'tunisia', 'tn'], 'villes': ['tunis']},
    'EG': {'noms': ['égypte', 'egypt', 'eg'], 'villes': ['le caire', 'cairo']},
    'ZA': {'noms': ['afrique du sud', 'south africa', 'za'], 'villes': ['pretoria']},
    'AR': {'noms': ['argentina', 'argentine', 'ar'], 'villes': ['buenos aires']},
    'ID': {'noms': ['indonesia', 'indonésie', 'id'], 'villes': ['jakarta']},
    'BA': {'noms': ['bosnia and herzegovina', 'bosnie-herzégovine', 'ba'], 'villes': ['sarajevo']},
    'US': {'noms': ['united states', 'usa', 'us'], 'villes': ['washington']},
    'GB': {'noms': ['united kingdom', 'uk', 'great britain', 'gb'], 'villes': ['london']},
    'FR': {'noms': ['france', 'fr'], 'villes': ['paris']},
    'DE': {'noms': ['germany', 'allemagne', 'de'], 'villes': ['berlin']},
    'GLOBAL': {'noms': ['global', 'international', 'mondial', 'worldwide'], 'villes': []},
}
    
    # Dans country_detector.py, ajoutez cette logique au début de detecter_pays_smart

def detecter_pays_smart(texte: str, url: str = None, pays_defaut: str = 'BF') -> str:
    """Détecte le pays de manière intelligente"""
    if not texte:
        return pays_defaut
    
    # ✅ NOUVEAU : Détection par URL en priorité
    if url:
        url_lower = url.lower()
        
        # UNFPA Burkina Faso
        if 'burkinafaso.unfpa.org' in url_lower:
            logger.info(f"🌍 Pays détecté (URL UNFPA): {url} → BF")
            return 'BF'
        
        # UNDP pays spécifiques
        if 'undp.org' in url_lower:
            # Chercher le pays dans l'URL
            if '/burkinafaso/' in url_lower or '/bf/' in url_lower:
                return 'BF'
            elif '/senegal/' in url_lower or '/sn/' in url_lower:
                return 'SN'
            elif '/mali/' in url_lower or '/ml/' in url_lower:
                return 'ML'
    
    texte_lower = texte.lower()
    
    # Chercher les noms de pays (triés par longueur décroissante)
    pays_tries = []
    for code, data in PAYS_DATA.items():
        for nom in data['noms']:
            pays_tries.append((len(nom), nom, code))
    
    pays_tries.sort(key=lambda x: x[0], reverse=True)
    
    for longueur, nom_pays, code in pays_tries:
        pattern = r'\b' + re.escape(nom_pays) + r'\b'
        if re.search(pattern, texte_lower):
            logger.info(f"🌍 Pays détecté : '{nom_pays}' → {code}")
            return code
    
    # Chercher les villes
    for code, data in PAYS_DATA.items():
        for ville in data.get('villes', []):
            pattern = r'\b' + re.escape(ville) + r'\b'
            if re.search(pattern, texte_lower):
                logger.info(f"🌍 Pays détecté (ville) : '{ville}' → {code}")
                return code
    
    # Analyser l'URL
    if url:
        code_url = _detecter_pays_url(url)
        if code_url:
            logger.info(f"🌍 Pays détecté (URL) : {url} → {code_url}")
            return code_url
    
    return pays_defaut


def _detecter_pays_url(url: str) -> str:
    """Détecte le pays à partir de l'URL"""
    if not url:
        return None
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        tld_mapping = {
            '.bf': 'BF', '.ci': 'CI', '.sn': 'SN', '.ml': 'ML',
            '.ne': 'NE', '.tg': 'TG', '.bj': 'BJ', '.gh': 'GH',
            '.ng': 'NG', '.cm': 'CM', '.ga': 'GA', '.cd': 'CD',
            '.rw': 'RW', '.ke': 'KE', '.ma': 'MA', '.dz': 'DZ',
        }
        
        for tld, code in tld_mapping.items():
            if domain.endswith(tld):
                return code
    except Exception as e:
        logger.debug(f"⚠️ Erreur détection URL: {e}")
    
    return None