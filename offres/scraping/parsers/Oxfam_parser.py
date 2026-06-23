# offres/scraping/parsers/oxfam_parser.py
from offres.scraping.base import BaseScraper
import logging

logger = logging.getLogger(__name__)

class OxfamParser(BaseScraper):
    def __init__(self, source_url, **kwargs):
        super().__init__(source_url, **kwargs)
    
    def run(self):
        soup = self.fetch_and_parse()
        if not soup:
            return []
        
        offers = []
        # ... ta logique de scraping spécifique
        
        return offers