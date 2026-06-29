# offres/scraping/base.py
"""
Classe de base pour tous les parsers
"""
import time
import logging
import requests
import urllib3
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod

# Désactiver les warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Classe abstraite pour tous les parsers"""
    
    def __init__(self, source_url: str, delay_seconds: int = 2, 
                 base_url: str = None, pays_defaut: str = 'BF', 
                 verify_ssl: bool = True, **kwargs):
        self.source_url = source_url
        self.delay_seconds = delay_seconds
        self.base_url = base_url or source_url
        self.pays_defaut = pays_defaut
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        # ✅ Désactiver la vérification SSL si nécessaire
        self.session.verify = self.verify_ssl
    
    def fetch_page(self, url: str) -> BeautifulSoup | None:
        """Récupère une page et retourne un objet BeautifulSoup"""
        try:
            time.sleep(self.delay_seconds)
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.SSLError as e:
            logger.warning(f"⚠️ Erreur SSL {url}: {e}")
            # ✅ Retry sans vérification SSL
            if self.verify_ssl:
                logger.info(f"🔄 Retry sans vérification SSL...")
                try:
                    response = self.session.get(url, timeout=30, verify=False)
                    response.raise_for_status()
                    return BeautifulSoup(response.text, 'html.parser')
                except Exception as retry_error:
                    logger.warning(f"⚠️ Erreur retry {url}: {retry_error}")
                    return None
            return None
        except Exception as e:
            logger.warning(f"⚠️ Erreur fetch {url}: {e}")
            return None
    
    def fetch_and_parse(self, use_js: bool = False) -> BeautifulSoup | None:
        """Récupère et parse la page principale"""
        return self.fetch_page(self.source_url)
    
    @abstractmethod
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        """Parse la page et retourne une liste d'offres"""
        pass
    
    @abstractmethod
    def run(self) -> list[dict]:
        """Lance le scraping complet"""
        pass