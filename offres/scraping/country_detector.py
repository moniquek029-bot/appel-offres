# offres/scraping/country_detector.py
"""
Détecteur de pays intelligent pour le scraping
Détecte le pays à partir du texte, de l'URL et des métadonnées
"""

import re
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# =============================================================================
# BASE DE DONNÉES DES PAYS (nom + code ISO + variantes)
# =============================================================================
PAYS_DATA = {
    # === AFRIQUE DE L'OUEST ===
    'BF': {
        'noms': ['burkina faso', 'burkina', 'bf'],
        'villes': ['ouagadougou', 'ouaga', 'bobo-dioulasso', 'koudougou'],
    },
    'CI': {
        'noms': ['côte d\'ivoire', 'cote d\'ivoire', 'ivory coast', 'ci'],
        'villes': ['abidjan', 'yamoussoukro', 'bouaké'],
    },
    'SN': {
        'noms': ['sénégal', 'senegal', 'sn'],
        'villes': ['dakar', 'thiès', 'saint-louis'],
    },
    'ML': {
        'noms': ['mali', 'ml'],
        'villes': ['bamako', 'sikasso', 'mopti'],
    },
    'NE': {
        'noms': ['niger', 'ne'],
        'villes': ['niamey', 'zinder', 'maradi'],
    },
    'TG': {
        'noms': ['togo', 'tg'],
        'villes': ['lomé', 'lome', 'kara', 'sokodé'],
    },
    'BJ': {
        'noms': ['bénin', 'benin', 'bj'],
        'villes': ['cotonou', 'porto-novo', 'parakou'],
    },
    'GH': {
        'noms': ['ghana', 'gh'],
        'villes': ['accra', 'kumasi', 'tamale'],
    },
    'NG': {
        'noms': ['nigeria', 'ng', 'nigéria'],
        'villes': ['abuja', 'lagos', 'kano'],
    },
    'GN': {
        'noms': ['guinée', 'guinea', 'gn'],
        'villes': ['conakry', 'kankan'],
    },
    
    # === AFRIQUE CENTRALE ===
    'CM': {
        'noms': ['cameroun', 'cameroon', 'cm'],
        'villes': ['yaoundé', 'yaounde', 'douala'],
    },
    'GA': {
        'noms': ['gabon', 'ga'],
        'villes': ['libreville', 'port-gentil'],
    },
    'CD': {
        'noms': ['rdc', 'république démocratique du congo', 'republic democratique du congo',
                 'democratic republic of congo', 'congo-kinshasa', 'cd'],
        'villes': ['kinshasa', 'lubumbashi'],
    },
    'CG': {
        'noms': ['congo', 'congo-brazzaville', 'république du congo', 'cg'],
        'villes': ['brazzaville', 'pointe-noire'],
    },
    'TD': {
        'noms': ['tchad', 'chad', 'td'],
        'villes': ['n\'djamena', 'ndjamena'],
    },
    'CF': {
        'noms': ['république centrafricaine', 'republique centrafricaine',
                 'central african republic', 'centrafrique', 'cf'],
        'villes': ['bangui'],
    },
    
    # === AFRIQUE DE L'EST ===
    'RW': {
        'noms': ['rwanda', 'rw'],
        'villes': ['kigali'],
    },
    'ET': {
        'noms': ['éthiopie', 'ethiopia', 'et'],
        'villes': ['addis-abeba', 'addis ababa'],
    },
    'KE': {
        'noms': ['kenya', 'ke'],
        'villes': ['nairobi', 'mombasa'],
    },
    'TZ': {
        'noms': ['tanzanie', 'tanzania', 'tz'],
        'villes': ['dar es salaam', 'dodoma'],
    },
    'UG': {
        'noms': ['ouganda', 'uganda', 'ug'],
        'villes': ['kampala'],
    },
    
    # === AFRIQUE DU NORD ===
    'MA': {
        'noms': ['maroc', 'morocco', 'ma'],
        'villes': ['rabat', 'casablanca', 'marrakech'],
    },
    'DZ': {
        'noms': ['algérie', 'algeria', 'dz'],
        'villes': ['alger', 'oran'],
    },
    'TN': {
        'noms': ['tunisie', 'tunisia', 'tn'],
        'villes': ['tunis', 'sfax'],
    },
    'EG': {
        'noms': ['égypte', 'egypt', 'eg'],
        'villes': ['le caire', 'cairo', 'alexandrie'],
    },
    
    # === AFRIQUE AUSTRALE ===
    'ZA': {
        'noms': ['afrique du sud', 'south africa', 'za'],
        'villes': ['pretoria', 'cape town', 'johannesburg'],
    },
    'MZ': {
        'noms': ['mozambique', 'mz'],
        'villes': ['maputo'],
    },
    
    # === ASIE ===
    'NP': {
        'noms': ['népal', 'nepal', 'np'],
        'villes': ['katmandou', 'kathmandu'],
    },
    'IN': {
        'noms': ['inde', 'india', 'in'],
        'villes': ['new delhi', 'mumbai', 'bangalore'],
    },
    'PK': {
        'noms': ['pakistan', 'pk'],
        'villes': ['islamabad', 'karachi'],
    },
    'AF': {
        'noms': ['afghanistan', 'af'],
        'villes': ['kaboul', 'kabul'],
    },
    'BD': {
        'noms': ['bangladesh', 'bd'],
        'villes': ['dhaka'],
    },
    
    # === AMÉRIQUE LATINE ===
    'AR': {
        'noms': ['argentine', 'argentina', 'ar'],
        'villes': ['buenos aires', 'cordoba'],
    },
    'BR': {
        'noms': ['brésil', 'brazil', 'br'],
        'villes': ['brasilia', 'sao paulo', 'rio'],
    },
    'CO': {
        'noms': ['colombie', 'colombia', 'co'],
        'villes': ['bogota', 'medellin'],
    },
    'MX': {
        'noms': ['mexique', 'mexico', 'mx'],
        'villes': ['mexico city', 'guadalajara'],
    },
    'PE': {
        'noms': ['pérou', 'peru', 'pe'],
        'villes': ['lima'],
    },
    'CL': {
        'noms': ['chili', 'chile', 'cl'],
        'villes': ['santiago'],
    },
    
    # === EUROPE ===
    'FR': {
        'noms': ['france', 'fr'],
        'villes': ['paris', 'lyon', 'marseille'],
    },
    'DE': {
        'noms': ['allemagne', 'germany', 'de'],
        'villes': ['berlin', 'munich'],
    },
    'GB': {
        'noms': ['royaume-uni', 'united kingdom', 'uk', 'great britain', 'gb'],
        'villes': ['london', 'londres', 'manchester'],
    },
    'ES': {
        'noms': ['espagne', 'spain', 'es'],
        'villes': ['madrid', 'barcelona'],
    },
    'PT': {
        'noms': ['portugal', 'pt'],
        'villes': ['lisbonne', 'porto'],
    },
    'BE': {
        'noms': ['belgique', 'belgium', 'be'],
        'villes': ['bruxelles', 'brussels'],
    },
    'CH': {
        'noms': ['suisse', 'switzerland', 'ch'],
        'villes': ['bern', 'geneva', 'zurich'],
    },
    
    # === MOYEN-ORIENT ===
    'SA': {
        'noms': ['arabie saoudite', 'saudi arabia', 'sa'],
        'villes': ['riyadh', 'jeddah'],
    },
    'AE': {
        'noms': ['émirats arabes unis', 'united arab emirates', 'uae', 'ae'],
        'villes': ['dubai', 'abu dhabi'],
    },
    'IL': {
        'noms': ['israël', 'israel', 'il'],
        'villes': ['jerusalem', 'tel aviv'],
    },
    'PS': {
        'noms': ['palestine', 'palestinian', 'ps', 'west bank', 'gaza'],
        'villes': ['ramallah', 'gaza', 'jerusalem'],
    },
    
    # === RÉGIONS MULTI-PAYS ===
    'REGIONAL': {
        'noms': ['régional', 'regional', 'west africa', 'africa', 'afrique',
                 'uemoa', 'ecowas', 'cedao', 'ue', 'eu', 'european union',
                 'union européenne', 'union europeenne', 'multiple countries',
                 'plusieurs pays', 'sous-région', 'sub-region'],
        'villes': [],
    },
    'GLOBAL': {
        'noms': ['global', 'international', 'mondial', 'worldwide', 'world'],
        'villes': [],
    },
}


def detecter_pays_smart(texte: str, url: str = None, pays_defaut: str = 'BF') -> str:
    """
    Détecte le pays de manière intelligente en analysant :
    1. Patterns explicites ("Country: Nepal", "Pays: Burkina Faso")
    2. Noms de pays dans le texte
    3. Villes dans le texte
    4. Domaine de l'URL
    
    Retourne le code ISO du pays (BF, CI, SN, etc.)
    """
    if not texte:
        return pays_defaut
    
    texte_lower = texte.lower()
    
    # =========================================================================
    # ÉTAPE 1 : Chercher des patterns explicites
    # =========================================================================
    patterns_explicites = [
        # Anglais
        r'country[:\s]+([a-zA-Z\s\-]+?)(?:\n|ref|process|deadline)',
        r'country office for ([a-zA-Z\s\-]+?)(?:\n|/)',
        r'location[:\s]+([a-zA-Z\s\-]+?)(?:\n|,)',
        r'based in ([a-zA-Z\s\-]+?)(?:\n|,)',
        r'office/country[:\s]*([a-zA-Z\s\-]+?)(?:\n|/)',
        
        # Français
        r'pays[:\s]+([a-zA-Z\s\-àâéèêëïîôùûüÿç]+?)(?:\n|,)',
        r'localisation[:\s]+([a-zA-Z\s\-àâéèêëïîôùûüÿç]+?)(?:\n|,)',
        r'situ[ée]+[ \w]*[àa] ([a-zA-Z\s\-àâéèêëïîôùûüÿç]+?)(?:\n|,)',
        
        # Espagnol
        r'país[:\s]+([a-zA-Z\s\-áéíóúñü]+?)(?:\n|,)',
        r'ubicaci[óo]n[:\s]+([a-zA-Z\s\-áéíóúñü]+?)(?:\n|,)',
    ]
    
    for pattern in patterns_explicites:
        match = re.search(pattern, texte, re.IGNORECASE)
        if match:
            pays_nom = match.group(1).strip()
            code = _trouver_code_pays(pays_nom)
            if code:
                logger.info(f"🌍 Pays détecté (pattern explicite): '{pays_nom}' → {code}")
                return code
    
    # =========================================================================
    # ÉTAPE 2 : Chercher les noms de pays (triés par longueur décroissante)
    # =========================================================================
    pays_tries = []
    for code, data in PAYS_DATA.items():
        for nom in data['noms']:
            pays_tries.append((len(nom), nom, code))
    
    # Trier par longueur décroissante (pour éviter "congo" avant "république du congo")
    pays_tries.sort(key=lambda x: x[0], reverse=True)
    
    for longueur, nom_pays, code in pays_tries:
        # Utiliser word boundaries pour éviter "congo" dans "condominium"
        pattern = r'\b' + re.escape(nom_pays) + r'\b'
        if re.search(pattern, texte_lower):
            # Vérifier que ce n'est pas un faux positif
            if _est_vrai_pays(texte_lower, nom_pays, code):
                logger.info(f" Pays détecté (nom): '{nom_pays}' → {code}")
                return code
    
    # =========================================================================
    # ÉTAPE 3 : Chercher les villes
    # =========================================================================
    for code, data in PAYS_DATA.items():
        for ville in data.get('villes', []):
            pattern = r'\b' + re.escape(ville) + r'\b'
            if re.search(pattern, texte_lower):
                logger.info(f"🌍 Pays détecté (ville): '{ville}' → {code}")
                return code
    
    # =========================================================================
    # ÉTAPE 4 : Analyser l'URL
    # =========================================================================
    if url:
        code_url = _detecter_pays_url(url)
        if code_url:
            logger.info(f"🌍 Pays détecté (URL): {url} → {code_url}")
            return code_url
    
    return pays_defaut


def _trouver_code_pays(nom_pays: str) -> str:
    """Trouve le code ISO à partir du nom du pays"""
    if not nom_pays:
        return None
    
    nom_lower = nom_pays.lower().strip()
    
    for code, data in PAYS_DATA.items():
        for nom in data['noms']:
            if nom.lower() == nom_lower or nom_lower in nom.lower() or nom.lower() in nom_lower:
                return code
    
    return None


def _est_vrai_pays(texte: str, nom_pays: str, code: str) -> bool:
    """
    Vérifie que le match n'est pas un faux positif
    Ex: "condominium" contient "congo" → faux positif
    """
    # Liste des mots qui pourraient créer des faux positifs
    faux_positifs = {
        'congo': ['condominium', 'conglomérat'],
        'mali': ['maligne', 'malin'],
        'togo': ['togo...'],  # peu de risques
    }
    
    if nom_pays in faux_positifs:
        for mot in faux_positifs[nom_pays]:
            if mot in texte:
                return False
    
    return True


def _detecter_pays_url(url: str) -> str:
    """Détecte le pays à partir de l'URL"""
    if not url:
        return None
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        
        # Détecter le TLD (Top Level Domain)
        tld_mapping = {
            '.bf': 'BF', '.ci': 'CI', '.sn': 'SN', '.ml': 'ML',
            '.ne': 'NE', '.tg': 'TG', '.bj': 'BJ', '.gh': 'GH',
            '.ng': 'NG', '.cm': 'CM', '.ga': 'GA', '.cd': 'CD',
            '.rw': 'RW', '.ke': 'KE', '.tz': 'TZ', '.ug': 'UG',
            '.ma': 'MA', '.dz': 'DZ', '.tn': 'TN', '.eg': 'EG',
            '.za': 'ZA', '.np': 'NP', '.in': 'IN', '.pk': 'PK',
            '.ar': 'AR', '.br': 'BR', '.mx': 'MX', '.fr': 'FR',
            '.de': 'DE', '.es': 'ES', '.pt': 'PT', '.be': 'BE',
            '.ch': 'CH', '.it': 'IT', '.uk': 'GB',
        }
        
        for tld, code in tld_mapping.items():
            if domain.endswith(tld):
                return code
        
        # Détecter les sous-domaines pays
        sous_domaines = {
            'burkina': 'BF', 'burkinafaso': 'BF',
            'senegal': 'SN', 'sénégal': 'SN',
            'cotedivoire': 'CI', 'ivorycoast': 'CI',
            'nepal': 'NP', 'argentina': 'AR',
        }
        
        for key, code in sous_domaines.items():
            if key in domain:
                return code
        
        # Détecter dans le path
        path_mapping = {
            '/bf/': 'BF', '/burkina/': 'BF',
            '/sn/': 'SN', '/senegal/': 'SN',
            '/ci/': 'CI', '/ivory-coast/': 'CI',
            '/np/': 'NP', '/nepal/': 'NP',
            '/ar/': 'AR', '/argentina/': 'AR',
        }
        
        for path_key, code in path_mapping.items():
            if path_key in path:
                return code
        
    except Exception as e:
        logger.debug(f"️ Erreur détection URL: {e}")
    
    return None


def detecter_pays_multiple(texte: str) -> list:
    """
    Détecte TOUS les pays mentionnés dans le texte
    Utile pour les offres régionales ou multi-pays
    """
    if not texte:
        return []
    
    texte_lower = texte.lower()
    pays_detectes = set()
    
    for code, data in PAYS_DATA.items():
        for nom in data['noms']:
            pattern = r'\b' + re.escape(nom) + r'\b'
            if re.search(pattern, texte_lower):
                pays_detectes.add(code)
        
        for ville in data.get('villes', []):
            pattern = r'\b' + re.escape(ville) + r'\b'
            if re.search(pattern, texte_lower):
                pays_detectes.add(code)
    
    return list(pays_detectes)