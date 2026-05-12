"""
offres/scraping/parsers/globaltenders_parser.py
Parser pour GlobalTenders - Plateforme internationale d'appels d'offres
Source : https://www.globaltenders.com
"""
import logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from ..base import BaseScraper
from ..utils import clean_text

logger = logging.getLogger(__name__)

class GlobalTendersParser(BaseScraper):
    """Parser pour GlobalTenders - Version mock pour démo."""

    def parse(self, soup: BeautifulSoup = None):
        # 🎭 MODE MOCK POUR DÉMO
        if self.source_url and 'mock' in self.source_url.lower():
            logger.info("🎭 GlobalTenders : mode mock activé")
            return self._get_mock_offers()

        # 🔍 MODE RÉEL : À adapter avec les vrais sélecteurs
        # GlobalTenders utilise souvent du contenu dynamique ou une API interne
        # Exemple : offer_cards = soup.select('div.tender-item, tr.tender-row, .search-result')
        offer_cards = []  # ← Remplacer par le vrai sélecteur après inspection HTML

        offers = []
        for card in offer_cards:
            try:
                titre = clean_text(card.select_one('h3, .tender-title, a.title') and card.select_one('h3, .tender-title, a.title').get_text() or "")
                if not titre: continue

                offers.append({
                    "titre": titre,
                    "organisme": clean_text(card.select_one('.buyer, .organization, .agency') and card.select_one('.buyer, .organization, .agency').get_text() or "Non spécifié"),
                    "description": clean_text(card.get_text())[:500],
                    "date_publication": datetime.now().date(),
                    "date_cloture": datetime.now().date() + timedelta(days=30),
                    "url_tdr": self._build_url(card.select_one('a').get('href', '')),
                    "pays": "BF",  # Ou extraire dynamiquement si disponible
                    "source_nom": "GlobalTenders"
                })
            except Exception as e:
                logger.warning(f"⚠️ Erreur parsing GlobalTenders : {e}")
        return offers

    def _get_mock_offers(self):
        """Offres mockées pour la démo."""
        return [
            {
                "titre": "International Consulting Services for Infrastructure Development",
                "organisme": "African Development Bank (AfDB)",
                "description": "The African Development Bank invites proposals from qualified consulting firms for technical assistance in infrastructure planning and sustainable development across West Africa. The mission includes feasibility studies, environmental impact assessments, and capacity building for local authorities...",
                "date_publication": datetime.now().date() - timedelta(days=2),
                "date_cloture": datetime.now().date() + timedelta(days=28),
                "url_tdr": "https://www.globaltenders.com/tenders/123456",
                "pays": "BF",
                "source_nom": "GlobalTenders"
            },
            {
                "titre": "Supply and Installation of Solar Power Systems for Rural Clinics",
                "organisme": "UNDP Burkina Faso",
                "description": "UNDP seeks experienced contractors for the turnkey supply, installation, and commissioning of off-grid solar photovoltaic systems in 15 rural health centers. The project aims to improve healthcare delivery through reliable electricity access...",
                "date_publication": datetime.now().date() - timedelta(days=4),
                "date_cloture": datetime.now().date() + timedelta(days=21),
                "url_tdr": "https://www.globaltenders.com/tenders/123457",
                "pays": "BF",
                "source_nom": "GlobalTenders"
            }
        ]

    def _build_url(self, rel: str) -> str:
        base = "https://www.globaltenders.com"
        return rel if rel.startswith('http') else f"{base}{rel}"

    def run(self):
        logger.info(f"🕷️ Scraping GlobalTenders: {self.source_url}")
        if self.source_url and 'mock' in self.source_url.lower():
            return self._get_mock_offers()
        soup = self.fetch_and_parse()
        return self.parse(soup) if soup else []