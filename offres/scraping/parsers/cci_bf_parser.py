"""
offres/scraping/parsers/cci_bf_parser.py
Parser pour CCI-BF - Chambre de Commerce et d'Industrie du Burkina Faso
Source : https://www.cci-bf.net ou URL des appels d'offres
"""

import logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from ..base import BaseScraper
from ..utils import clean_text
from datetime import date  

logger = logging.getLogger(__name__)

class CCIBFParser(BaseScraper):
    """Parser pour CCI-BF - Version mock + template réel."""
    
    def parse(self, soup: BeautifulSoup = None):
        """Extrait les offres depuis la page HTML."""
        offers = []
        
        # 🎭 MODE MOCK POUR DÉMO
        if self.source_url and 'mock' in self.source_url.lower():
            logger.info("🎭 CCI-BF : mode mock activé")
            return self._get_mock_offers()
        
        # 🔍 MODE RÉEL : À adapter
        # Exemple : offer_cards = soup.select('div.annonce, .marche-public, article.appel-offre')
        
        offer_cards = []  # ← Remplacer par le vrai sélecteur
        
        for card in offer_cards:
            try:
                titre = clean_text(card.select_one('h2, h3.titre, .offer-title').get_text() or "")
                if not titre:
                    continue
                
                offers.append({
                    "titre": titre,
                    "organisme": "CCI-BF - Chambre de Commerce et d'Industrie du Burkina Faso",
                    "description": clean_text(card.get_text())[:500],
                    "date_publication": datetime.now().date(),
                    "date_cloture": datetime.now().date() + timedelta(days=28),
                    "url_tdr": self._build_url(card.select_one('a').get('href', '')),
                    "pays": "BF",
                    "source_nom": "CCI-BF"
                })
            except Exception as e:
                logger.warning(f"⚠️ Erreur parsing CCI-BF : {e}")
                continue
        
        return offers
    
    def _get_mock_offers(self):
        """Offres mockées pour la démo."""
        return [
            {
                "titre": "Accompagnement des PME dans la digitalisation de leurs processus",
                "organisme": "CCI-BF - Chambre de Commerce et d'Industrie du Burkina Faso",
                "description": "La CCI-BF lance un appel à manifestation d'intérêt pour le recrutement d'un cabinet spécialisé dans l'accompagnement des PME/PMI burkinabè vers la transformation digitale. La mission inclut l'audit, la formation et le déploiement d'outils...",
                "date_publication": datetime.now().date() - timedelta(days=3),
                "date_cloture": datetime.now().date() + timedelta(days=24),
                "url_tdr": "https://www.cci-bf.net/appels-offres/detail/digitalisation-pme-2026",
                "pays": "BF",
                "source_nom": "CCI-BF"
            }
        ]
    
    def _build_url(self, rel: str) -> str:
        base = "https://www.cci-bf.net"
        return rel if rel.startswith('http') else f"{base}{rel}"
    
    def run(self):
        logger.info(f"🕷️ Scraping CCI-BF: {self.source_url}")
        if self.source_url and 'mock' in self.source_url.lower():
            return self._get_mock_offers()
        soup = self.fetch_and_parse()
        return self.parse(soup) if soup else []