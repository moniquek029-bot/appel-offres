# offres/scraping/constantes.py
"""
Constantes partagées entre frontend et backend
Ce fichier est un simple wrapper qui importe depuis le fichier centralisé
"""

# ✅ Importer uniquement ce qui existe dans search_keywords.py
from offres.utils.search_keywords import (
    DOMAINES_STANDARDS,
    MOTS_CLES_DOMAINES,
    COUNTRIES,
    detecter_domaine,
    get_domain_keywords,
    get_country_codes,
)

# ✅ Réexporter pour compatibilité
__all__ = [
    'DOMAINES_STANDARDS',
    'MOTS_CLES_DOMAINES',
    'COUNTRIES',
    'detecter_domaine',
    'get_domain_keywords',
    'get_country_codes',
]