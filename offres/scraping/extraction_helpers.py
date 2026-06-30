# offres/scraping/extraction_helpers.py
"""
Helpers centralisés pour l'extraction des offres
Version finale avec filtrage complet
"""
import re
import logging
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from offres.utils.search_keywords import detecter_domaine
from offres.scraping.country_detector import detecter_pays_smart
from offres.utils.offer_validator import is_valid_offer_title

logger = logging.getLogger(__name__)


# =============================================================================
# 1. PARSING UNIVERSEL DES DATES
# =============================================================================

MONTHS_MAP = {
    'janvier': 1, 'février': 2, 'fevrier': 2, 'mars': 3, 'avril': 4,
    'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8, 'aout': 8,
    'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12, 'decembre': 12,
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'june': 6, 'july': 7, 'august': 8, 'september': 9,
    'october': 10, 'november': 11, 'december': 12,
}


def parse_date_universelle(date_str: str) -> date | None:
    """Parse une date depuis n'importe quel format courant"""
    if not date_str:
        return None
    
    date_str = date_str.strip()
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
    match = re.match(
        r'(\d{1,2})[-\s]+([A-Za-zéû]+)[-\s]+(\d{2,4})',
        date_text,
        re.IGNORECASE
    )
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
# 2. EXTRACTION UNIFIÉE DE TOUS LES CHAMPS
# =============================================================================

def extract_all_details(soup: BeautifulSoup, url: str = "", pays_defaut: str = 'BF', 
                       titre: str = "", description: str = "") -> dict:
    """
    Extrait tous les champs d'une page de détail
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
    
    result['texte_complet'] = soup.get_text()[:5000]
    texte_pour_domaine = f"{titre} {description} {result['texte_complet']}"
    
    # Patterns spécifiques pour les dates
    date_patterns = [
        r'deadline[:\s]+(\d{1,2}[-\s]+[A-Za-z]{3,9}[-\s]+\d{2,4})',
        r'deadline[:\s]+(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4})',
        r'posted[:\s]+(\d{1,2}[-\s]+[A-Za-z]{3,9}[-\s]+\d{2,4})',
        r'posted[:\s]+(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4})',
        r'published\s+on[:\s]+(\d{1,2}[-\s]+[A-Za-z]{3,9}[-\s]+\d{2,4})',
        r'date\s+limite[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'date\s+de\s+cl[oô]ture[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
    ]
    
    texte_complet = result['texte_complet']
    
    # Extraire les dates avec des patterns spécifiques
    for pattern in date_patterns:
        match = re.search(pattern, texte_complet, re.IGNORECASE)
        if match:
            date_str = match.group(1).strip()
            parsed_date = parse_date_universelle(date_str)
            if parsed_date:
                if 'deadline' in pattern.lower() or 'clôture' in pattern.lower() or 'limite' in pattern.lower():
                    if not result['date_cloture']:
                        result['date_cloture'] = parsed_date
                else:
                    if not result['date_publication']:
                        result['date_publication'] = parsed_date
    
    # Parcourir les éléments
    for elem in soup.find_all(['td', 'th', 'dt', 'dd', 'div', 'span', 'strong', 'b', 'p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        text = elem.get_text(strip=True)
        text_lower = text.lower()
        
        # PAYS
        if re.search(r'\b(office|country|pays)\b', text_lower):
            next_elem = elem.find_next_sibling()
            if next_elem:
                next_text = next_elem.get_text(strip=True)
                if next_text and len(next_text) > 2:
                    detected = detecter_pays_smart(next_text, url=url, pays_defaut=pays_defaut)
                    if detected != pays_defaut:
                        result['pays'] = detected
        
        # DOMAINE
        elif re.search(r'\b(category|type|sector|domaine)\b', text_lower):
            next_elem = elem.find_next_sibling()
            if next_elem:
                next_text = next_elem.get_text(strip=True)
                if next_text:
                    detected = detecter_domaine(next_text)
                    if detected != 'Autres':
                        result['domaine'] = detected
        
        # PDF
        elif elem.name == 'a' and elem.get('href'):
            href = elem.get('href', '').lower()
            link_text = text.lower()
            if '.pdf' in href or any(kw in link_text for kw in ['download', 'télécharger', 'tdr']):
                result['url_tdr'] = urljoin(url, elem.get('href'))
    
    # Fallbacks
    if not result['date_publication']:
        result['date_publication'] = date.today()
    
    if not result['date_cloture']:
        result['date_cloture'] = _extract_deadline_from_text(texte_complet)
    
    if not result['date_cloture']:
        result['date_cloture'] = date.today() + timedelta(days=30)
    
    if result['domaine'] == 'Autres':
        result['domaine'] = detecter_domaine(texte_pour_domaine)
    
    return result


def _extract_deadline_from_text(texte: str):
    """Extrait la date limite depuis un texte complet"""
    date_patterns = [
        r'\d{1,2}[-\s]+[A-Za-z]{3,9}[-\s]+\d{2,4}',
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, texte, re.IGNORECASE)
        for match in matches:
            parsed = parse_date_universelle(match)
            if parsed and parsed >= date.today():
                return parsed
    
    return None


# =============================================================================
# 3. VÉRIFICATION OFFRE EXPIRÉE
# =============================================================================

def is_offer_expired(date_cloture) -> bool:
    """Vérifie si une offre est expirée"""
    if not date_cloture:
        return False
    
    if isinstance(date_cloture, str):
        date_cloture = parse_date_universelle(date_cloture)
    elif isinstance(date_cloture, datetime):
        date_cloture = date_cloture.date()
    
    if not date_cloture:
        return False
    
    return date_cloture < date.today()


# =============================================================================
# 4. VÉRIFICATION DATE IRRÉALISTE
# =============================================================================

def is_date_unrealistic(date_cloture) -> bool:
    """Vérifie si une date de clôture est irréaliste (> 3 ans)"""
    if not date_cloture:
        return False
    
    if isinstance(date_cloture, str):
        date_cloture = parse_date_universelle(date_cloture)
    elif isinstance(date_cloture, datetime):
        date_cloture = date_cloture.date()
    
    if not date_cloture:
        return False
    
    three_years_later = date.today() + timedelta(days=365*3)
    return date_cloture > three_years_later


# =============================================================================
# 5. VÉRIFICATION OFFRE TROP ANCIENNE
# =============================================================================

def is_offer_too_old(date_publication) -> bool:
    """Vérifie si une offre est trop ancienne (> 2 ans)"""
    if not date_publication:
        return False
    
    if isinstance(date_publication, str):
        date_publication = parse_date_universelle(date_publication)
    elif isinstance(date_publication, datetime):
        date_publication = date_publication.date()
    
    if not date_publication:
        return False
    
    two_years_ago = date.today() - timedelta(days=365*2)
    return date_publication < two_years_ago


# =============================================================================
# 6. VALIDATION COMPLÈTE D'UNE OFFRE
# =============================================================================

def is_offer_valid(offre: dict) -> tuple[bool, str]:
    """
    Valide une offre complète
    Retourne (is_valid, reason)
    """
    titre = offre.get('titre', '')
    date_cloture = offre.get('date_cloture')
    date_publication = offre.get('date_publication')
    
    # 1. Vérifier le titre
    if not is_valid_offer_title(titre):
        return False, f"Titre invalide: {titre[:50]}"
    
    # 2. Vérifier si expirée
    if is_offer_expired(date_cloture):
        return False, f"Expirée: {date_cloture}"
    
    # 3. Vérifier date irréaliste
    if is_date_unrealistic(date_cloture):
        return False, f"Date irréaliste: {date_cloture}"
    
    # 4. Vérifier offre trop ancienne
    if is_offer_too_old(date_publication):
        return False, f"Trop ancienne: {date_publication}"
    
    return True, "Valide"


# offres/scraping/extraction_helpers.py - Remplacer extract_pdf_url

# À la fin de offres/scraping/extraction_helpers.py
# À la fin de offres/scraping/extraction_helpers.py, remplacer extract_pdf_url

def extract_pdf_url(soup: BeautifulSoup, base_url: str) -> str | None:
    """
    Extrait l'URL du PDF/TDR depuis une page HTML
    Retourne la meilleure URL trouvée ou None
    """
    if not soup:
        return None
    
    candidats = []
    
    # Stratégie 1 : Liens directs vers PDF
    for link in soup.find_all('a', href=True):
        href = link['href'].strip()
        text = link.get_text(strip=True).lower()
        
        # Liens avec extension .pdf
        if href.lower().endswith('.pdf'):
            full_url = urljoin(base_url, href)
            # Exclure les faux PDFs (logos, icônes)
            if not any(x in href.lower() for x in ['logo', 'icon', 'favicon', 'header', 'footer']):
                candidats.append((100, full_url, 'pdf_direct'))
        
        # Liens avec mots-clés de téléchargement
        elif any(kw in text for kw in [
            'télécharger', 'telecharger', 'download', 'tdr',
            'termes de référence', 'terms of reference',
            'cahier des charges', 'dossier de consultation',
            'document', 'pièce jointe', 'annexe'
        ]):
            if not href.startswith('#') and not href.startswith('javascript:'):
                full_url = urljoin(base_url, href)
                score = 80
                if 'tdr' in text or 'termes de référence' in text:
                    score = 95
                candidats.append((score, full_url, 'mot_cle'))
    
    # Stratégie 2 : Chercher dans les boutons
    for button in soup.find_all(['button', 'input']):
        text = button.get_text(strip=True).lower() if button.name == 'button' else button.get('value', '').lower()
        onclick = button.get('onclick', '').lower()
        
        if any(kw in text or kw in onclick for kw in ['download', 'pdf', 'tdr']):
            parent = button.find_parent('a')
            if parent and parent.get('href'):
                full_url = urljoin(base_url, parent['href'])
                candidats.append((70, full_url, 'button'))
    
    # Stratégie 3 : Chercher dans les iframes ou embeds
    for embed in soup.find_all(['iframe', 'embed']):
        src = embed.get('src', '')
        if src and '.pdf' in src.lower():
            full_url = urljoin(base_url, src)
            candidats.append((60, full_url, 'embed'))
    
    # Trier par score et retourner le meilleur
    if candidats:
        candidats.sort(key=lambda x: x[0], reverse=True)
        best = candidats[0]
        logger.info(f"   📄 PDF trouvé: {best[1][:80]} (score: {best[0]})")
        return best[1]
    
    return None

# =============================================================================
# EXTRACTION DE DATE DE PUBLICATION
# =============================================================================

def extract_publication_date_from_text(texte: str) -> date | None:
    """Extrait la date de publication depuis un texte"""
    if not texte:
        return None
    
    patterns = [
        r'posted\s*[:;]\s*(\d{2})-([A-Za-z]{3})-(\d{2,4})',
        r'published\s*[:;]\s*(\d{2})-([A-Za-z]{3})-(\d{2,4})',
        r'publication\s*[:;]\s*(\d{2})-([A-Za-z]{3})-(\d{2,4})',
        r'publié le\s*[:;]\s*(\d{2})-([A-Za-z]{3})-(\d{2,4})',
        r'publié\s*[:;]\s*(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
        r'date\s*[:;]\s*(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
    ]
    
    months_en = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    for pattern in patterns:
        match = re.search(pattern, texte, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) >= 3:
                try:
                    day = int(groups[0])
                    month_str = groups[1].lower()
                    year_str = groups[2]
                    
                    if month_str.isdigit():
                        month = int(month_str)
                    else:
                        month = months_en.get(month_str[:3], 1)
                    
                    year = int(year_str)
                    if year < 50:
                        year += 2000
                    elif year < 100:
                        year += 1900
                    
                    parsed = date(year, month, day)
                    if parsed <= date.today():
                        return parsed
                except (ValueError, TypeError):
                    continue
    
    return None