# offres/scraping/parsers/globaltenders_parser.py

import logging
from datetime import datetime, timedelta, date
from ..base import BaseScraper
from ..utils import clean_text

logger = logging.getLogger(__name__)

class GlobalTendersParser(BaseScraper):
    """Parser pour GlobalTenders"""
    
    # ✅ Ajouter cette méthode pour ignorer robots.txt en mode mock
    def is_allowed(self, url):
        """Contourne robots.txt pour le mode mock"""
        if 'mock' in self.source_url.lower():
            return True
        return super().is_allowed(url)
    
    def parse(self, soup=None):
        offers = []
        
        # Mode mock pour démo
        if self.source_url and 'mock' in self.source_url.lower():
            logger.info("🎭 GlobalTenders : mode mock activé")
            return self._get_mock_offers()
        
        # Mode réel (à adapter)
        return offers
    
    def _get_mock_offers(self):
        """Offres mockées"""
        import uuid
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        return [
            {
                "titre": "International Consulting Services for Infrastructure",
                "organisme": "African Development Bank (AfDB)",
                "description": "The African Development Bank invites proposals...",
                "date_publication": date.today() - timedelta(days=2),
                "date_cloture": date.today() + timedelta(days=28),
                "url_tdr": f"https://www.globaltenders.com/tenders/{timestamp}-{unique_id}",
                "pays": "INT",
            },
            {
                "titre": "Supply of Medical Equipment to Regional Hospitals",
                "organisme": "WHO Burkina Faso",
                "description": "Supply and delivery of medical equipment...",
                "date_publication": date.today() - timedelta(days=1),
                "date_cloture": date.today() + timedelta(days=21),
                "url_tdr": f"https://www.globaltenders.com/tenders/{timestamp}-{unique_id}-medical",
                "pays": "BF",
            }
        ]
    
    def run(self):
        logger.info(f"🕷️ Scraping GlobalTenders: {self.source_url}")
        if self.source_url and 'mock' in self.source_url.lower():
            return self._get_mock_offers()
        return []