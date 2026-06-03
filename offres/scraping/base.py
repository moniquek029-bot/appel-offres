# offres/scraping/base.py - VERSION FINALE CORRIGÉE
import requests, time, logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)

class BaseScraper:
    def __init__(self, source_url: str, delay_seconds: int = 2, base_url: str = None, pays_defaut: str = 'BF', **kwargs):
        self.source_url = source_url
        self.delay_seconds = delay_seconds
        self.base_url = base_url or f"{urlparse(source_url).scheme}://{urlparse(source_url).netloc}"
        self.pays_defaut = pays_defaut
        self.session = requests.Session()
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
        }

    def fetch_html(self, url: str, timeout: int = 15) -> str | None:
        try:
            response = self.session.get(url, headers=self.default_headers, timeout=timeout, verify=True)
            response.raise_for_status()
            time.sleep(self.delay_seconds)
            return response.text
        except requests.exceptions.SSLError:
            try:
                response = self.session.get(url, headers=self.default_headers, timeout=timeout, verify=False)
                response.raise_for_status()
                return response.text
            except:
                return None
        except:
            return None

    def fetch_and_parse(self) -> BeautifulSoup | None:  # ✅ AUCUN PARAMÈTRE
        html = self.fetch_html(self.source_url)
        return BeautifulSoup(html, 'html.parser') if html else None

    def fetch_page(self, url: str) -> BeautifulSoup | None:  # ✅ AUCUN PARAMÈTRE
        if not url: return None
        full_url = url if url.startswith('http') else urljoin(self.base_url, url)
        html = self.fetch_html(full_url)
        return BeautifulSoup(html, 'html.parser') if html else None