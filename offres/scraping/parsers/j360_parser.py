"""
Parser pour J360 Info - Burkina Faso
URL: https://www.j360.info/appels-d-offres/afrique/burkina-faso/
"""
import re
import logging
import cloudscraper
from datetime import date
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text
from offres.scraping.extraction_helpers import (
    extract_publication_date_from_text,
    extract_deadline_from_text,
    is_offer_valid
)
from offres.utils.search_keywords import est_appel_offres, detecter_domaine

logger = logging.getLogger(__name__)


class J360Parser(BaseScraper):
    """Parser pour J360 Info avec contournement anti-bot via CloudScraper"""
    
    def __init__(self, source_url: str, **kwargs):
        super().__init__(source_url, **kwargs)
        self.base_domain = urlparse(source_url).netloc
        self.pays_defaut = 'BF'

    def fetch_page_robust(self, url: str) -> BeautifulSoup | None:
        """Méthode de récupération furtive avec CloudScraper pour bypass Cloudflare"""
        try:
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                }
            )
            
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0',
            }
            
            # 1. Requête sur la page d'accueil pour résoudre le défi Cloudflare
            scraper.get('https://www.j360.info/', headers=headers, timeout=15)
            
            # 2. Requête sur la page cible
            response = scraper.get(url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                return BeautifulSoup(response.text, 'html.parser')
            else:
                logger.warning(f"⚠️ Échec HTTP {response.status_code} sur {url}. La protection WAF est peut-être trop forte.")
                return None
                
        except cloudscraper.exceptions.CloudflareChallengeError:
            logger.error("❌ Cloudflare a détecté le bot et bloque l'accès.")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur de connexion robuste: {e}")
            return None

    def parse(self, soup: BeautifulSoup) -> list[dict]:
        """Parse la page principale"""
        offres_candidates = []
        if not soup:
            return offres_candidates
        
        conteneurs = soup.find_all(['article', 'div'], class_=re.compile(r'post|item|offer|tender|listing'))
        
        if not conteneurs:
            for link in soup.find_all('a', href=True):
                texte = link.get_text(strip=True)
                if len(texte) > 30 and any(mot in texte.lower() for mot in ['appel', 'offre', 'avis', 'marché', 'consultation']):
                    parent = link.find_parent(['div', 'article', 'li', 'tr'])
                    if parent and parent not in conteneurs:
                        conteneurs.append(parent)
        
        for conteneur in conteneurs[:30]:
            try:
                titre_elem = conteneur.find(['h2', 'h3', 'h4', 'a', '.title'])
                if not titre_elem:
                    continue
                
                titre = titre_elem.get_text(strip=True)
                if len(titre) < 15 or not est_appel_offres(titre):
                    continue
                
                url_source = None
                link_elem = conteneur.find('a', href=True)
                if link_elem:
                    href = link_elem.get('href', '').strip()
                    if href and not href.startswith('#') and not href.startswith('javascript:'):
                        url_source = urljoin(self.source_url, href)
                
                if not url_source:
                    continue
                
                description = conteneur.get_text(strip=True)[:1000]
                
                offres_candidates.append({
                    'titre': clean_text(titre)[:300],
                    'description': description,
                    'url_source': url_source,
                })
            except Exception as e:
                logger.debug(f"⚠️ Erreur extraction: {e}")
                continue
        
        return offres_candidates
    
    def run(self) -> list[dict]:
        logger.info(f"🕷️ J360Parser (Mode CloudScraper): {self.source_url}")
        try:
            soup = self.fetch_page_robust(self.source_url)
            if not soup:
                return []
            
            candidates = self.parse(soup)
            offres_valides = []
            
            for candidate in candidates:
                try:
                    offre = self._enrichir_offre(candidate)
                    if offre and is_offer_valid(offre)[0]:
                        offres_valides.append(offre)
                except Exception as e:
                    logger.debug(f"⚠️ Erreur enrichissement: {e}")
                    continue
            
            logger.info(f"✅ J360Parser: {len(offres_valides)} offres valides extraites")
            return offres_valides
        except Exception as e:
            logger.error(f"❌ Erreur J360Parser: {e}")
            return []
    
    def _enrichir_offre(self, candidate: dict) -> dict | None:
        titre = candidate['titre']
        url_source = candidate['url_source']
        description_base = candidate.get('description', '')
        
        detail_soup = self.fetch_page_robust(url_source)
        if not detail_soup:
            return None
        
        texte_complet = detail_soup.get_text(separator=' ')
        
        date_pub = extract_publication_date_from_text(texte_complet)
        date_cloture = extract_deadline_from_text(texte_complet)
        
        # ✅ CORRECTION : Forcer le pays à BF pour J360 Burkina
        pays = 'BF'
        
        # Chercher PDF
        pdf_url = None
        for link in detail_soup.find_all('a', href=True):
            if link.get('href', '').lower().endswith('.pdf'):
                pdf_url = urljoin(url_source, link.get('href'))
                break
        
        url_tdr = pdf_url or url_source
        
        if not date_pub:
            return None
        if date_cloture and date_cloture < date.today():
            return None
        
        return {
            'titre': titre,
            'organisme': 'J360 Info',
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