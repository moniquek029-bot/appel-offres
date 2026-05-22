# offres/scraping/utils.py
import re
from datetime import date, datetime
import logging

logger = logging.getLogger(__name__)

def clean_text(text):
    """
    Nettoie une chaîne de caractères (supprime les balises HTML, espaces superflus)
    ✅ CORRIGÉ : Gère les objets date/datetime
    """
    # ✅ Si c'est déjà une date ou datetime, la convertir en string
    if isinstance(text, (date, datetime)):
        return text.strftime('%Y-%m-%d')
    
    # Si ce n'est pas une chaîne, retourner une chaîne vide
    if not isinstance(text, str):
        return str(text) if text else ''
    
    # Supprimer les balises HTML
    text = re.sub(r'<[^>]+>', '', text)
    # Supprimer les espaces multiples
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def parse_french_date(date_str, default_days=30):
    """
    Convertit une date française (JJ/MM/AAAA) en objet date
    ✅ CORRIGÉ : Gère les objets date/datetime en entrée
    """
    from django.utils import timezone
    
    # ✅ Si c'est déjà une date ou datetime, la retourner
    if isinstance(date_str, (date, datetime)):
        return date_str.date() if isinstance(date_str, datetime) else date_str
    
    # Si c'est None ou vide, retourner date par défaut
    if not date_str:
        return (timezone.now() + timezone.timedelta(days=default_days)).date()
    
    # Si ce n'est pas une chaîne, essayer de convertir
    if not isinstance(date_str, str):
        try:
            return date_str.date() if hasattr(date_str, 'date') else date_str
        except:
            return (timezone.now() + timezone.timedelta(days=default_days)).date()
    
    # Nettoyer la chaîne
    date_str = clean_text(date_str)
    
    # Patterns de dates françaises
    patterns = [
        r'(\d{2})[/\-](\d{2})[/\-](\d{4})',  # DD/MM/YYYY ou DD-MM-YYYY
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
                # Vérifier le format
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
    
    # Date par défaut
    return (timezone.now() + timezone.timedelta(days=default_days)).date()


def normalize_url(url, base_url):
    """Normalise une URL (relative → absolue)"""
    from urllib.parse import urljoin
    
    if not url:
        return None
    
    # Si l'URL est déjà complète
    if url.startswith('http://') or url.startswith('https://'):
        return url
    
    # Sinon, joindre avec l'URL de base
    return urljoin(base_url, url)


def archive_expired_offres():
    """Archive les offres dont la date de clôture est dépassée"""
    from offres.models import AppelOffre
    from django.utils import timezone
    
    expired = AppelOffre.objects.filter(
        date_cloture__lt=timezone.now().date(),
        statut='Ouvert'
    )
    count = expired.count()
    expired.update(statut='Expiré')
    return count