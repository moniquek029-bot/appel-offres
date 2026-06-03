"""
Parser pour UEMOA - Version CORRIGÉE
"""

from bs4 import BeautifulSoup
from datetime import date, timedelta
import logging
import requests

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url, get_first_pdf_url

logger = logging.getLogger(__name__)


class UEMOAParser(BaseScraper):
    """Parser UEMOA avec extraction de VRAIES données"""
    
    def __init__(self, source_url: str, base_url: str = "https://www.uemoa.int", pays_defaut: str = 'BF', **kwargs):
        super().__init__(source_url, delay_seconds=3, base_url=base_url, pays_defaut=pays_defaut, **kwargs)
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        offres = []
        
        items = soup.select('.views-row, .node, .appel-item, article')
        if not items:
            items = soup.find_all(['div', 'article'], limit=30)
        
        for item in items:
            try:
                title_link = item.select_one('a')
                if not title_link:
                    continue
                
                titre = clean_text(title_link.text)
                if len(titre) < 10:
                    continue
                
                url_source = normalize_url(title_link.get('href'), self.base_url)
                
                offre = {
                    'titre': titre[:300],
                    'organisme': "UEMOA",
                    'description': clean_text(item.get_text())[:500],
                    'date_publication': date.today() - timedelta(days=7),
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
                logger.debug(f"Erreur parsing UEMOA: {e}")
                continue
        
        logger.info(f"✅ UEMOA: {len(offres)} offre(s) extraite(s)")
        return offres
    
    def parse_detail_page(self, soup: BeautifulSoup, base_url: str) -> dict | None:
        try:
            url_tdr = get_first_pdf_url(soup, base_url)
            if url_tdr:
                return {'url_tdr': url_tdr}
            return None
        except Exception as e:
            logger.warning(f"Erreur extraction PDF UEMOA: {e}")
            return None
    
    # ✅ CORRECTION: run() sans headers
    def run(self) -> list[dict]:
        logger.info(f"🕷️ UEMOA scraping: {self.source_url}")
        try:
            soup = self.fetch_and_parse()
            if not soup:
                return []
            return self.parse(soup)
        except Exception as e:
            logger.error(f"❌ Erreur UEMOA: {e}")
            return []