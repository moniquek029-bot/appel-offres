# offres/scraping/parsers/generic_parser.py 

import re
import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta
import logging

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url, parse_french_date, extract_pdf_from_page, is_valid_pdf_url

logger = logging.getLogger(__name__)


class GenericParser(BaseScraper):
    """Parser générique adaptable à tout site (PDF optionnel)"""
    
    def __init__(self, source_url: str, **kwargs):
        super().__init__(source_url, **kwargs)
        from urllib.parse import urlparse
        parsed = urlparse(source_url)
        self.base_url = f"{parsed.scheme}://{parsed.netloc}"
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        """Parse intelligemment en cherchant des patterns communs"""
        offres = []
        
        selectors = [
            'div.offre', 'div.offer', 'div.tender', 'div.appel',
            'article', '.item', '.card', '.post', '.listing-item',
            'tr', 'li.offer-item', 'div.job', 'div.procurement'
        ]
        
        containers = []
        for selector in selectors:
            found = soup.select(selector)
            if found:
                containers = found
                logger.debug(f"Pattern trouvé: {selector} ({len(found)} éléments)")
                break
        
        if not containers:
            containers = soup.find_all(['div', 'article', 'li', 'tr'], limit=50)
        
        for container in containers:
            try:
                title_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '.titre', '.name', '.offer-title']
                titre = None
                for sel in title_selectors:
                    elem = container.select_one(sel)
                    if elem and len(elem.get_text(strip=True)) > 10:
                        titre = clean_text(elem.get_text(strip=True))
                        break
                
                if not titre or len(titre) < 10:
                    continue
                
                link_elem = container.select_one('a[href]')
                url_source = normalize_url(link_elem.get('href'), self.base_url) if link_elem else None
                
                if not url_source:
                    continue
                
                date_selectors = ['.date', '.deadline', '.closing', '.posted', 'time', '[datetime]']
                date_cloture = date.today() + timedelta(days=30)
                for sel in date_selectors:
                    elem = container.select_one(sel)
                    if elem:
                        date_text = clean_text(elem.text)
                        parsed_date = parse_french_date(date_text)
                        if parsed_date:
                            date_cloture = parsed_date
                            break
                
                offre = {
                    'titre': titre[:300],
                    'organisme': self._extract_organisme(container),
                    'description': clean_text(container.get_text())[:500],
                    'date_publication': date.today() - timedelta(days=2),
                    'date_cloture': date_cloture,
                    'url_source': url_source,
                    'url_tdr': None,
                    'pays': self.pays_defaut,
                    'statut': 'Ouvert',
                    'mode_acquisition': 'AUTO',
                }
                
                offres.append(offre)
                    
            except Exception as e:
                logger.debug(f"Erreur parsing: {e}")
                continue
        
        logger.info(f"✅ {len(offres)} offre(s) extraite(s)")
        return offres
    
    def _extract_organisme(self, container) -> str:
        """Extrait l'organisme du conteneur"""
        org_selectors = ['.organization', '.buyer', '.author', '.company', '.publisher', '.client']
        for sel in org_selectors:
            elem = container.select_one(sel)
            if elem and len(elem.get_text(strip=True)) > 3:
                return clean_text(elem.get_text(strip=True))
        return "Organisme non spécifié"
    
    def parse_detail_page(self, soup: BeautifulSoup, base_url: str) -> dict | None:
        """Extrait le PDF de la page détail (optionnel)"""
        try:
            pdf_url = extract_pdf_from_page(str(soup), base_url)
            if pdf_url:
                return {'url_tdr': pdf_url}
            return None
        except Exception as e:
            logger.debug(f"Erreur extraction PDF: {e}")
            return None
    
    def run(self) -> list[dict]:
        """Exécute le scraping générique"""
        logger.info(f"🕷️ Scraping générique: {self.source_url}")
        
        soup = self.fetch_and_parse()
        if not soup:
            logger.warning(f"Aucune donnée pour {self.source_url}")
            return []
        
        offres = self.parse(soup)
        
        # Essayer d'extraire les PDF pour chaque offre (optionnel)
        for offre in offres:
            if offre.get('url_source'):
                try:
                    detail_soup = self.fetch_page(offre['url_source'])
                    if detail_soup:
                        pdf_data = self.parse_detail_page(detail_soup, self.base_url)
                        if pdf_data and pdf_data.get('url_tdr'):
                            offre['url_tdr'] = pdf_data['url_tdr']
                            logger.info(f" PDF trouvé pour: {offre['titre'][:50]}...")
                except Exception as e:
                    logger.debug(f"Erreur extraction PDF: {e}")
        
        return offres