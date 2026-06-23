# offres/scraping/parsers/__init__.py

"""
Package de parsers pour le scraping d'offres
"""

# ✅ Export explicite des classes disponibles
from .smart_parser import SmartParser  # ← ADAPTE LE NOM DU FICHIER SI NÉCESSAIRE

# Si tu as d'autres parsers, ajoute-les ici :
# from .unfpa_parser import UnfpaParser
# from .agetib_parser import AgetibParser

__all__ = [
    'SmartParser',
    # 'UnfpaParser',
    # 'AgetibParser',
]