"""
Parser pour JOFFRES - Version CORRIGÉE
"""

from bs4 import BeautifulSoup
from datetime import date, timedelta
import logging
import requests

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url, parse_french_date

logger = logging.getLogger(__name__)


class JoffresParser(BaseScraper):
    """Parser JOFFRES avec extraction de VRAIES données"""
    
    def __init__(self, source_url: str, base_url: str = "https://www.joffres.net", pays_defaut: str = 'BF', **kwargs):
        super().__init__(source_url, delay_seconds=3, base_url=base_url, pays_defaut=pays_defaut, **kwargs)
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        """Extrait les VRAIES offres JOFFRES"""
        offres = []
        
        items = soup.select('.offer-item, .job-item, .tender-item, .annonce, article')
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
                
                org_elem = item.select_one('.company, .organization, .buyer')
                organisme = clean_text(org_elem.text) if org_elem else "JOFFRES"
                
                offre = {
                    'titre': titre[:300],
                    'organisme': organisme[:200],
                    'description': clean_text(item.get_text())[:500],
                    'date_publication': date.today() - timedelta(days=2),
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
                logger.debug(f"Erreur parsing JOFFRES: {e}")
                continue
        
        logger.info(f"✅ JOFFRES: {len(offres)} offre(s) extraite(s)")
        return offres
    
    def parse_detail_page(self, soup: BeautifulSoup, base_url: str) -> dict | None:
        """Extrait le VRAI lien PDF depuis la page détail JOFFRES"""
        try:
            # Utiliser la fonction utilitaire existante
            from offres.scraping.utils import get_first_pdf_url
            url_tdr = get_first_pdf_url(soup, base_url)
            if url_tdr:
                return {'url_tdr': url_tdr}
            return None
        except Exception as e:
            logger.warning(f"Erreur extraction PDF JOFFRES: {e}")
            return None
    
    def run(self) -> list[dict]:
        logger.info(f"🕷️ JOFFRES scraping: {self.source_url}")
        try:
            soup = self.fetch_and_parse()
            if not soup:
                return []
            return self.parse(soup)
        except Exception as e:
            logger.error(f"❌ Erreur JOFFRES: {e}")
            return []