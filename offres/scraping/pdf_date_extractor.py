"""
Extracteur de dates depuis les PDFs
✅ VERSION FINALE : Extraction contextuelle intelligente
"""
import re
import logging
from datetime import date, datetime, timedelta
from io import BytesIO

logger = logging.getLogger(__name__)

# =============================================================================
# PATTERNS DE DATES (couvrent TOUS les formats)
# =============================================================================

DATE_PATTERNS = [
    # Format français long : "15 janvier 2026", "15 juillet 2026"
    r'(\d{1,2})\s+(janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre)\s+(\d{4})',
    
    # Format français avec virgule : "mars 17, 2026"
    r'(janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre)\s+(\d{1,2}),?\s+(\d{4})',
    
    # Format français avec point : "08 juil. 2026"
    r'(\d{1,2})\s+(jan|fév|fev|mar|avr|mai|jun|juil|jul|aoû|aou|sep|oct|nov|déc|dec)\.?\s+(\d{4})',
    
    # Format numérique : 15/07/2026, 15-07-2026, 15.07.2026
    r'(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})',
    r'(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2})\b',
    
    # Format anglais : "July 20, 2026", "20-Jul-26", "20 July 2026"
    r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2}),?\s+(\d{4})',
    r'(\d{1,2})[-\s](jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[-\s](\d{2,4})',
    r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})',
    
    # Format espagnol : "15 de enero de 2026"
    r'(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+de\s+(\d{4})',
]

# =============================================================================
# MOTS-CLÉS CONTEXTUELS (pour classifier les dates)
# =============================================================================

# Mots qui indiquent une date de CLÔTURE
CLOSURE_CONTEXT_WORDS = [
    # Français
    'clôture', 'cloture', 'date limite', 'date de clôture', 'date butoir',
    'deadline', 'échéance', 'expiration', 'expire le', 'fin de',
    'remise des offres', 'remise des plis', 'remise des dossiers',
    'soumission avant', 'soumettre avant', 'déposer avant',
    'délai de soumission', 'délai de dépôt', 'dernier délai',
    'date de fin', 'fin de réception', 'fermeture',
    'ouverture des plis', 'ouverture des offres',
    'avant le', 'au plus tard le', 'jusqu\'au',
    'date de réception', 'réception des offres',
    
    # Anglais
    'closing date', 'closing time', 'deadline', 'due date',
    'submission deadline', 'submission date', 'bid closing',
    'tender closing', 'proposal deadline', 'expiry date',
    'expiration date', 'cut-off date', 'end date',
    'last date', 'final date', 'submit by', 'submit before',
    'application deadline', 'application closing',
    
    # Espagnol
    'fecha de cierre', 'fecha límite', 'fecha limite',
    'plazo de presentación', 'fecha tope', 'vencimiento',
]

# Mots qui indiquent une date de PUBLICATION
PUBLICATION_CONTEXT_WORDS = [
    # Français
    'publication', 'publié le', 'date de publication', 'parution',
    'date de parution', 'émis le', 'lancé le', 'paru le',
    'mis en ligne', 'posté le', 'annoncé le',
    
    # Anglais
    'publication date', 'published on', 'posted on', 'posted',
    'date published', 'issued on', 'release date', 'launch date',
    'announced on', 'posted date',
    
    # Espagnol
    'fecha de publicación', 'fecha de publicacion', 'publicado el',
    'fecha de emisión', 'fecha de emision',
]


# =============================================================================
# FONCTION PRINCIPALE
# =============================================================================

def extract_dates_from_pdf(pdf_url: str) -> tuple:
    """
    ✅ Extrait les dates de publication et de clôture depuis un PDF
    Retourne (date_publication, date_cloture)
    """
    if not pdf_url:
        return None, None
    
    try:
        # Télécharger le PDF
        import requests
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(pdf_url, timeout=30, headers=headers, verify=False)
        response.raise_for_status()
        
        # Vérifier que c'est un vrai PDF
        if not response.content.startswith(b'%PDF'):
            logger.warning(f"⚠️ Ce n'est pas un PDF valide: {pdf_url[:60]}")
            return None, None
        
        # Extraire le texte du PDF
        text = extract_text_from_pdf(response.content)
        
        if not text or len(text.strip()) < 50:
            logger.warning(f"⚠️ PDF trop court ou vide: {pdf_url[:60]}")
            return None, None
        
        logger.info(f"   📝 Texte PDF extrait: {len(text)} caractères")
        
        # Extraire les dates avec contexte
        date_pub = extract_publication_date(text)
        date_cloture = extract_closure_date(text)
        
        # Si on n'a pas de date de publication mais qu'on a une clôture,
        # chercher la date la plus ancienne dans le document
        if not date_pub and date_cloture:
            all_dates = find_all_dates_in_text(text)
            past_dates = [d for d in all_dates if d < date_cloture]
            if past_dates:
                date_pub = max(past_dates)  # La plus récente avant la clôture
                logger.info(f"   📅 Date publication (déduite): {date_pub}")
        
        return date_pub, date_cloture
        
    except requests.exceptions.Timeout:
        logger.error(f"❌ Timeout PDF: {pdf_url[:60]}")
        return None, None
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erreur téléchargement PDF: {e}")
        return None, None
    except Exception as e:
        logger.error(f"❌ Erreur extraction PDF: {e}")
        return None, None


def extract_text_from_pdf(pdf_content: bytes) -> str:
    """Extrait le texte d'un PDF avec gestion d'erreurs"""
    try:
        from pypdf import PdfReader
        pdf_file = BytesIO(pdf_content)
        reader = PdfReader(pdf_file)
        
        text = ""
        for page in reader.pages:
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            except Exception as e:
                logger.debug(f"⚠️ Erreur extraction page: {e}")
                continue
        
        return text
    except ImportError:
        logger.error("❌ pypdf non installé. Exécutez: pip install pypdf")
        return ""
    except Exception as e:
        logger.error(f"❌ Erreur lecture PDF: {e}")
        return ""


def extract_publication_date(text: str):
    """Extrait la date de publication avec contexte"""
    text_lower = text.lower()
    
    # Chercher d'abord les mots-clés de publication
    for keyword in PUBLICATION_CONTEXT_WORDS:
        if keyword in text_lower:
            # Extraire le contexte autour du mot-clé (±150 caractères)
            idx = text_lower.find(keyword)
            context = text[max(0, idx-150):idx+150]
            
            # Chercher une date dans le contexte
            date_found = find_first_date_in_text(context)
            if date_found and is_valid_date(date_found):
                logger.info(f"   📅 Date publication trouvée via '{keyword}': {date_found}")
                return date_found
    
    return None


def extract_closure_date(text: str):
    """Extrait la date de clôture avec contexte"""
    text_lower = text.lower()
    
    # Chercher les mots-clés de clôture
    for keyword in CLOSURE_CONTEXT_WORDS:
        if keyword in text_lower:
            # Extraire le contexte autour du mot-clé (±150 caractères)
            idx = text_lower.find(keyword)
            context = text[max(0, idx-150):idx+150]
            
            # Chercher une date dans le contexte
            date_found = find_first_date_in_text(context)
            if date_found and is_valid_date(date_found):
                logger.info(f"   📅 Date clôture trouvée via '{keyword}': {date_found}")
                return date_found
    
    # Fallback : chercher la date future la plus proche
    all_dates = find_all_dates_in_text(text)
    today = date.today()
    future_dates = [d for d in all_dates if d >= today and d <= today + timedelta(days=730)]
    
    if future_dates:
        # Prendre la date future la plus proche (généralement la clôture)
        closest = min(future_dates)
        logger.info(f"   📅 Date clôture (future la plus proche): {closest}")
        return closest
    
    return None


def find_first_date_in_text(text: str):
    """Trouve la première date valide dans un texte"""
    for pattern in DATE_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                date_found = parse_date_from_match(match)
                if date_found and is_valid_date(date_found):
                    return date_found
            except Exception:
                continue
    return None


def find_all_dates_in_text(text: str) -> list:
    """Trouve toutes les dates valides dans un texte"""
    all_dates = []
    
    for pattern in DATE_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                date_found = parse_date_from_match(match)
                if date_found and is_valid_date(date_found):
                    all_dates.append(date_found)
            except Exception:
                continue
    
    return sorted(set(all_dates))


def parse_date_from_match(match):
    """Parse une date depuis un match regex"""
    groups = match.groups()
    
    if len(groups) < 3:
        return None
    
    months_map = {
        'janvier': 1, 'février': 2, 'fevrier': 2, 'mars': 3, 'avril': 4,
        'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8, 'aout': 8,
        'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12, 'decembre': 12,
        'jan': 1, 'fév': 2, 'fev': 2, 'mar': 3, 'avr': 4,
        'jun': 6, 'juil': 7, 'jul': 7, 'aoû': 8, 'aou': 8,
        'sep': 9, 'oct': 10, 'nov': 11, 'déc': 12, 'dec': 12,
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5,
        'june': 6, 'july': 7, 'august': 8, 'september': 9, 'october': 10,
        'november': 11, 'december': 12,
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5,
        'junio': 6, 'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10,
        'noviembre': 11, 'diciembre': 12,
    }
    
    try:
        # Format : mois jour année (ex: "mars 17, 2026")
        if groups[0].lower() in months_map:
            month = months_map[groups[0].lower()]
            day = int(groups[1])
            year = int(groups[2])
        
        # Format : jour mois année (ex: "15 janvier 2026")
        elif groups[1].lower() in months_map:
            day = int(groups[0])
            month = months_map[groups[1].lower()]
            year = int(groups[2])
        
        # Format numérique : jour/mois/année
        else:
            day = int(groups[0])
            month = int(groups[1])
            year = int(groups[2])
        
        # Année sur 2 chiffres
        if year < 50:
            year += 2000
        elif year < 100:
            year += 1900
        
        if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2100:
            return date(year, month, day)
    
    except (ValueError, TypeError, IndexError):
        pass
    
    return None


def is_valid_date(d: date) -> bool:
    """Vérifie si une date est valide"""
    if not d:
        return False
    
    today = date.today()
    
    # Date ne doit pas être dans le passé de plus de 2 ans
    if d < today - timedelta(days=730):
        return False
    
    # Date ne doit pas être dans plus de 2 ans
    if d > today + timedelta(days=730):
        return False
    
    return True