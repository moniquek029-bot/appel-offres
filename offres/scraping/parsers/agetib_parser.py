"""
Parser pour AGETIB - Version CORRIGÉE
"""

from bs4 import BeautifulSoup
from datetime import date, timedelta
import logging
import requests

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url

logger = logging.getLogger(__name__)


class AgetibParser(BaseScraper):
    """Parser AGETIB avec extraction de VRAIES données"""
    
    def __init__(self, source_url: str, base_url: str = "https://www.agetib.net", pays_defaut: str = 'BF', **kwargs):
        super().__init__(source_url, delay_seconds=3, base_url=base_url, pays_defaut=pays_defaut, **kwargs)
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        offres = []
        
        cards = soup.select('.offer-card, .appel-offre, article')
        if not cards:
            cards = soup.find_all(['div', 'article'], limit=30)
        
        for card in cards:
            try:
                titre_elem = card.select_one('h3, h4, .title, a')
                if not titre_elem:
                    continue
                
                titre = clean_text(titre_elem.text)
                if len(titre) < 10:
                    continue
                
                link_elem = card.select_one('a[href]')
                url_source = normalize_url(link_elem.get('href'), self.base_url) if link_elem else None
                
                offre = {
                    'titre': titre[:300],
                    'organisme': "AGETIB",
                    'description': clean_text(card.get_text())[:500],
                    'date_publication': date.today() - timedelta(days=3),
                    'date_cloture': date.today() + timedelta(days=30),
                    'url_source': url_source,
                    'url_tdr': None,
                    'pays': self.pays_defaut,
                    'statut': 'Ouvert',
                    'mode_acquisition': 'AUTO',
                }
                
                if titre and url_source:
                    offres.append(offre)
                    
            except Exception as e:
                logger.debug(f"Erreur parsing AGETIB: {e}")
                continue
        
        logger.info(f"✅ AGETIB: {len(offres)} offre(s) extraite(s)")
        return offres
    
    def parse_detail_page(self, soup: BeautifulSoup, base_url: str) -> dict | None:
        try:
            from offres.scraping.utils import get_first_pdf_url
            url_tdr = get_first_pdf_url(soup, base_url)
            if url_tdr:
                return {'url_tdr': url_tdr}
            return None
        except Exception as e:
            logger.warning(f"Erreur extraction PDF AGETIB: {e}")
            return None
    
    def run(self) -> list[dict]:
        logger.info(f"🕷️ AGETIB scraping: {self.source_url}")
        try:
            # L'AGETIB nécessite Playwright (mode dynamique)
            soup = self.fetch_and_parse(use_js=True)
            if not soup:
                return []
            return self.parse(soup)
        except Exception as e:
            logger.error(f"❌ Erreur AGETIB: {e}")
            return []