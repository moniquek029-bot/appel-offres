"""
offres/scraping/parsers/joffres_parser.py
Parser pour Joffres.net - Appels d'offres Burkina Faso
Source : https://www.joffres.net/les_appeloffre/filtre
"""

import logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from ..base import BaseScraper
from ..utils import clean_text
from datetime import date  

logger = logging.getLogger(__name__)

class JoffresParser(BaseScraper):
    """Parser pour joffres.net - Version mock pour démo + template réel."""
    
    def parse(self, soup: BeautifulSoup = None):
        """
        Extrait les offres depuis la page HTML.
        NOTE : Les sélecteurs CSS ci-dessous sont des exemples.
        À adapter après inspection du HTML réel de joffres.net.
        """
        offers = []
        
        # 🎭 MODE MOCK POUR DÉMO (à retirer en production)
        if self.source_url and 'mock' in self.source_url.lower():
            logger.info("🎭 Joffres : mode mock activé pour démo")
            return self._get_mock_offers()
        
        # 🔍 MODE RÉEL : À adapter avec les vrais sélecteurs
        # Exemple de structure à inspecter sur joffres.net :
        # offer_cards = soup.select('div.offer-card, article.appel-offre, .market-item')
        
        offer_cards = []  # ← Remplacer par le vrai sélecteur
        
        for card in offer_cards:
            try:
                # Extraire les données (adaptez les sélecteurs)
                titre = clean_text(card.select_one('h3.titre, h2.title, .offer-title').get_text() or "")
                if not titre:
                    continue
                    
                organisme = clean_text(card.select_one('.organisme, .buyer, .entity').get_text() or "Non spécifié")
                
                # Date de publication (format à adapter)
                date_text = card.select_one('.date, .publication-date, time').get_text() or ""
                date_pub = date.today()                
                # Lien vers le TDR
                lien = card.select_one('a[href*="detail"], a.titre, .btn-detail')
                url_tdr = self._build_absolute_url(lien['href']) if lien and lien.has_attr('href') else self.source_url
                
                offers.append({
                    "titre": titre,
                    "organisme": organisme,
                    "description": clean_text(card.get_text())[:500],
                    "date_publication": date_pub,
                    "date_cloture": date_pub + timedelta(days=30),  # Estimation
                    "url_tdr": url_tdr,
                    "pays": "BF",
                    "source_nom": "Joffres.net"
                })
                
            except Exception as e:
                logger.warning(f"⚠️ Erreur parsing Joffres : {e}")
                continue
        
        logger.info(f"✅ Joffres : {len(offers)} offre(s) extraites")
        return offers
    
    def _get_mock_offers(self):
        """Génère des offres mockées pour la démo."""
        return [
            {
                "titre": "Appel d'offres pour la fourniture de matériel bureautique",
                "organisme": "Ministère de l'Économie et des Finances",
                "description": "Le Ministère lance un appel d'offres pour l'acquisition de matériel informatique et bureautique destiné à l'équipement de ses services centraux et régionaux. La commande porte sur des ordinateurs, imprimantes, scanners et accessoires...",
                "date_publication": datetime.now().date() - timedelta(days=2),
                "date_cloture": datetime.now().date() + timedelta(days=21),
                "url_tdr": "https://www.joffres.net/les_appeloffre/detail/12345",
                "pays": "BF",
                "source_nom": "Joffres.net"
            },
            {
                "titre": "Recrutement d'un cabinet pour audit financier",
                "organisme": "Office National de l'Eau et de l'Assainissement (ONEA)",
                "description": "L'ONEA souhaite recruter un cabinet d'audit indépendant pour la vérification de ses comptes de l'exercice 2025. La mission comprend l'audit de régularité, de sincérité et l'évaluation du contrôle interne...",
                "date_publication": datetime.now().date() - timedelta(days=4),
                "date_cloture": datetime.now().date() + timedelta(days=18),
                "url_tdr": "https://www.joffres.net/les_appeloffre/detail/12346",
                "pays": "BF",
                "source_nom": "Joffres.net"
            }
        ]
    
    def _build_absolute_url(self, relative_url: str) -> str:
        """Convertit une URL relative en URL absolue."""
        if relative_url.startswith('http'):
            return relative_url
        base = "https://www.joffres.net"
        return base + relative_url if relative_url.startswith('/') else f"{base}/{relative_url}"
    
    def run(self):
        """Exécute le scraping complet."""
        logger.info(f"🕷️ Démarrage scraping Joffres: {self.source_url}")
        
        # Pour la démo, on utilise le mock si l'URL contient 'mock'
        if self.source_url and 'mock' in self.source_url.lower():
            return self._get_mock_offers()
        
        soup = self.fetch_and_parse()
        return self.parse(soup) if soup else []