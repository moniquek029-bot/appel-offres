"""
offres/scraping/parsers/joffres_parser.py
Parser pour Joffres.net - Appels d'offres Burkina Faso
Source : https://www.joffres.net/les_appeloffre/filtre
"""

import logging
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from ..base import BaseScraper
from ..utils import clean_text

logger = logging.getLogger(__name__)

class JoffresParser(BaseScraper):
    """Parser pour joffres.net - Version mock pour démo + template réel."""
    
    def fetch_and_parse(self):
        """ Télécharge la page HTML et retourne un objet BeautifulSoup."""
        try:
            logger.info(f"Téléchargement de {self.source_url}")
            # Headers pour simuler un navigateur réel et éviter les blocages
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.source_url, headers=headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logger.error(f"❌ Erreur de téléchargement : {e}")
            return None
    
    def parse(self, soup: BeautifulSoup = None):
        """Extrait les offres depuis la page HTML."""
        offers = []
        
        # 🎭 MODE MOCK POUR DÉMO
        if self.source_url and 'mock' in self.source_url.lower():
            logger.info("🎭 Joffres : mode mock activé")
            return self._get_mock_offers()
        
        # 🔍 MODE RÉEL : Sélecteurs à adapter selon le site
        offer_cards = []  # Remplacez par : soup.select('div.offer-card') etc.
        
        for card in offer_cards:
            try:
                titre = clean_text(card.select_one('h3.titre') and card.select_one('h3.titre').get_text() or "")
                if not titre: continue
                
                offers.append({
                    "titre": titre,
                    "organisme": clean_text(card.select_one('.organisme') and card.select_one('.organisme').get_text() or "Non spécifié"),
                    "description": clean_text(card.get_text())[:500],
                    "date_publication": datetime.now().date(),
                    "date_cloture": datetime.now().date() + timedelta(days=30),
                    "url_tdr": self._build_absolute_url(card.select_one('a').get('href', '')),
                    "pays": "BF",
                    "source_nom": "Joffres.net"
                })
            except Exception as e:
                logger.warning(f"⚠️ Erreur parsing carte : {e}")
                continue
        
        logger.info(f"✅ Joffres : {len(offers)} offre(s) extraites")
        return offers
    
    def _get_mock_offers(self):
        """Génère des offres mockées avec URLs uniques."""
        import uuid
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        return [
            {
                "titre": "Appel d'offres pour la fourniture de matériel bureautique",
                "organisme": "Ministère de l'Économie et des Finances",
                "description": "Le Ministère lance un appel d'offres pour l'acquisition de matériel informatique et bureautique destiné à l'équipement de ses services centraux et régionaux...",
                "date_publication": datetime.now().date() - timedelta(days=2),
                "date_cloture": datetime.now().date() + timedelta(days=21),
                "url_tdr": f"https://www.joffres.net/les_appeloffre/detail/{timestamp}-{unique_id}",
                "pays": "BF",
                "source_nom": "Joffres.net"
            },
            {
                "titre": "Recrutement d'un cabinet pour audit financier",
                "organisme": "ONEA",
                "description": "L'ONEA souhaite recruter un cabinet d'audit indépendant pour la vérification de ses comptes...",
                "date_publication": datetime.now().date() - timedelta(days=4),
                "date_cloture": datetime.now().date() + timedelta(days=18),
                "url_tdr": f"https://www.joffres.net/les_appeloffre/detail/{timestamp}-{unique_id}-audit",
                "pays": "BF",
                "source_nom": "Joffres.net"
            }
        ]
    
    def _build_absolute_url(self, relative_url: str) -> str:
        """Convertit une URL relative en URL absolue."""
        if not relative_url or relative_url.startswith('http'):
            return relative_url or self.source_url
        base = "https://www.joffres.net"
        return f"{base}{relative_url}" if relative_url.startswith('/') else f"{base}/{relative_url}"
    
    def run(self):
        """Exécute le scraping complet."""
        logger.info(f"🕷️ Démarrage scraping Joffres: {self.source_url}")
        
        # Pour la démo, on utilise le mock si l'URL contient 'mock'
        if self.source_url and 'mock' in self.source_url.lower():
            return self._get_mock_offers()
        
        soup = self.fetch_and_parse()
        return self.parse(soup) if soup else []