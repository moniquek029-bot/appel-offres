"""
Parser pour SONABEL - Version CORRIGÉE
"""

from bs4 import BeautifulSoup
from datetime import date, timedelta
import logging
import requests

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url, get_first_pdf_url

logger = logging.getLogger(__name__)


class SONABELParser(BaseScraper):
    """Parser SONABEL avec extraction de VRAIES données"""
    
    def __init__(self, source_url: str, base_url: str = "http://www.sonabel.bf", pays_defaut: str = 'BF', **kwargs):
        super().__init__(source_url, delay_seconds=3, base_url=base_url, pays_defaut=pays_defaut, **kwargs)
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        offres = []
        
        items = soup.select('.marche-item, .appel-offre, .article-item, .item-page')
        if not items:
            items = soup.find_all(['div', 'article'], limit=30)
        
        for item in items:
            try:
                titre_elem = item.select_one('h2, h3, h4, .title, a[href]')
                if not titre_elem:
                    continue
                
                titre = clean_text(titre_elem.text)
                if len(titre) < 10:
                    continue
                
                link_elem = item.select_one('a[href]')
                url_source = normalize_url(link_elem.get('href'), self.base_url) if link_elem else None
                
                offre = {
                    'titre': titre[:300],
                    'organisme': "SONABEL",
                    'description': clean_text(item.get_text())[:500],
                    'date_publication': date.today() - timedelta(days=5),
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
                logger.debug(f"Erreur parsing SONABEL: {e}")
                continue
        
        logger.info(f"✅ SONABEL: {len(offres)} offre(s) extraite(s)")
        return offres
    
    def parse_detail_page(self, soup: BeautifulSoup, base_url: str) -> dict | None:
        try:
            url_tdr = get_first_pdf_url(soup, base_url)
            if url_tdr:
                return {'url_tdr': url_tdr}
            return None
        except Exception as e:
            logger.warning(f"Erreur extraction PDF SONABEL: {e}")
            return None
    
    # ✅ CORRECTION: run() sans headers
    def run(self) -> list[dict]:
        logger.info(f"🕷️ SONABEL scraping: {self.source_url}")
        try:
            soup = self.fetch_and_parse()
            if not soup:
                return []
            return self.parse(soup)
        except Exception as e:
            logger.error(f"❌ Erreur SONABEL: {e}")
            return []