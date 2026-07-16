"""
Helpers d'extraction - VERSION FINALE COHÉRENTE
✅ Toutes les fonctions utilisent le même nom : parse_date_from_groups
"""
import re
import logging
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


# =============================================================================
# PARSING UNIVERSEL DES DATES
# =============================================================================

MONTHS_MAP = {
    'janvier': 1, 'février': 2, 'fevrier': 2, 'mars': 3, 'avril': 4,
    'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8, 'aout': 8,
    'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12, 'decembre': 12,
    'jan': 1, 'fév': 2, 'fev': 2, 'mar': 3, 'avr': 4, 'may': 5,
    'jun': 6, 'juil': 7, 'jul': 7, 'aoû': 8, 'aou': 8,
    'sep': 9, 'oct': 10, 'nov': 11, 'déc': 12, 'dec': 12,
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'june': 6, 'july': 7, 'august': 8, 'september': 9,
    'october': 10, 'november': 11, 'december': 12,
}


def parse_date_universelle(date_str: str) -> date | None:
    """Parse une date depuis n'importe quel format courant"""
    if not date_str:
        return None
    
    date_str = str(date_str).strip()
    date_str = re.split(r'\s+\d{1,2}:\d{2}', date_str)[0].strip()
    date_str = re.split(r'\s*\(.*?\)', date_str)[0].strip()
    
    if not date_str:
        return None
    
    # Format ISO : 2026-06-29
    match = re.search(r'(\d{4}-\d{2}-\d{2})', date_str)
    if match:
        try:
            return datetime.strptime(match.group(1), '%Y-%m-%d').date()
        except ValueError:
            pass
    
    # Format avec mois en lettres
    date_text = date_str.replace('/', '-').replace('  ', ' ').strip()
    match = re.match(r'(\d{1,2})[-\s]+([A-Za-zéû]+)[-\s]+(\d{2,4})', date_text, re.IGNORECASE)
    if match:
        day = int(match.group(1))
        month_str = match.group(2).lower()
        year = int(match.group(3))
        
        if year < 100:
            year += 2000 if year < 50 else 1900
        
        month = MONTHS_MAP.get(month_str)
        if month and 1 <= day <= 31:
            try:
                return date(year, month, day)
            except ValueError:
                pass
    
    # Format numérique
    match = re.match(r'(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', date_str)
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


# =============================================================================
# FONCTION CENTRALE DE PARSING DES GROUPES (PUBLIQUE)
# =============================================================================

def parse_date_from_groups(groups) -> date | None:
    """Parse une date depuis des groupes regex (jour, mois, année)"""
    if not groups or len(groups) < 3:
        return None
    
    try:
        # Format : mois jour année (ex: "mars 17, 2026" ou "July 20, 2026")
        if groups[0].lower() in MONTHS_MAP:
            month = MONTHS_MAP[groups[0].lower()]
            day = int(groups[1])
            year = int(groups[2])
        # Format : jour mois année (ex: "15 janvier 2026" ou "15/07/2026")
        elif groups[1].lower() in MONTHS_MAP:
            day = int(groups[0])
            month = MONTHS_MAP[groups[1].lower()]
            year = int(groups[2])
        else:
            # Format numérique pur
            day = int(groups[0])
            month = int(groups[1])
            year = int(groups[2])
        
        # Correction année sur 2 chiffres
        if year < 50:
            year += 2000
        elif year < 100:
            year += 1900
        
        if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2100:
            return date(year, month, day)
    except (ValueError, TypeError, IndexError):
        pass
    
    return None


# =============================================================================
# FONCTIONS INTERNES D'AIDE
# =============================================================================

def _find_any_date(texte: str) -> date | None:
    """Trouve la première date valide dans un texte"""
    dates = _find_all_dates(texte)
    return dates[0] if dates else None


def _find_all_dates(texte: str) -> list:
    """Trouve toutes les dates valides dans un texte"""
    if not texte:
        return []
    
    patterns = [
        r'(\d{1,2})\s+(janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre)\s+(\d{4})',
        r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{4})',
        r'(\d{1,2})\s+([A-Za-z]{3,9})\s+(\d{4})',
    ]
    
    all_dates = []
    for pattern in patterns:
        for match in re.finditer(pattern, texte, re.IGNORECASE):
            parsed = parse_date_from_groups(match.groups())
            if parsed:
                all_dates.append(parsed)
    
    return sorted(set(all_dates))


# =============================================================================
# EXTRACTION DES DATES DEPUIS LE TEXTE
# =============================================================================

def extract_publication_date_from_text(texte: str) -> date | None:
    """Extrait la date de publication depuis un texte"""
    if not texte:
        return None
    
    today = date.today()
    
    patterns_contexte = [
        r'(?:date\s+du\s+lancement|lancement\s+d\'appel|date\s+de\s+publication)\s*[:;]?\s*(?:le\s+)?(\d{1,2})\s+(janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre)\s+(\d{4})',
        r'(?:posted|publication|publi[ée])\s*(\d{1,2})\s+([A-Za-z]{3,9})\s+(\d{4})',
        r'(?:publi[ée]\s*le|date\s*de\s*publication)\s*(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{4})',
    ]
    
    for pattern in patterns_contexte:
        match = re.search(pattern, texte, re.IGNORECASE)
        if match:
            parsed = parse_date_from_groups(match.groups())
            if parsed and parsed <= today:
                logger.info(f"📅 Date publication trouvée: {parsed}")
                return parsed
    
    debut = texte[:1000]
    parsed = _find_any_date(debut)
    if parsed and parsed <= today:
        logger.info(f"📅 Date publication (début): {parsed}")
        return parsed
    
    return None


def extract_deadline_from_text(texte: str) -> date | None:
    """Extrait la date de clôture depuis un texte"""
    if not texte:
        return None
    
    today = date.today()
    
    patterns_contexte = [
        r'(?:date\s+limite\s+de\s+réception\s+des\s+offres|date\s+limite\s+de\s+dép[oô]t|date\s+limite)\s*[:;]?\s*(?:le\s+)?(\d{1,2})\s+(janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre)\s+(\d{4})',
        r'(?:closing\s*date|deadline|closing)\s*(\d{1,2})\s+([A-Za-z]{3,9})\s+(\d{4})',
        r'(?:cl[oô]ture|deadline|date\s*limite)\s*[:;\s]*(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{4})',
        r'(?:jusqu\'au|au\s*plus\s*tard\s*le)\s*(\d{1,2})\s+(janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre)\s+(\d{4})',
    ]
    
    for pattern in patterns_contexte:
        match = re.search(pattern, texte, re.IGNORECASE)
        if match:
            parsed = parse_date_from_groups(match.groups())
            if parsed:
                if parsed >= today - timedelta(days=7):
                    logger.info(f"📅 Date clôture trouvée: {parsed}")
                    return parsed
    
    toutes_dates = _find_all_dates(texte)
    futures = [d for d in toutes_dates if d >= today and d <= today + timedelta(days=730)]
    
    if futures:
        futures.sort()
        meilleure = futures[-1]
        logger.info(f"📅 Date clôture (fallback, plus lointaine): {meilleure}")
        return meilleure
    
    return None


# =============================================================================
# EXTRACTION DE L'ORGANISME
# =============================================================================

def extract_organisme(soup: BeautifulSoup, url: str, titre: str) -> str | None:
    """Extrait l'organisme depuis la page"""
    if not soup:
        return None
    
    texte = soup.get_text()
    
    patterns = [
        r'(?:organisme|organization|organisation|entit[eé]|entity|entreprise|company|structure)\s*[:;\s]+([^\n\r]{3,100})',
        r'(?:[ée]mis\s*par|issued\s*by|publi[ée]\s*par|published\s*by)\s*[:;\s]+([^\n\r]{3,100})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, texte, re.IGNORECASE)
        if match:
            org = match.group(1).strip()
            org = re.split(r'[\n\r]', org)[0].strip()
            if len(org) >= 3 and len(org) <= 100:
                return org
    
    return None


# =============================================================================
# EXTRACTION UNIFIÉE
# =============================================================================

def extract_all_details(soup: BeautifulSoup, url: str = "", pays_defaut: str = None, 
                       titre: str = "", description: str = "") -> dict:
    """
    Extrait tous les champs SANS valeurs par défaut
    """
    result = {
        'pays': None,
        'date_publication': None,
        'date_cloture': None,
        'domaine': None,
        'organisme': None,
        'url_tdr': None,
        'texte_complet': '',
    }
    
    if not soup:
        return result
    
    result['texte_complet'] = soup.get_text(separator=' ')[:15000]
    texte_complet = result['texte_complet']
    
    # DATES
    result['date_publication'] = extract_publication_date_from_text(texte_complet)
    result['date_cloture'] = extract_deadline_from_text(texte_complet)
    
    # PAYS
    from offres.scraping.country_detector import detecter_pays_smart
    result['pays'] = detecter_pays_smart(
        texte_complet, 
        url=url, 
        pays_defaut=pays_defaut
    )
    
    # ORGANISME
    result['organisme'] = extract_organisme(soup, url, titre)
    
    # DOMAINE
    from offres.utils.search_keywords import detecter_domaine
    texte_pour_domaine = f"{titre} {description} {texte_complet[:2000]}"
    result['domaine'] = detecter_domaine(texte_pour_domaine)
    
    # PDF
    result['url_tdr'] = extract_pdf_url(soup, url)
    
    return result


# =============================================================================
# EXTRACTION PDF
# =============================================================================

def extract_pdf_url(soup: BeautifulSoup, base_url: str) -> str | None:
    """Extrait l'URL du PDF"""
    if not soup:
        return None
    
    candidats = []
    
    for link in soup.find_all('a', href=True):
        href = link['href'].strip()
        text = link.get_text(strip=True).lower()
        
        if href.lower().endswith('.pdf'):
            full_url = urljoin(base_url, href)
            if not any(x in href.lower() for x in ['logo', 'icon', 'favicon']):
                candidats.append((100, full_url))
        
        elif any(kw in text for kw in [
            'télécharger', 'telecharger', 'download', 'tdr',
            'termes de référence', 'cahier des charges'
        ]):
            if not href.startswith('#') and not href.startswith('javascript:'):
                full_url = urljoin(base_url, href)
                candidats.append((80, full_url))
    
    if candidats:
        candidats.sort(key=lambda x: x[0], reverse=True)
        return candidats[0][1]
    
    return None


# =============================================================================
# VALIDATIONS
# =============================================================================

def is_offer_expired(date_cloture) -> bool:
    """Vérifie si une offre est expirée"""
    if not date_cloture:
        return False  # Pas de date = pas expirée
    
    if isinstance(date_cloture, str):
        date_cloture = parse_date_universelle(date_cloture)
    elif isinstance(date_cloture, datetime):
        date_cloture = date_cloture.date()
    
    if not date_cloture:
        return False
    
    return date_cloture < date.today()


def is_date_unrealistic(date_cloture) -> bool:
    """Vérifie si une date est irréaliste"""
    if not date_cloture:
        return True
    
    if isinstance(date_cloture, str):
        date_cloture = parse_date_universelle(date_cloture)
    
    if not date_cloture:
        return True
    
    three_years_later = date.today() + timedelta(days=365*3)
    return date_cloture > three_years_later


def is_offer_too_old(date_publication, max_days: int = 365) -> bool:
    """Vérifie si une offre est trop ancienne"""
    if not date_publication:
        return True
    
    if isinstance(date_publication, str):
        date_publication = parse_date_universelle(date_publication)
    
    if not date_publication:
        return True
    
    return (date.today() - date_publication).days > max_days


def is_offer_valid(offre: dict) -> tuple[bool, str]:
    """Validation STRICTE : aucune valeur par défaut acceptée"""
    titre = offre.get('titre', '')
    date_cloture = offre.get('date_cloture')
    date_publication = offre.get('date_publication')
    pays = offre.get('pays')
    
    if not titre or len(titre) < 15:
        return False, "Titre manquant ou trop court"
    
    if not date_cloture:
        return False, "Aucune date de clôture trouvée"
    
    if not date_publication:
        return False, "Aucune date de publication trouvée"
    
    if not pays:
        return False, "Aucun pays détecté"
    
    if is_offer_expired(date_cloture):
        return False, f"Expirée: {date_cloture}"
    
    if is_date_unrealistic(date_cloture):
        return False, f"Date irréaliste: {date_cloture}"
    
    if is_offer_too_old(date_publication):
        return False, f"Trop ancienne: {date_publication}"
    
    return True, "Valide"