# offres/scraping/parsers/afdb_parser.py
import re
import logging
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import date, timedelta

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url, parse_french_date, detecter_pays
from offres.scraping.extraction_helpers import extract_pdf_url
from offres.utils.search_keywords import detecter_domaine, est_appel_offres

logger = logging.getLogger(__name__)


class AfDBParser(BaseScraper):
    """Parser AfDB - UNIQUEMENT les appels d'offres"""
    
    def __init__(self, source_url: str, **kwargs):
        base_url = "https://www.afdb.org"
        super().__init__(source_url, delay_seconds=2, base_url=base_url, **kwargs)
        self.pays_defaut = 'REGIONAL'
    
    def detecter_domaine(self, titre, description=""):
        return detecter_domaine(titre, description)
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        offres = []
        articles = soup.find_all(['tr', 'div', 'article'], class_=re.compile(r'procurement|tender|opportunity', re.I))
        
        if not articles:
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) > 1:
                    articles.extend(rows[1:])
        
        logger.info(f"🔍 AfDB: {len(articles)} blocs trouvés")
        
        for article in articles:
            try:
                offre = self._parser_article(article)
                if offre:
                    if offre['date_cloture'] and offre['date_cloture'] < date.today():
                        continue
                    
                    if not est_appel_offres(offre.get('titre', ''), offre.get('description', '')):
                        logger.info(f"   ⏭️ REJETÉ (pas un appel d'offres): {offre.get('titre', '')[:50]}...")
                        continue
                    
                    if not any(o['url_source'] == offre['url_source'] for o in offres):
                        offres.append(offre)
                        logger.info(f"  ✅ Appel d'offres extrait (domaine: {offre.get('domaine', 'Autres')})")
            except Exception as e:
                logger.debug(f"⚠️ Erreur parsing: {e}")
                continue
        
        return offres
    
    def _parser_article(self, article) -> dict | None:
        titre_elem = article.find(['a', 'h3', 'h4', 'td'])
        if not titre_elem:
            return None
        
        titre = clean_text(titre_elem.get_text(strip=True))
        if len(titre) < 15:
            return None
        
        url_source = None
        link_elem = article.find('a', href=True)
        if link_elem:
            url_source = urljoin(self.base_url, link_elem['href'])
        
        if not url_source:
            return None
        
        date_pub = date.today()
        date_cloture = date_pub + timedelta(days=45)
        pays = detecter_pays(titre, 'BF')
        domaine = self.detecter_domaine(titre)
        description = f"Banque Africaine de Développement (AfDB) - {titre}"
        
        return {
            'titre': titre[:300],
            'organisme': 'African Development Bank',
            'description': description[:500],
            'date_publication': date_pub,
            'date_cloture': date_cloture,
            'url_source': url_source,
            'url_tdr': url_source,  # ✅ Sera mis à jour dans run()
            'pays': pays,
            'domaine': domaine,
            'statut': 'Ouvert',
            'type_offre': 'APPEL_D_OFFRES',
            'mode_acquisition': 'AUTO',
        }
    
    def run(self) -> list[dict]:
        logger.info(f"🕷️ AfDB scraping: {self.source_url}")
        try:
            soup = self.fetch_and_parse(use_js=True)
            if not soup:
                return []
            
            offres = self.parse(soup)
            for offre in offres:
                if offre.get('url_source'):
                    time.sleep(1)
                    detail_soup = self.fetch_page(offre['url_source'])
                    if detail_soup:
                        pdf_url = extract_pdf_url(detail_soup, self.base_url)
                        if pdf_url:
                            offre['url_tdr'] = pdf_url
                            logger.info(f"  ✅ PDF trouvé pour {offre['titre'][:40]}...")
            return offres
        except Exception as e:
            logger.error(f"❌ Erreur AfDB: {e}")
            return []