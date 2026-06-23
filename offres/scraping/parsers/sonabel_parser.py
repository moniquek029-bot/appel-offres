# offres/scraping/parsers/sonabel_parser.py
from bs4 import BeautifulSoup
from datetime import date, timedelta
import logging
import re

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url

logger = logging.getLogger(__name__)

class SONABELParser(BaseScraper):
    """Parser SONABEL pour extraire les appels d'offres"""
    
    def __init__(self, source_url: str, base_url: str = "https://www.sonabel.bf", pays_defaut: str = 'BF', **kwargs):
        super().__init__(source_url, delay_seconds=2, base_url=base_url, pays_defaut=pays_defaut, **kwargs)
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        offres = []
        
        # Mots-clés pour identifier les appels d'offres
        keywords = ['appel', 'offre', 'marché', 'avis', 'tender', 'consultant']
        
        # Chercher tous les liens contenant des mots-clés d'offres
        for link in soup.find_all('a', href=True):
            titre = clean_text(link.get_text(strip=True))
            href = link['href']
            
            # Filtrer les liens pertinents
            if len(titre) < 20:
                continue
            if not any(kw in titre.lower() for kw in keywords):
                continue
            if href in ['#', '/']:
                continue
            
            url_source = normalize_url(href, self.base_url)
            
            offre = {
                'titre': titre[:300],
                'organisme': "SONABEL",
                'description': titre,
                'date_publication': date.today() - timedelta(days=5),
                'date_cloture': date.today() + timedelta(days=30),
                'url_source': url_source,
                'url_tdr': None,
                'pays': self.pays_defaut,
                'statut': 'Ouvert',
                'mode_acquisition': 'AUTO',
            }
            
            # Éviter les doublons
            if not any(o['url_source'] == url_source for o in offres):
                offres.append(offre)
        
        logger.info(f"✅ SONABEL: {len(offres)} offre(s) extraite(s)")
        return offres[:30]
    
    def run(self) -> list[dict]:
        logger.info(f"🕷️ SONABEL scraping: {self.source_url}")
        try:
            soup = self.fetch_and_parse(use_js=False)
            if not soup:
                return []
            return self.parse(soup)
        except Exception as e:
            logger.error(f"❌ Erreur SONABEL: {e}")
            return []