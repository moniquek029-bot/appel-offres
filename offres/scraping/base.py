"""
BaseScraper amélioré avec retry, fallback DNS et gestion d'erreurs
"""
import requests
import urllib3
import ssl
import time
import socket
import logging
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class SSLAdapter(HTTPAdapter):
    """Adaptateur qui ignore les erreurs SSL"""
    def __init__(self, *args, **kwargs):
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        super().__init__(*args, **kwargs)
    
    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().init_poolmanager(*args, **kwargs)


DNS_FALLBACKS = {
    '8.8.8.8': 'Google DNS',
    '1.1.1.1': 'Cloudflare DNS',
    '9.9.9.9': 'Quad9 DNS',
}


def test_dns_resolution(domain: str) -> bool:
    try:
        socket.gethostbyname(domain)
        return True
    except socket.gaierror:
        return False


def force_dns_resolution(domain: str) -> str | None:
    if test_dns_resolution(domain):
        return domain
    
    for dns_ip, dns_name in DNS_FALLBACKS.items():
        try:
            import dns.resolver
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [dns_ip]
            answers = resolver.resolve(domain, 'A')
            ip = str(answers[0])
            logger.info(f"   🌐 DNS résolu via {dns_name}: {domain} → {ip}")
            return ip
        except Exception as e:
            logger.debug(f"   ⚠️ DNS {dns_name} échoué pour {domain}: {e}")
            continue
    
    return None


class BaseScraper(ABC):
    """Scraper de base avec retry et gestion d'erreurs robuste"""
    
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    TIMEOUT = 30
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    def __init__(self, source_url: str, **kwargs):
        self.source_url = source_url
        self.base_url = kwargs.get('base_url', source_url)
        self.pays_defaut = kwargs.get('pays_defaut', 'BF')
        self.delay_seconds = kwargs.get('delay_seconds', 1)
        
        self.session = requests.Session()
        self.session.verify = False
        
        retry_strategy = Retry(
            total=self.MAX_RETRIES,
            backoff_factor=self.RETRY_DELAY,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", SSLAdapter())
        
        self.session.headers.update({
            'User-Agent': self.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr,fr-FR;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def fetch_page(self, url: str, use_js: bool = False, timeout: int = None) -> BeautifulSoup | None:
        timeout = timeout or self.TIMEOUT
        
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                logger.debug(f"   🌐 Tentative {attempt}/{self.MAX_RETRIES}: {url[:80]}")
                
                response = self.session.get(url, timeout=timeout, allow_redirects=True)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    logger.debug(f"   ✅ Page récupérée ({len(response.content)} bytes)")
                    return soup
                
                elif response.status_code in [403, 429]:
                    logger.warning(f"   ⚠️ Status {response.status_code} - Attente avant retry")
                    time.sleep(self.RETRY_DELAY * attempt)
                    continue
                
                else:
                    logger.warning(f"   ⚠️ Status HTTP {response.status_code}")
                    return None
                    
            except requests.exceptions.SSLError as e:
                logger.warning(f"   ⚠️ SSL Error (tentative {attempt}): {str(e)[:80]}")
                try:
                    response = requests.get(url, timeout=timeout, verify=False,
                                          headers=self.session.headers)
                    if response.status_code == 200:
                        return BeautifulSoup(response.text, 'html.parser')
                except Exception:
                    pass
                
            except requests.exceptions.ConnectionError as e:
                error_str = str(e)
                
                if 'NameResolutionError' in error_str or 'getaddrinfo failed' in error_str:
                    logger.warning(f"   ⚠️ Erreur DNS (tentative {attempt})")
                    
                    from urllib.parse import urlparse
                    domain = urlparse(url).netloc
                    
                    ip = force_dns_resolution(domain)
                    if ip:
                        new_url = url.replace(domain, ip)
                        logger.info(f"   🔄 Retry avec IP: {new_url[:80]}")
                        try:
                            response = requests.get(new_url, timeout=timeout, verify=False,
                                                  headers=self.session.headers,
                                                  allow_redirects=True)
                            if response.status_code == 200:
                                return BeautifulSoup(response.text, 'html.parser')
                        except Exception as retry_err:
                            logger.error(f"   ❌ Retry échoué: {retry_err}")
                
                elif 'Connection refused' in error_str:
                    logger.warning(f"   ⚠️ Connexion refusée")
                
                elif 'Connection timed out' in error_str or 'Read timed out' in error_str:
                    logger.warning(f"   ⚠️ Timeout")
                
                if attempt < self.MAX_RETRIES:
                    time.sleep(self.RETRY_DELAY * attempt)
                    continue
                
                logger.error(f"   ❌ Échec après {self.MAX_RETRIES} tentatives")
                return None
                
            except requests.exceptions.Timeout:
                logger.warning(f"   ⚠️ Timeout (tentative {attempt})")
                if attempt < self.MAX_RETRIES:
                    time.sleep(self.RETRY_DELAY * attempt)
                    continue
                return None
                
            except Exception as e:
                logger.error(f"   ❌ Erreur inattendue: {e}")
                return None
        
        return None
    
    def fetch_and_parse(self, use_js: bool = False) -> BeautifulSoup | None:
        time.sleep(self.delay_seconds)
        return self.fetch_page(self.source_url, use_js=use_js)
    
    @abstractmethod
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        pass
    
    @abstractmethod
    def run(self) -> list[dict]:
        pass