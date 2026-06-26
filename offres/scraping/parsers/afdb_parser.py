# offres/scraping/parsers/afdb_parser.py
import re
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import date, timedelta

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url, parse_french_date, detecter_pays

logger = logging.getLogger(__name__)


class AfDBParser(BaseScraper):
    """Parser spécialisé pour African Development Bank"""
    
    def __init__(self, source_url: str, **kwargs):
        base_url = "https://www.afdb.org"
        super().__init__(source_url, delay_seconds=2, base_url=base_url, **kwargs)
        self.pays_defaut = 'AF'  # Africa
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        """Parse la page AfDB Procurement"""
        offres = []
        
        # AfDB utilise des tableaux ou des listes
        articles = soup.find_all(['tr', 'div', 'article'], class_=re.compile(r'procurement|tender|opportunity', re.I))
        
        if not articles:
            # Fallback : chercher dans les tableaux
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) > 1:  # Plus qu'une ligne d'en-tête
                    articles.extend(rows[1:])  # Skip header
        
        logger.info(f"🔍 AfDB: {len(articles)} blocs trouvés")
        
        for article in articles:
            try:
                offre = self._parser_article(article)
                if offre:
                    if not any(o['url_source'] == offre['url_source'] for o in offres):
                        offres.append(offre)
            except Exception as e:
                logger.debug(f"⚠️ Erreur parsing: {e}")
                continue
        
        logger.info(f"✅ AfDB: {len(offres)} offre(s) extraite(s)")
        return offres
    
    def _parser_article(self, article) -> dict | None:
        """Parse un article individuel"""
        
        # Titre
        titre_elem = article.find(['a', 'h3', 'h4', 'td'])
        if not titre_elem:
            return None
        
        titre = clean_text(titre_elem.get_text(strip=True))
        if len(titre) < 15:
            return None
        
        # Lien
        url_source = None
        link_elem = article.find('a', href=True)
        if link_elem:
            url_source = urljoin(self.base_url, link_elem['href'])
        
        if not url_source:
            return None
        
        # Description
        description = titre
        
        # Dates
        date_pub = date.today()
        date_cloture = date_pub + timedelta(days=45)
        
        # Pays africain par défaut
        pays = detecter_pays(titre, 'BF')
        
        offre = {
            'titre': titre[:300],
            'organisme': 'African Development Bank',
            'description': description[:500],
            'date_publication': date_pub,
            'date_cloture': date_cloture,
            'url_source': url_source,
            'url_tdr': None,
            'pays': pays,
            'statut': 'Ouvert',
            'mode_acquisition': 'AUTO',
        }
        
        return offre
    
    def extract_pdf_from_detail(self, detail_url: str) -> str | None:
        """Extrait le PDF depuis la page de détail"""
        try:
            soup = self.fetch_page(detail_url)
            if not soup:
                return None
            
            # Chercher les liens PDF
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text(strip=True).lower()
                
                if '.pdf' in href.lower():
                    return normalize_url(href, self.base_url)
                
                if any(word in text for word in ['download', 'document', 'notice', ' bidding']):
                    if href and not href.startswith('#'):
                        return normalize_url(href, self.base_url)
            
            return None
        except Exception as e:
            logger.warning(f"⚠️ Erreur extraction PDF: {e}")
            return None
    
    def run(self) -> list[dict]:
        """Exécute le scraping complet"""
        logger.info(f"🕷️ AfDB scraping: {self.source_url}")
        try:
            soup = self.fetch_and_parse(use_js=True)
            if not soup:
                return []
            
            offres = self.parse(soup)
            
            # Extraire les PDFs
            for offre in offres:
                if offre.get('url_source'):
                    import time
                    time.sleep(1)
                    pdf_url = self.extract_pdf_from_detail(offre['url_source'])
                    if pdf_url:
                        offre['url_tdr'] = pdf_url
                        logger.info(f"📄 PDF trouvé: {offre['titre'][:50]}")
            
            return offres
        except Exception as e:
            logger.error(f"❌ Erreur AfDB: {e}")
            return []