# offres/scraping/extraction_helpers.py
"""
Helpers centralisés pour l'extraction des offres
Utilisés par TOUS les parsers pour garantir la cohérence
"""
import re
import logging
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup

from offres.scraping.constantes import detecter_domaine
from offres.scraping.country_detector import detecter_pays_smart

logger = logging.getLogger(__name__)


# =============================================================================
# 1. EXTRACTION UNIVERSELLE DES DATES
# =============================================================================

# Patterns de dates courants (ordre important)
DATE_PATTERNS = [
    # Format ISO : 2026-06-29
    (r'(\d{4}-\d{2}-\d{2})', '%Y-%m-%d'),
    # Format UNDP : 29-Jun-26 ou 29-June-2026
    (r'(\d{1,2}[-/]\s*[A-Za-z]{3,9}[-/]\s*\d{2,4})', None),
    # Format français : 29/06/2026 ou 29-06-2026
    (r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', None),
    # Format texte : "29 juin 2026", "29 Juin 2026"
    (r'(\d{1,2}\s+[A-Za-zéû]+\s+\d{2,4})', None),
]

# Mapping des mois (FR + EN)
MONTHS_MAP = {
    # Français
    'janvier': 1, 'février': 2, 'fevrier': 2, 'mars': 3, 'avril': 4,
    'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8, 'aout': 8,
    'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12, 'decembre': 12,
    # Anglais court
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
    # Anglais long
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'june': 6, 'july': 7, 'august': 8, 'september': 9,
    'october': 10, 'november': 11, 'december': 12,
}


def parse_date_universelle(date_str: str) -> date | None:
    """
    Parse une date depuis n'importe quel format courant
    Retourne un objet date ou None
    """
    if not date_str:
        return None
    
    # Nettoyer la chaîne
    date_str = date_str.strip()
    # Enlever l'heure et le fuseau horaire
    date_str = re.split(r'\s+\d{1,2}:\d{2}', date_str)[0].strip()
    date_str = re.split(r'\s*\(.*?\)', date_str)[0].strip()
    
    if not date_str:
        return None
    
    # Essayer chaque pattern
    for pattern, fmt in DATE_PATTERNS:
        match = re.search(pattern, date_str, re.IGNORECASE)
        if match:
            date_text = match.group(1).strip()
            
            # Format ISO simple
            if fmt == '%Y-%m-%d':
                try:
                    return datetime.strptime(date_text, fmt).date()
                except ValueError:
                    continue
            
            # Format avec mois en lettres (FR/EN)
            if any(mois in date_text.lower() for mois in MONTHS_MAP.keys()):
                result = _parse_date_with_month_name(date_text)
                if result:
                    return result
            
            # Format numérique DD/MM/YYYY ou DD-MM-YYYY
            result = _parse_numeric_date(date_text)
            if result:
                return result
    
    logger.debug(f"⚠️ Date non reconnue: {date_str}")
    return None


def _parse_date_with_month_name(date_text: str) -> date | None:
    """Parse une date avec nom de mois (ex: '29-Jun-26', '29 juin 2026')"""
    # Normaliser les séparateurs
    date_text = date_text.replace('/', '-').replace('  ', ' ').strip()
    
    # Pattern : 29-Jun-26 ou 29 Jun 2026
    match = re.match(
        r'(\d{1,2})[-\s]+([A-Za-zéû]+)[-\s]+(\d{2,4})',
        date_text,
        re.IGNORECASE
    )
    if match:
        day = int(match.group(1))
        month_str = match.group(2).lower()
        year = int(match.group(3))
        
        # Année sur 2 chiffres → 4 chiffres
        if year < 100:
            year += 2000 if year < 50 else 1900
        
        month = MONTHS_MAP.get(month_str)
        if month and 1 <= day <= 31:
            try:
                return date(year, month, day)
            except ValueError:
                pass
    
    return None


def _parse_numeric_date(date_text: str) -> date | None:
    """Parse une date numérique DD/MM/YYYY ou DD-MM-YYYY"""
    # Normaliser
    date_text = date_text.replace('/', '-').strip()
    
    match = re.match(r'(\d{1,2})-(\d{1,2})-(\d{2,4})', date_text)
    if match:
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))
        
        if year < 100:
            year += 2000 if year < 50 else 1900
        
        if 1 <= day <= 31 and 1 <= month <= 12:
            try:
                return date(year, month, day)
            except ValueError:
                pass
    
    return None


def extraire_date_cloture(soup: BeautifulSoup, texte_complet: str = "") -> date | None:
    """
    Extrait la date de clôture depuis une page HTML
    Cherche dans cet ordre :
    1. Patterns explicites (Deadline, Date limite, etc.)
    2. Dates dans le texte complet
    """
    if not soup:
        return None
    
    # Keywords pour identifier la date de clôture
    deadline_keywords = [
        'deadline', 'date limite', 'date de clôture', 'date de cloture',
        'closing date', 'submission deadline', 'date de soumission',
        'expiration', 'expire le', 'expires on', 'due date',
        'fecha límite', 'plazo', 'closing',
    ]
    
    # Chercher les éléments avec ces keywords
    for elem in soup.find_all(['td', 'th', 'dt', 'dd', 'div', 'span', 'strong', 'b', 'p', 'li']):
        text = elem.get_text(strip=True).lower()
        
        # Vérifier si cet élément contient un keyword de deadline
        if any(kw in text for kw in deadline_keywords):
            # Chercher la date dans cet élément ou son voisin
            date_candidates = []
            
            # Dans l'élément lui-même
            date_candidates.append(elem.get_text())
            
            # Dans les éléments voisins
            for sibling in [elem.find_next_sibling(), elem.find_parent()]:
                if sibling:
                    date_candidates.append(sibling.get_text())
            
            # Essayer de parser chaque candidat
            for candidate in date_candidates:
                if not candidate:
                    continue
                
                # Chercher toutes les dates dans le texte
                date_matches = re.findall(
                    r'\d{1,2}[-/\s]+[A-Za-zéû]+[-/\s]+\d{2,4}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}-\d{2}-\d{2}',
                    candidate,
                    re.IGNORECASE
                )
                
                for date_match in date_matches:
                    parsed = parse_date_universelle(date_match)
                    if parsed:
                        # Vérifier que c'est une date future ou récente (pas une vieille date)
                        if parsed >= date.today() - timedelta(days=30):
                            return parsed
    
    # Fallback : chercher dans le texte complet
    if texte_complet:
        date_matches = re.findall(
            r'\d{1,2}[-/\s]+[A-Za-zéû]+[-/\s]+\d{2,4}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}-\d{2}-\d{2}',
            texte_complet,
            re.IGNORECASE
        )
        for date_match in date_matches:
            parsed = parse_date_universelle(date_match)
            if parsed and parsed >= date.today() - timedelta(days=30):
                return parsed
    
    return None


# =============================================================================
# 2. EXTRACTION UNIVERSELLE DU PAYS
# =============================================================================

def extraire_pays(soup: BeautifulSoup, texte_complet: str = "", url: str = "", pays_defaut: str = 'BF') -> str:
    """
    Extrait le pays depuis une page HTML
    Utilise le détecteur intelligent existant
    """
    if not texte_complet and soup:
        texte_complet = soup.get_text()[:3000]
    
    return detecter_pays_smart(texte_complet, url=url, pays_defaut=pays_defaut)


# =============================================================================
# 3. EXTRACTION UNIVERSELLE DU DOMAINE
# =============================================================================

def extraire_domaine(soup: BeautifulSoup = None, texte_complet: str = "", category_text: str = "") -> str:
    """
    Extrait le domaine depuis une page HTML
    """
    # Si on a un texte de catégorie explicite (ex: UNDP), l'utiliser en priorité
    if category_text:
        domaine = detecter_domaine(category_text)
        if domaine != 'Autres':
            return domaine
    
    # Sinon, utiliser le texte complet
    if not texte_complet and soup:
        texte_complet = soup.get_text()[:3000]
    
    return detecter_domaine(texte_complet)


# =============================================================================
# 4. VÉRIFICATION OFFRE EXPIRÉE
# =============================================================================

def is_offer_expired(date_cloture) -> bool:
    """
    Vérifie si une offre est expirée
    Accepte : date, datetime, string, None
    """
    if not date_cloture:
        return False  # Pas de date = on ne peut pas dire qu'elle est expirée
    
    # Convertir en date si nécessaire
    if isinstance(date_cloture, str):
        date_cloture = parse_date_universelle(date_cloture)
    elif isinstance(date_cloture, datetime):
        date_cloture = date_cloture.date()
    
    if not date_cloture:
        return False
    
    # Une offre est expirée si sa date de clôture est STRICTEMENT avant aujourd'hui
    return date_cloture < date.today()


# =============================================================================
# 5. HELPER POUR EXTRAIRE TOUS LES CHAMPS D'UNE PAGE DE DÉTAIL
# =============================================================================

def extract_all_details(soup: BeautifulSoup, url: str = "", pays_defaut: str = 'BF') -> dict:
    """
    Extrait tous les champs d'une page de détail en une seule passe
    Retourne un dict avec : pays, date_publication, date_cloture, domaine, url_tdr
    """
    result = {
        'pays': pays_defaut,
        'date_publication': None,
        'date_cloture': None,
        'domaine': 'Autres',
        'url_tdr': None,
        'texte_complet': '',
    }
    
    if not soup:
        return result
    
    # Récupérer le texte complet
    result['texte_complet'] = soup.get_text()[:5000]
    
    # Parcourir tous les éléments une seule fois
    for elem in soup.find_all(['td', 'th', 'dt', 'dd', 'div', 'span', 'strong', 'b', 'p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        text = elem.get_text(strip=True)
        text_lower = text.lower()
        
        # PAYS
        if re.search(r'\b(office|country|pays|país|ubicaci[oó]n|location)\b', text_lower):
            next_elem = elem.find_next_sibling()
            if next_elem:
                next_text = next_elem.get_text(strip=True)
                if next_text and len(next_text) > 2:
                    detected = detecter_pays_smart(next_text, url=url, pays_defaut=pays_defaut)
                    if detected != pays_defaut:
                        result['pays'] = detected
        
        # DATE DE CLÔTURE
        elif re.search(r'\b(deadline|date limite|date de cl[ôo]ture|closing date|fecha l[ií]mite)\b', text_lower):
            next_elem = elem.find_next_sibling()
            if next_elem:
                next_text = next_elem.get_text(strip=True)
                parsed = parse_date_universelle(next_text)
                if parsed:
                    result['date_cloture'] = parsed
        
        # DATE DE PUBLICATION
        elif re.search(r'\b(published on|posted|publi[éc] le|date de publication|fecha de publicaci[oó]n)\b', text_lower):
            next_elem = elem.find_next_sibling()
            if next_elem:
                next_text = next_elem.get_text(strip=True)
                parsed = parse_date_universelle(next_text)
                if parsed:
                    result['date_publication'] = parsed
        
        # DOMAINE / CATÉGORIE
        elif re.search(r'\b(category|type|sector|procurement type|domaine|categor[ií]a)\b', text_lower):
            next_elem = elem.find_next_sibling()
            if next_elem:
                next_text = next_elem.get_text(strip=True)
                if next_text:
                    detected = detecter_domaine(next_text)
                    if detected != 'Autres':
                        result['domaine'] = detected
        
        # PDF / TDR
        elif elem.name == 'a' and elem.get('href'):
            href = elem.get('href', '').lower()
            link_text = text.lower()
            if '.pdf' in href or any(kw in link_text for kw in ['download', 'télécharger', 'tdr', 'terms of reference']):
                from urllib.parse import urljoin
                result['url_tdr'] = urljoin(url, elem.get('href'))
    
    # Fallbacks
    if not result['date_publication']:
        result['date_publication'] = date.today()
    
    if not result['date_cloture']:
        # Essayer d'extraire depuis le texte complet
        result['date_cloture'] = extraire_date_cloture(soup, result['texte_complet'])
    
    if not result['date_cloture']:
        result['date_cloture'] = date.today() + timedelta(days=30)
    
    if result['domaine'] == 'Autres':
        result['domaine'] = detecter_domaine(result['texte_complet'])
    
    return result