"""
offres/scraping/utils.py
Utilitaires de nettoyage, parsing de dates et archivage automatique.
Utilisé par les tâches Celery et les parsers BeautifulSoup.
"""

import re
from datetime import datetime
from django.utils import timezone
from offres.models import AppelOffre


def clean_text(text: str) -> str:
    """Nettoie le texte HTML, supprime les espaces multiples et sauts de ligne."""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_french_date(date_str: str):
    """Parse les formats de dates français courants (DD/MM/YYYY, YYYY-MM-DD, etc.)."""
    if not date_str:
        return None
    date_str = clean_text(date_str)
    formats = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d %B %Y", "%d %b %Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


def normalize_url(url: str, base_url: str) -> str:
    """Convertit une URL relative en URL absolue."""
    if not url:
        return ""
    if url.startswith("http"):
        return url
    return f"{base_url.rstrip('/')}/{url.lstrip('/')}"


def archive_expired_offres():
    """
     Archive automatiquement les offres dont la date de clôture est dépassée.
    Appelée quotidiennement par Celery Beat.
    """
    today = timezone.now().date()
    # Change le statut de "Ouvert" à "Clôturé" pour les offres expirées
    count = AppelOffre.objects.filter(statut="Ouvert", date_cloture__lt=today).update(statut="Clôturé")
    print(f" {count} offres archivées automatiquement (date de clôture dépassée).")
    return count

