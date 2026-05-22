"""
offres/scraping/base.py
Moteur de scraping conforme au CDC :
- Section 4.a : Utilisation de requests + BeautifulSoup pour sites statiques
- Section 1.b : Respect des robots.txt & limitation de fréquence
- Section 3 : Modularité pour faciliter les mises à jour
- Section 4.a bis : Selenium pour sites dynamiques (JavaScript)
"""

import time
import logging
import requests
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class BaseScraper:
    """Classe de base sécurisée et modulaire pour l'extraction de métadonnées."""
    
    def __init__(self, source_url: str, delay_seconds: int = 3, max_retries: int = 3):
        self.source_url = source_url.rstrip("/")
        self.delay = delay_seconds  # CDC: Évite la surcharge des serveurs sources
        self.session = requests.Session()
        
        # Headers réalistes pour éviter les blocages basiques
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; TendersBot/1.0; +https://votre-domaine.com/bot)"
        })
        
        # Stratégie de retry automatique (429, 5xx)
        retry_strategy = Retry(total=max_retries, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
        self.session.mount("http://", HTTPAdapter(max_retries=retry_strategy))
        self.session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
        
        self.robot_parser = RobotFileParser()
        self._load_robots()

    def _load_robots(self):
        """Charge et vérifie les directives robots.txt (CDC Section 1.c)"""
        try:
            self.robot_parser.set_url(f"{self.source_url}/robots.txt")
            self.robot_parser.read()
            logger.info(f"✅ robots.txt chargé pour {self.source_url}")
        except Exception as e:
            logger.warning(f"⚠️ Impossible de lire robots.txt : {e}")

    def is_allowed(self, path: str) -> bool:
        """Vérifie si le scraping est autorisé pour un chemin donné"""
        return self.robot_parser.can_fetch("*", path)

    def fetch_html(self, url: str) -> str | None:
        """Récupère le HTML avec timeout et gestion d'erreurs réseau"""
        if not self.is_allowed("/"):
            logger.warning(f"🚫 Scraping bloqué par robots.txt pour {url}")
            return None
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"❌ Erreur HTTP pour {url} : {e}")
            return None

    def fetch_with_selenium(self, url: str, wait_seconds: int = 5) -> str | None:
        """
        Récupère le HTML d'un site dynamique (JavaScript) avec Selenium.
        Conforme CDC Section 4.a : "Selenium sera privilégié pour les sites dynamiques"
        
        Args:
            url: L'URL à scraper
            wait_seconds: Temps d'attente pour le chargement JavaScript (défaut: 5s)
        
        Returns:
            Le HTML de la page ou None en cas d'erreur
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            logger.info(f"🌐 Utilisation de Selenium pour {url[:80]}...")
            
            # Configuration de Chrome en mode headless (pas d'interface graphique)
            options = Options()
            options.add_argument('--headless')  # Mode sans interface graphique
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            # Installation automatique du driver Chrome
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            # Chargement de la page
            driver.get(url)
            time.sleep(wait_seconds)  # Attendre le chargement JavaScript
            
            # Récupération du HTML généré
            html = driver.page_source
            driver.quit()
            
            logger.info(f"✅ Page dynamique récupérée avec Selenium ({len(html)} caractères)")
            return html
            
        except ImportError as e:
            logger.error(f"❌ Selenium non installé. Exécutez: pip install selenium webdriver-manager")
            logger.error(f"   Erreur détaillée: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur Selenium pour {url[:80]}...: {type(e).__name__} - {e}")
            return None

    def fetch_and_parse(self, use_selenium: bool = False) -> BeautifulSoup | None:
        """
        Récupère et parse le HTML en choisissant le moteur adapté.
        
        Args:
            use_selenium: True pour les sites dynamiques (JavaScript),
                         False pour les sites statiques (par défaut, utilise requests)
        
        Returns:
            Un objet BeautifulSoup ou None en cas d'erreur
        """
        if use_selenium:
            html = self.fetch_with_selenium(self.source_url)
        else:
            html = self.fetch_html(self.source_url)
        
        if html:
            return BeautifulSoup(html, "html.parser")
        
        logger.error(f"❌ Impossible de récupérer le contenu de {self.source_url}")
        return None

    def parse(self, soup: BeautifulSoup) -> list[dict]:
        """
        MÉTHODE ABSTRAITE : Doit être surchargée par chaque parser spécifique.
        Retourne une liste de dictionnaires contenant UNIQUEMENT les métadonnées (CDC Section 3).
        
        Args:
            soup: Objet BeautifulSoup contenant le HTML parsé
        
        Returns:
            Liste de dictionnaires représentant les offres extraites
        """
        raise NotImplementedError("Chaque site doit implémenter sa logique de parsing dans offers/scraping/parsers/")

    def run(self) -> list[dict]:
        """Pipeline d'exécution sécurisé et respectueux du rate-limiting"""
        logger.info(f"🕷️ Démarrage du scraping pour {self.source_url}")
        
        # Récupération du HTML (méthode standard pour sites statiques)
        html = self.fetch_html(self.source_url)
        if not html:
            logger.warning(f"⚠️ Aucun contenu récupéré pour {self.source_url}")
            return []
        
        # Respect du rate-limiting (CDC Section 1.b)
        time.sleep(self.delay)
        
        # Parsing et extraction des offres
        soup = BeautifulSoup(html, "html.parser")
        return self.parse(soup)