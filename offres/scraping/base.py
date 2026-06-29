# offres/scraping/base.py
import requests
import time
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import urllib3
from offres.scraping.extraction_helpers import is_offer_expired, extract_all_details

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class BaseScraper:
    def __init__(self, source_url: str, delay_seconds: int = 2, base_url: str = None, pays_defaut: str = 'BF', **kwargs):
        self.source_url = source_url
        self.delay_seconds = delay_seconds
        self.base_url = base_url or f"{urlparse(source_url).scheme}://{urlparse(source_url).netloc}"
        self.pays_defaut = pays_defaut
        self.session = requests.Session()
        self.session.verify = False  # ← DÉSACTIVER VÉRIFICATION SSL
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
        }

    def fetch_html(self, url: str, timeout: int = 15) -> str | None:
        """Requête HTTP avec gestion SSL désactivée"""
        try:
            logger.info(f"📡 Requête HTTP vers : {url}")
            response = self.session.get(
                url,
                headers=self.default_headers,
                timeout=timeout,
                verify=False  # ← IGNORER SSL
            )
            response.raise_for_status()
            time.sleep(self.delay_seconds)
            logger.info(f"✅ HTML récupéré : {len(response.text)} caractères")
            return response.text
        except Exception as e:
            logger.error(f"❌ Erreur fetch_html: {e}")
            return None

    def fetch_html_with_js(self, url: str, timeout_seconds: int = 30) -> str | None:
        """Rendu JavaScript via Playwright"""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.error("❌ Playwright non installé. Lancez: pip install playwright && playwright install chromium")
            return None

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=self.default_headers['User-Agent'],
                    viewport={"width": 1920, "height": 1080}
                )
                page = context.new_page()
                logger.info(f"🌐 Chargement Playwright pour : {url}")
                page.goto(url, timeout=timeout_seconds * 1000, wait_until="networkidle")
                time.sleep(self.delay_seconds)
                html = page.content()
                browser.close()
                logger.info(f"✅ HTML Playwright : {len(html)} caractères")
                return html
        except Exception as e:
            logger.error(f"❌ Erreur Playwright: {e}")
            return None

    def fetch_and_parse(self, use_js: bool = False) -> BeautifulSoup | None:
        """Récupère et parse le HTML"""
        try:
            if use_js:
                html = self.fetch_html_with_js(self.source_url)
            else:
                html = self.fetch_html(self.source_url)
            
            if html:
                return BeautifulSoup(html, "html.parser")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur fetch_and_parse: {e}")
            return None

    def fetch_page(self, url: str, use_js: bool = False) -> BeautifulSoup | None:
        """Récupère une page secondaire"""
        if not url:
            return None
        full_url = url if url.startswith('http') else urljoin(self.base_url, url)
        html = self.fetch_html_with_js(full_url) if use_js else self.fetch_html(full_url)
        return BeautifulSoup(html, 'html.parser') if html else None
    

    # Dans offres/scraping/base.py, ajoutez cette méthode à la classe BaseScraper :

def validate_site(self) -> dict:
    """
    Valide si le site est un site d'appels d'offres
    """
    from offres.scraping.site_validator import SiteValidator
    
    try:
        # Récupérer la page
        soup = self.fetch_and_parse(use_js=False)
        
        if not soup:
            return {
                'is_valid': False,
                'score': 0,
                'error': 'Impossible de récupérer la page'
            }
        
        # Valider
        validator = SiteValidator(soup=soup, url=self.source_url)
        return validator.validate()
    
    except Exception as e:
        logger.error(f"❌ Erreur validation: {e}")
        return {
            'is_valid': False,
            'score': 0,
            'error': str(e)
        }
    
# Dans la classe BaseScraper, ajoutez ces méthodes :


def filter_expired_offers(self, offres: list[dict]) -> list[dict]:
    """
    Filtre les offres expirées AVANT sauvegarde
    Log chaque offre rejetée
    """
    offres_valides = []
    rejected_count = 0
    
    for offre in offres:
        date_cloture = offre.get('date_cloture')
        
        if is_offer_expired(date_cloture):
            rejected_count += 1
            logger.info(f"   ⏭️ Offre EXPIRÉE rejetée : {offre.get('titre', '')[:50]}... (clôture: {date_cloture})")
            continue
        
        offres_valides.append(offre)
    
    if rejected_count > 0:
        logger.info(f"   📊 {rejected_count} offre(s) expirée(s) rejetée(s), {len(offres_valides)} conservée(s)")
    
    return offres_valides

def extract_details_unified(self, detail_url: str) -> dict:
    """
    Extrait tous les détails d'une page en utilisant les helpers centralisés
    """
    try:
        soup = self.fetch_page(detail_url)
        if not soup:
            return {}
        
        return extract_all_details(
            soup, 
            url=detail_url, 
            pays_defaut=self.pays_defaut
        )
    except Exception as e:
        logger.warning(f"⚠️ Erreur extraction détails: {e}")
        return {}