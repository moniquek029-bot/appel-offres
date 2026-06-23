# offres/scraping/parsers/joffres_parser.py
from bs4 import BeautifulSoup
from datetime import date, timedelta
import logging
import re

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url

logger = logging.getLogger(__name__)

class JoffresParser(BaseScraper):
    """Parser JOFFRES avec sélecteurs larges"""
    
    def __init__(self, source_url: str, base_url: str = "https://www.joffres.net", pays_defaut: str = 'BF', **kwargs):
        super().__init__(source_url, delay_seconds=3, base_url=base_url, pays_defaut=pays_defaut, **kwargs)
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        offres = []
        
        # Chercher tous les liens contenant des mots-clés d'offres
        keywords = ['appel', 'offre', 'marché', 'tender', 'avis']
        
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

            pays = detecter_pays(titre, self.pays_defaut)
            
            offre = {
                'titre': titre[:300],
                'organisme': "JOFFRES",
                'description': titre,
                'date_publication': date.today() - timedelta(days=2),
                'date_cloture': date.today() + timedelta(days=30),
                'url_source': url_source,
                'url_tdr': None,
                'pays':pays,
                'statut': 'Ouvert',
                'mode_acquisition': 'AUTO',
            }
            
            if not any(o['url_source'] == url_source for o in offres):
                offres.append(offre)
        
        logger.info(f"✅ JOFFRES: {len(offres)} offre(s) extraite(s)")
        return offres[:30]
    
    def run(self) -> list[dict]:
        logger.info(f"🕷️ JOFFRES scraping: {self.source_url}")
        try:
            soup = self.fetch_and_parse(use_js=False)  # ← ESSAYER SANS JS D'ABORD
            if not soup:
                return []
            return self.parse(soup)
        except Exception as e:
            logger.error(f"❌ Erreur JOFFRES: {e}")
            return []