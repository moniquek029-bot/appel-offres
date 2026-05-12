"""
offres/scraping/parsers/template.py
Parser générique de secours pour le scraping.
Utilisé quand aucun parser spécifique n'est configuré pour une URL.
 Retourne une liste vide par défaut - à remplacer par un parser dédié en production.
"""

from ..base import BaseScraper
from ..utils import clean_text, parse_french_date, normalize_url
import logging

logger = logging.getLogger(__name__)

class TemplateSiteParser(BaseScraper):
    """
    Parser générique qui hérite de BaseScraper.
     Par défaut, retourne une liste vide pour éviter d'insérer des données incorrectes.
    À remplacer par un parser dédié pour chaque site en production.
    """
    
    def parse(self, soup):
        """
        Extraction basique - retourne toujours une liste vide par défaut.
        Surchargez cette méthode dans un parser dédié pour extraire les données réelles.
        """
        logger.warning(f" TemplateSiteParser utilisé pour {self.source_url}")
        logger.info(" Créez un parser dédié dans offres/scraping/parsers/ pour ce site.")
        
        # Retourne vide pour éviter d'insérer des données incorrectes
        return []