"""
offres/scraping/utils.py
Fonctions utilitaires pour le scraping - VERSION CORRIGÉE
✅ Ajout validation PDF stricte + extraction robuste
"""

import re
from datetime import date, datetime
import logging
import requests
import uuid
from django.core.files.base import ContentFile
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def clean_text(text):
    if isinstance(text, (date, datetime)):
        return text.strftime('%Y-%m-%d')
    if not isinstance(text, str):
        return str(text) if text else ''
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def parse_french_date(date_str, default_days=30):
    from django.utils import timezone
    
    if isinstance(date_str, (date, datetime)):
        return date_str.date() if isinstance(date_str, datetime) else date_str
    if not date_str:
        return (timezone.now() + timezone.timedelta(days=default_days)).date()
    if not isinstance(date_str, str):
        return (timezone.now() + timezone.timedelta(days=default_days)).date()
    
    date_str = clean_text(date_str)
    
    patterns = [
        r'(\d{2})[/\-](\d{2})[/\-](\d{4})',
        r'(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})',
    ]
    
    months_fr = {
        'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
        'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
    }
    
    for pattern in patterns:
        match = re.search(pattern, date_str, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) == 3:
                if groups[0].isdigit() and groups[1].isdigit() and groups[2].isdigit():
                    day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
                else:
                    day = int(groups[0])
                    month = months_fr.get(groups[1].lower(), 1)
                    year = int(groups[2])
                try:
                    return date(year, month, day)
                except ValueError:
                    pass
    
    return (timezone.now() + timezone.timedelta(days=default_days)).date()


def normalize_url(url, base_url):
    from urllib.parse import urljoin
    if not url:
        return None
    if url.startswith('http://') or url.startswith('https://'):
        return url
    return urljoin(base_url, url)


def archive_expired_offres():
    from offres.models import AppelOffre
    from django.utils import timezone
    
    expired = AppelOffre.objects.filter(
        date_cloture__lt=timezone.now().date(),
        statut='Ouvert'
    )
    count = expired.count()
    expired.update(statut='Expiré')
    return count


def get_first_pdf_url(soup, base_url):
    """Extrait le premier lien PDF valide trouvé dans la page"""
    # Liens directs .pdf
    for link in soup.find_all('a', href=True):
        href = link.get('href', '').strip()
        if href.lower().endswith('.pdf'):
            return normalize_url(href, base_url)
    
    # Liens avec mots-clés prioritaires
    priority_keywords = ['tdr', 'cahier des charges', 'termes de référence', 
                        'document', 'download', 'télécharger', 'pdf']
    for link in soup.find_all('a', href=True):
        text = link.get_text().lower()
        href = link.get('href', '').strip()
        if any(kw in text for kw in priority_keywords) and '.pdf' in href.lower():
            return normalize_url(href, base_url)
    
    # Embed/iframe
    for embed in soup.find_all(['iframe', 'embed', 'object'], src=True):
        src = embed.get('src', '').strip()
        if src.lower().endswith('.pdf'):
            return normalize_url(src, base_url)
    
    return None


def is_valid_pdf_url(url, timeout: int = 10) -> bool:
    """
    ✅ NOUVEAU : Vérifie qu'une URL pointe vers un PDF réellement accessible
    """
    if not url:
        return False
    
    # 1. Vérifier l'extension
    if not url.lower().endswith('.pdf'):
        return False
    
    # 2. Vérifier que l'URL est bien formée
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
    except:
        return False
    
    # 3. Faire un HEAD request pour vérifier l'accessibilité
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
        
        # Vérifier le statut HTTP
        if response.status_code not in [200, 302, 301]:
            return False
        
        # Vérifier le Content-Type (optionnel car certains sites ne le renvoient pas)
        content_type = response.headers.get('Content-Type', '').lower()
        if 'application/pdf' not in content_type and 'application/octet-stream' not in content_type:
            pass  # Certains sites ne renvoient pas le bon Content-Type
        
        return True
    except requests.RequestException as e:
        logger.debug(f"❌ URL PDF invalide {url}: {e}")
        return False


def extract_pdf_from_page(html_content: str, base_url: str) -> str | None:
    """
    ✅ NOUVEAU : Extrait la PREMIÈRE URL PDF valide d'une page HTML
    Priorité aux liens avec texte contenant 'TDR', 'PDF', 'Download', etc.
    """
    if not html_content:
        return None
    
    soup = BeautifulSoup(html_content, 'html.parser')
    pdf_candidates = []
    
    # Keywords qui indiquent un lien vers un document important
    priority_keywords = ['tdr', 'cahier des charges', 'termes de référence', 
                        'document', 'download', 'télécharger', 'pdf', 'file']
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        text = link.get_text().strip().lower()
        
        # Filtrer uniquement les liens PDF
        if href.lower().endswith('.pdf'):
            full_url = urljoin(base_url, href)
            
            # Score de priorité
            score = 0
            for kw in priority_keywords:
                if kw in text or kw in href.lower():
                    score += 10
            
            pdf_candidates.append((score, full_url, text))
    
    # Trier par score décroissant
    pdf_candidates.sort(key=lambda x: x[0], reverse=True)
    
    # Retourner le premier PDF valide
    for score, url, text in pdf_candidates:
        if is_valid_pdf_url(url):
            logger.info(f"✅ PDF valide trouvé: {url[:80]}... (score: {score})")
            return url
    
    # Fallback : retourner le premier PDF même si non validé (optionnel)
    if pdf_candidates:
        logger.warning(f"⚠️ PDF trouvé mais non validé: {pdf_candidates[0][1]}")
        return pdf_candidates[0][1]
    
    return None


def fetch_and_validate_pdf(pdf_url: str, titre: str) -> bytes | None:
    """
    ✅ NOUVEAU : Télécharge et valide le contenu d'un PDF
    Retourne les bytes du PDF ou None si invalide
    """
    if not is_valid_pdf_url(pdf_url):
        return None
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(pdf_url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return None
        
        # Vérifier que c'est bien un PDF (signature magique %PDF-)
        content = response.content
        if not content.startswith(b'%PDF-'):
            logger.warning(f"⚠️ Contenu non-PDF pour {pdf_url}")
            return None
        
        # Vérifier taille minimale (éviter les PDF vides)
        if len(content) < 1024:  # 1KB minimum
            logger.warning(f"⚠️ PDF trop petit: {len(content)} bytes")
            return None
        
        return content
    except Exception as e:
        logger.debug(f"❌ Erreur téléchargement PDF {pdf_url}: {e}")
        return None


# =============================================================================
# FONCTION DE TÉLÉCHARGEMENT PDF (MISE À JOUR)
# =============================================================================
def download_pdf_file(pdf_url, titre, max_retries=3):
    """
    Télécharge un fichier PDF à partir d'une URL - VERSION ROBUSTE
    Gère les redirections, les erreurs, et retourne un ContentFile.
    """
    if not pdf_url:
        return None
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/pdf,application/octet-stream,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'fr,fr-FR;q=0.8,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    for attempt in range(max_retries):
        try:
            logger.debug(f"📥 Téléchargement PDF (tentative {attempt+1}/{max_retries}): {pdf_url[:100]}...")
            
            response = requests.get(pdf_url, headers=headers, timeout=45, allow_redirects=True)
            response.raise_for_status()
            
            content_type = response.headers.get('Content-Type', '').lower()
            content_length = len(response.content)
            
            # Si c'est une page HTML (pas un PDF), essayer d'extraire le lien PDF
            if 'text/html' in content_type:
                logger.debug(f"⚠️ Réponse HTML au lieu de PDF, tentative d'extraction...")
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Chercher un lien PDF dans la page
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if href.lower().endswith('.pdf') or 'download' in href.lower():
                        new_url = normalize_url(href, pdf_url)
                        logger.debug(f"🔄 Nouvelle tentative avec: {new_url}")
                        return download_pdf_file(new_url, titre, max_retries-1)
                
                # Chercher des iframes/embeds
                for embed in soup.find_all(['iframe', 'embed', 'object'], src=True):
                    src = embed.get('src', '')
                    if src.lower().endswith('.pdf'):
                        new_url = normalize_url(src, pdf_url)
                        logger.debug(f"🔄 Nouvelle tentative (embed) avec: {new_url}")
                        return download_pdf_file(new_url, titre, max_retries-1)
                
                logger.warning(f"❌ Aucun PDF trouvé dans la page HTML")
                return None
            
            # Vérifier que c'est bien un PDF
            if 'application/pdf' in content_type or pdf_url.lower().endswith('.pdf'):
                if content_length < 1024:
                    logger.warning(f"⚠️ PDF trop petit ({content_length} bytes), peut-être une erreur")
                    if attempt < max_retries - 1:
                        continue
                
                # Générer un nom de fichier
                safe_title = re.sub(r'[^a-zA-Z0-9]', '_', titre[:50]) if titre else 'document'
                filename = f"{safe_title}_{uuid.uuid4().hex[:8]}.pdf"
                
                logger.info(f"✅ PDF téléchargé: {filename} ({content_length} bytes)")
                return ContentFile(response.content, name=filename)
            else:
                logger.debug(f"⚠️ Content-Type inattendu: {content_type}")
                if attempt < max_retries - 1:
                    continue
                return None
                
        except requests.Timeout:
            logger.warning(f"⏰ Timeout pour {pdf_url}")
            if attempt < max_retries - 1:
                continue
        except requests.RequestException as e:
            logger.warning(f"❌ Erreur requête: {e}")
            if attempt < max_retries - 1:
                continue
        except Exception as e:
            logger.error(f"❌ Erreur inattendue: {e}")
            return None
    
    return None