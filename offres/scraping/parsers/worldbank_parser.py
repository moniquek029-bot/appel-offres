# offres/scraping/parsers/worldbank_parser.py
"""
Parser pour la Banque Mondiale
"""
import re
import logging
from datetime import date, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url
from offres.scraping.extraction_helpers import extract_all_details, extract_pdf_url, is_offer_valid

logger = logging.getLogger(__name__)


class WorldBankParser(BaseScraper):
    """Parser Banque Mondiale"""
    
    def __init__(self, source_url: str, **kwargs):
        super().__init__(source_url, **kwargs)
        self.base_url = "https://www.worldbank.org"
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        offres = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            titre = link.get_text(strip=True)
            
            if not titre or len(titre) < 15:
                continue
            
            if not any(kw in href.lower() for kw in ['procurement', 'contract', 'bid']):
                continue
            
            url_source = urljoin(self.base_url, href)
            
            detail_soup = self.fetch_page(url_source)
            if not detail_soup:
                continue
            
            details = extract_all_details(
                detail_soup,
                url=url_source,
                pays_defaut='GLOBAL',
                titre=titre,
                description=titre
            )
            
            offre = {
                'titre': clean_text(titre)[:300],
                'organisme': 'Banque Mondiale',
                'description': clean_text(titre)[:1000],
                'date_publication': details.get('date_publication'),
                'date_cloture': details.get('date_cloture'),
                'url_source': url_source,
                'url_tdr': details.get('url_tdr'),
                'pays': details.get('pays', 'GLOBAL'),
                'domaine': 'Finance & Comptabilité',
                'statut': 'Ouvert',
                'type_offre': 'APPEL_D_OFFRES',
                'mode_acquisition': 'AUTO',
            }
            
            is_valid, reason = is_offer_valid(offre)
            if is_valid:
                offres.append(offre)
        
        return offres
    
    def run(self) -> list[dict]:
        logger.info(f"🕷️ WorldBank scraping: {self.source_url}")
        try:
            soup = self.fetch_and_parse()
            if not soup:
                return []
            return self.parse(soup)
        except Exception as e:
            logger.error(f"❌ Erreur WorldBank: {e}")
            return []