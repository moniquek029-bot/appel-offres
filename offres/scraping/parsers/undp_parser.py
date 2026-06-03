# offres/scraping/parsers/undp_parser.py
# Version complète et corrigée

import re
import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta
from urllib.parse import urljoin
import logging

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url

logger = logging.getLogger(__name__)


class UNDPParser(BaseScraper):
    """Parser UNDP avec extraction des offres"""
    
    def __init__(self, source_url: str, base_url: str = "https://procurement-notices.undp.org", pays_defaut: str = 'BF', **kwargs):
        super().__init__(source_url, delay_seconds=2, base_url=base_url, pays_defaut=pays_defaut, **kwargs)
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        """Extrait les offres UNDP depuis la page de recherche"""
        offres = []
        
        # Chercher les lignes du tableau des résultats
        rows = soup.find_all('tr')
        
        for row in rows:
            try:
                # Chercher le lien de la notice
                link = row.find('a', href=re.compile(r'notice'))
                if not link:
                    continue
                
                titre = clean_text(link.get_text(strip=True))
                if len(titre) < 15:
                    continue
                
                url_source = normalize_url(link['href'], self.base_url)
                
                # Extraire la date de clôture
                cells = row.find_all('td')
                date_cloture = date.today() + timedelta(days=30)
                for cell in cells:
                    cell_text = cell.get_text(strip=True)
                    if '/' in cell_text or '-' in cell_text:
                        try:
                            from datetime import datetime
                            for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d', '%Y-%m-%d']:
                                try:
                                    date_cloture = datetime.strptime(cell_text, fmt).date()
                                    break
                                except:
                                    pass
                        except:
                            pass
                
                offre = {
                    'titre': titre[:300],
                    'organisme': "UNDP",
                    'description': clean_text(row.get_text(strip=True))[:500],
                    'date_publication': date.today() - timedelta(days=5),
                    'date_cloture': date_cloture,
                    'url_source': url_source,
                    'url_tdr': None,
                    'pays': self.pays_defaut,
                    'statut': 'Ouvert',
                    'mode_acquisition': 'AUTO',
                }
                offres.append(offre)
                
            except Exception as e:
                logger.debug(f"Erreur parsing ligne UNDP: {e}")
                continue
        
        logger.info(f"✅ UNDP: {len(offres)} offre(s) extraite(s)")
        return offres[:30]
    
    def parse_detail_page(self, soup: BeautifulSoup, base_url: str) -> dict | None:
        """Extrait le PDF depuis la page détail"""
        try:
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.endswith('.pdf'):
                    return {'url_tdr': normalize_url(href, base_url)}
                text = link.get_text().lower()
                if 'download' in text or 'pdf' in text:
                    if '.pdf' in href.lower():
                        return {'url_tdr': normalize_url(href, base_url)}
            return None
        except Exception as e:
            logger.warning(f"Erreur extraction PDF UNDP: {e}")
            return None
    
    def run(self) -> list[dict]:
        logger.info(f"🕷️ UNDP scraping: {self.source_url}")
        try:
            soup = self.fetch_and_parse()
            if not soup:
                return []
            return self.parse(soup)
        except Exception as e:
            logger.error(f"❌ Erreur UNDP: {e}")
            return []