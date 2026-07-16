"""
Parser spécifique pour Tala Com
URL: https://www.tala-com.com/tous-les-appels-doffres/
"""
import re
import logging
from datetime import date, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url
from offres.scraping.extraction_helpers import (
    extract_publication_date_from_text,
    extract_deadline_from_text,
    is_offer_valid
)
from offres.scraping.country_detector import detecter_pays_smart
from offres.utils.search_keywords import est_appel_offres, detecter_domaine

logger = logging.getLogger(__name__)


class TalaComParser(BaseScraper):
    """Parser spécifique pour Tala Com"""
    
    def __init__(self, source_url: str, **kwargs):
        super().__init__(source_url, **kwargs)
        self.base_domain = urlparse(source_url).netloc
        self.pays_defaut = 'BF'
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        """Parse la page principale"""
        offres_candidates = []
        
        if not soup:
            return offres_candidates
        
        # Tala Com utilise probablement une structure WordPress
        articles = soup.find_all('article')
        
        if not articles:
            articles = soup.find_all('div', class_=re.compile(r'post|entry|item'))
        
        if not articles:
            for link in soup.find_all('a', href=True):
                texte = link.get_text(strip=True)
                if len(texte) > 30 and any(mot in texte.lower() for mot in [
                    'appel', 'offre', 'avis', 'marché'
                ]):
                    parent = link.find_parent(['div', 'article', 'li'])
                    if parent:
                        articles.append(parent)
        
        for article in articles[:30]:
            try:
                titre = None
                for sel in ['h2', 'h3', 'a', '.title']:
                    elem = article.find(sel) if hasattr(article, 'find') else None
                    if elem:
                        titre = elem.get_text(strip=True)
                        if len(titre) > 15:
                            break
                
                if not titre or len(titre) < 15:
                    continue
                
                if not est_appel_offres(titre):
                    continue
                
                url_source = None
                link_elem = article.find('a', href=True) if hasattr(article, 'find') else None
                if link_elem:
                    href = link_elem.get('href', '').strip()
                    if href and not href.startswith('#'):
                        url_source = urljoin(self.source_url, href)
                
                if not url_source:
                    continue
                
                description = article.get_text(strip=True)[:1000]
                
                offres_candidates.append({
                    'titre': clean_text(titre)[:300],
                    'description': clean_text(description),
                    'url_source': url_source,
                })
                
            except Exception as e:
                logger.debug(f"⚠️ Erreur: {e}")
                continue
        
        return offres_candidates
    
    def run(self) -> list[dict]:
        """Exécute le scraping"""
        logger.info(f"🕷️ TalaComParser: {self.source_url}")
        
        try:
            soup = self.fetch_and_parse(use_js=False)
            if not soup:
                return []
            
            candidates = self.parse(soup)
            if not candidates:
                return []
            
            offres_valides = []
            
            for candidate in candidates:
                try:
                    offre = self._enrichir_offre(candidate)
                    if offre:
                        is_valid, reason = is_offer_valid(offre)
                        if not is_valid:
                            continue
                        offres_valides.append(offre)
                except Exception as e:
                    logger.debug(f"⚠️ Erreur: {e}")
                    continue
            
            logger.info(f"✅ TalaComParser: {len(offres_valides)} offres")
            return offres_valides
            
        except Exception as e:
            logger.error(f"❌ Erreur: {e}")
            return []
    
    def _enrichir_offre(self, candidate: dict) -> dict | None:
        """Enrichit une offre"""
        titre = candidate['titre']
        url_source = candidate['url_source']
        description_base = candidate.get('description', '')
        
        detail_soup = self.fetch_page(url_source)
        if not detail_soup:
            return None
        
        texte_complet = detail_soup.get_text(separator=' ')
        
        date_pub = extract_publication_date_from_text(texte_complet)
        date_cloture = extract_deadline_from_text(texte_complet)
        
        pays = detecter_pays_smart(texte_complet, url=url_source, pays_defaut='BF')
        
        pdf_url = None
        for link in detail_soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            if href.endswith('.pdf'):
                pdf_url = urljoin(url_source, link.get('href'))
                break
        
        url_tdr = pdf_url or url_source
        
        if not date_pub:
            return None
        
        if date_cloture and date_cloture < date.today():
            return None
        
        offre = {
            'titre': titre,
            'organisme': 'Tala Com',
            'description': description_base[:2000],
            'date_publication': date_pub,
            'date_cloture': date_cloture,
            'url_source': url_source,
            'url_tdr': url_tdr,
            'pays': pays,
            'domaine': detecter_domaine(titre, description_base) or 'Autres',
            'statut': 'Ouvert',
            'type_offre': 'APPEL_D_OFFRES',
            'mode_acquisition': 'AUTO',
        }
        
        logger.info(f"   ✅ {titre[:50]} | {pays} | Pub: {date_pub}")
        return offre