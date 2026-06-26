# offres/scraping/utils.py
# Fonctions utilitaires pour le scraping - VERSION OPTIMISÉE SÉCURISÉE
# offres/scraping/utils.py

import re
from datetime import date, datetime
import logging
import requests
import uuid
from django.core.files.base import ContentFile
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# ==================== DÉTECTION AUTOMATIQUE DE PAYS ====================
PAYS_AFRICAINS = {
    'burkina faso': 'BF', 'burkina': 'BF', 'bf': 'BF', 'ouagadougou': 'BF',
    'mali': 'ML', 'ml': 'ML', 'bamako': 'ML',
    'niger': 'NE', 'ne': 'NE', 'niamey': 'NE',
    'sénégal': 'SN', 'senegal': 'SN', 'sn': 'SN', 'dakar': 'SN',
    'côte d\'ivoire': 'CI', 'cote d\'ivoire': 'CI', 'ci': 'CI', 'abidjan': 'CI',
    'guinée': 'GN', 'guinea': 'GN', 'gn': 'GN',
    'togo': 'TG', 'tg': 'TG',
    'bénin': 'BJ', 'benin': 'BJ', 'bj': 'BJ',
    'ghana': 'GH', 'gh': 'GH',
    'cameroun': 'CM', 'cameroon': 'CM', 'cm': 'CM',
    'tchad': 'TD', 'chad': 'TD',
    'nigeria': 'NG', 'ng': 'NG',
    'kenya': 'KE', 'ke': 'KE',
    'rdc': 'CD', 'congo': 'CD',
    'afrique de l\'ouest': 'AO', 'west africa': 'AO',
    'afrique': 'AF', 'africa': 'AF',
    'global': 'GL', 'international': 'GL', 'multiple': 'GL', 'mondial': 'GL',
}

def detecter_pays(texte: str, pays_defaut: str = 'BF') -> str:
    """
    Détecte le pays dans un texte (titre ou description).
    Retourne le code pays ISO ou le pays par défaut.
    """
    if not texte:
        return pays_defaut
    
    texte_lower = texte.lower()
    
    # Trier par longueur décroissante pour éviter les faux positifs
    pays_tries = sorted(PAYS_AFRICAINS.items(), key=lambda x: len(x[0]), reverse=True)
    
    for nom_pays, code in pays_tries:
        pattern = r'\b' + re.escape(nom_pays) + r'\b'
        if re.search(pattern, texte_lower):
            logger.debug(f" Pays détecté: '{nom_pays}' → {code}")
            return code
    
    return pays_defaut

# ... reste du fichier (clean_text, parse_french_date, etc.)

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


def is_valid_pdf_url(url, timeout: int = 10) -> bool:
    """
    Vérifie l'accessibilité d'une URL.
    CORRECTION : N'exclut plus les fichiers sans l'extension explicite '.pdf'
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
    except:
        return False
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        # Utilisation de HEAD pour économiser de la bande passante
        response = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
        
        if response.status_code in [200, 301, 302]:
            return True
        
        # Fallback si HEAD est bloqué par le serveur (fréquent)
        fallback = requests.get(url, headers=headers, timeout=timeout, stream=True)
        return fallback.status_code == 200
    except requests.RequestException as e:
        logger.debug(f" URL inaccessible {url}: {e}")
        return False


def extract_pdf_from_page(html_content: str, base_url: str) -> str | None:
    """
    Extrait une URL de document potentielle d'une page HTML.
    CORRECTION : Inclus les liens de téléchargement dynamiques basés sur les mots-clés.
    """
    if not html_content:
        return None
    
    soup = BeautifulSoup(html_content, 'html.parser')
    pdf_candidates = []
    
    priority_keywords = ['tdr', 'cahier des charges', 'termes de référence', 
                         'document', 'download', 'télécharger', 'pdf', 'file', 'notice']
    
    for link in soup.find_all('a', href=True):
        href = link['href'].strip()
        if not href or href.startswith('#') or href.startswith('javascript:'):
            continue
            
        text = link.get_text().strip().lower()
        full_url = normalize_url(href, base_url)
        
        score = 0
        # Condition d'acceptation élargie : extension .pdf OU mot-clé fort dans le texte/lien
        is_pdf_extension = href.lower().endswith('.pdf')
        has_keyword = any(kw in text or kw in href.lower() for kw in priority_keywords)
        
        if is_pdf_extension or has_keyword:
            if is_pdf_extension:
                score += 20
            if has_keyword:
                score += 15
                
            pdf_candidates.append((score, full_url))
    
    # Trier par score de pertinence
    pdf_candidates.sort(key=lambda x: x[0], reverse=True)
    
    # Valider et renvoyer la meilleure URL valide au sens réseau
    for score, url in pdf_candidates:
        if is_valid_pdf_url(url):
            return url
            
    return None


def fetch_and_validate_pdf(pdf_url: str, titre: str) -> bytes | None:
    """
    Télécharge et valide la signature magique du flux binaire.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(pdf_url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return None
        
        content = response.content
        
        #  VALIDATION ABSOLUE : Vérification du conteneur binaire
        if not content.startswith(b'%PDF-'):
            logger.warning(f" Flux binaire non-PDF détecté pour l'URL: {pdf_url}")
            return None
        
        if len(content) < 1024:  # Moins de 1 Ko = Fichier corrompu ou vide
            logger.warning(f" Fichier PDF anormalement petit ({len(content)} octets)")
            return None
            
        return content
    except Exception as e:
        logger.debug(f" Échec de la lecture du flux PDF {pdf_url}: {e}")
        return None


def download_pdf_file(pdf_url, titre, max_retries=3):
    """
    Télécharge un fichier et l'encapsule dans un objet de fichier Django ContentFile.
    """
    if not pdf_url:
        return None
        
    content = fetch_and_validate_pdf(pdf_url, titre)
    if content:
        safe_title = re.sub(r'[^a-zA-Z0-9]', '_', titre[:50]) if titre else 'document'
        filename = f"{safe_title}_{uuid.uuid4().hex[:8]}.pdf"
        return ContentFile(content, name=filename)
        
    return None


def get_first_pdf_url(soup, base_url):
    """Alias de compatibilité pour éviter de casser les anciens parsers"""
    if not soup:
        return None
    # On passe la string HTML brute à la nouvelle fonction robuste
    return extract_pdf_from_page(str(soup), base_url)



#Archivage et suprression
# =============================================================================
# CYCLE DE VIE ET PURGE AUTOMATIQUE DES OFFRES
# =============================================================================

def archive_and_delete_old_offres(days_to_keep=30):
    """
    1. Oriente les offres fraîches vers le statut 'Expiré' via la fonction native.
    2. Identifie et supprime les offres déjà marquées comme 'Expiré' depuis plus de X jours.
    Libère l'espace sur la base de données et supprime les fichiers physiques (PDF).
    """
    from offres.models import AppelOffre
    from django.utils import timezone
    
    # Étape 1 : Exécuter l'archivage standard existant
    try:
        archived_count = archive_expired_offres()
        if archived_count > 0:
            logger.info(f" {archived_count} nouvelles offres sont passées au statut Expiré.")
    except Exception as e:
        logger.error(f"Erreur lors de l'archivage automatique : {e}")
        archived_count = 0

    # Étape 2 : Purge et suppression définitive pour libérer l'espace
    date_limite = timezone.now().date() - timezone.timedelta(days=days_to_keep)
    
    # Cibler les offres déjà expirées dont la date de clôture dépasse le seuil de rétention
    offres_a_supprimer = AppelOffre.objects.filter(
        statut='Expiré', 
        date_cloture__lt=date_limite
    )
    
    deleted_count = offres_a_supprimer.count()
    
    if deleted_count > 0:
        for offre in offres_a_supprimer:
            if offre.fichier_pdf:
                try:
                    offre.fichier_pdf.delete(save=False)
                except Exception as e:
                    logger.error(f"Impossible de détruire le fichier PDF physique pour l'offre {offre.id} : {e}")
        
        # Effacement définitif en BDD
        offres_a_supprimer.delete()
        logger.info(f" Nettoyage de l'espace disque accompli : {deleted_count} anciennes offres purgées.")
    else:
        logger.info("Aucune ancienne offre expirée ne nécessite de purge aujourd'hui.")

    return archived_count, deleted_count