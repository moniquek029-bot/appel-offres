"""
offres/scraping/parsers/agetib_parser.py
Parser pour Agetib.net - Agence d'Exécution des Travaux d'Intérêt Public
Source : https://www.agetib.net (ou URL réelle des appels d'offres)
"""

import logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from ..base import BaseScraper
from ..utils import clean_text
from datetime import date  # 

logger = logging.getLogger(__name__)

class AgetibParser(BaseScraper):
    """Parser pour agetib.net - Version mock + template réel."""
    
    def parse(self, soup: BeautifulSoup = None):
        """Extrait les offres depuis la page HTML."""
        offers = []
        
        # 🎭 MODE MOCK POUR DÉMO
        if self.source_url and 'mock' in self.source_url.lower():
            logger.info("🎭 Agetib : mode mock activé")
            return self._get_mock_offers()
        
        # 🔍 MODE RÉEL : À adapter avec les vrais sélecteurs
        # Inspecter le HTML de agetib.net pour trouver les bons sélecteurs
        # Exemple : offer_cards = soup.select('div.tender, article.market, .appel-offre')
        
        offer_cards = []  # ← Remplacer par le vrai sélecteur
        
        for card in offer_cards:
            try:
                titre = clean_text(card.select_one('h3, h4.title, .titre-ao').get_text() or "")
                if not titre:
                    continue
                
                offers.append({
                    "titre": titre,
                    "organisme": "AGETIB - Agence d'Exécution des Travaux d'Intérêt Public",
                    "description": clean_text(card.get_text())[:500],
                    "date_publication": date.today(),
                    "date_cloture": date.today() + timedelta(days=25),
                    "url_tdr": self._build_url(card.select_one('a').get('href', '')),
                    "pays": "BF",
                    "source_nom": "Agetib.net"
                })
            except Exception as e:
                logger.warning(f"⚠️ Erreur parsing Agetib : {e}")
                continue
        
        return offers
    
    def _get_mock_offers(self):
        """Offres mockées pour la démo."""
        return [
            {
                "titre": "Travaux de réhabilitation de voiries urbaines à Ouagadougou",
                "organisme": "AGETIB - Agence d'Exécution des Travaux d'Intérêt Public",
                "description": "L'AGETIB lance un appel d'offres pour les travaux de réhabilitation de voiries dans les communes de Ouagadougou. Le projet comprend le reprofilage, le drainage et la signalisation sur un linéaire de 15 km...",
                "date_publication": datetime.now().date() - timedelta(days=1),
                "date_cloture": datetime.now().date() + timedelta(days=22),
                "url_tdr": "https://www.agetib.net/appels-offres/detail/voirie-ouaga-2026",
                "pays": "BF",
                "source_nom": "Agetib.net"
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