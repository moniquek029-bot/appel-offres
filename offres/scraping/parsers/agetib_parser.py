# offres/scraping/parsers/agetib_parser.py
import logging
from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup
from ..base import BaseScraper
from ..utils import clean_text, parse_french_date

logger = logging.getLogger(__name__)

class AgetibParser(BaseScraper):
    """Parser pour agetib.net"""
    
    def parse(self, soup: BeautifulSoup = None):
        """Extrait les offres depuis la page HTML."""
        offers = []
        
        # MODE MOCK POUR DÉMO
        if self.source_url and 'mock' in self.source_url.lower():
            logger.info("🎭 Agetib : mode mock activé")
            return self._get_mock_offers()
        
        # MODE RÉEL
        offer_cards = []  # À remplacer par les vrais sélecteurs
        
        for card in offer_cards:
            try:
                titre = clean_text(card.select_one('h3, h4.title, .titre-ao').get_text() or "")
                if not titre:
                    continue
                
                offers.append({
                    "titre": titre,
                    "organisme": "AGETIB - Agence d'Exécution des Travaux d'Intérêt Public",
                    "description": clean_text(card.get_text())[:500],
                    "date_publication": date.today(),  # ✅ Utilisation correcte de date.today()
                    "date_cloture": date.today() + timedelta(days=25),
                    "url_tdr": self._build_url(card.select_one('a').get('href', '')),
                    "pays": "BF",
                })
            except Exception as e:
                logger.warning(f"⚠️ Erreur parsing Agetib : {e}")
                continue
        
        return offers
    
    def _get_mock_offers(self):
        """Offres mockées avec URLs uniques."""
        import uuid
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        return [
            {
                "titre": "Travaux de réhabilitation de voiries urbaines à Ouagadougou",
                "organisme": "AGETIB - Agence d'Exécution des Travaux d'Intérêt Public",
                "description": "L'AGETIB lance un appel d'offres pour les travaux de réhabilitation de voiries...",
                "date_publication": date.today() - timedelta(days=1),  # ✅ date.today() au lieu de datetime.now().date()
                "date_cloture": date.today() + timedelta(days=22),
                "url_tdr": f"https://www.agetib.net/appels-offres/detail/voirie-{timestamp}-{unique_id}",
                "pays": "BF",
            }
        ]
    
    def _build_url(self, rel: str) -> str:
        base = "https://www.agetib.net"
        return rel if rel.startswith('http') else f"{base}{rel}"
    
    def run(self):
        logger.info(f"🕷️ Scraping Agetib: {self.source_url}")
        if self.source_url and 'mock' in self.source_url.lower():
            return self._get_mock_offers()
        soup = self.fetch_and_parse()
        return self.parse(soup) if soup else []