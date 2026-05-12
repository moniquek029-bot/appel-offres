"""
offres/scraping/base.py
Moteur de scraping conforme au CDC :
- Section 4.a : Utilisation de requests + BeautifulSoup pour sites statiques
- Section 1.b : Respect des robots.txt & limitation de fréquence
- Section 3 : Modularité pour faciliter les mises à jour
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
        self.delay = delay_seconds  #  CDC: Évite la surcharge des serveurs sources
        self.session = requests.Session()
        
        #  Headers réalistes pour éviter les blocages basiques
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; TendersBot/1.0; +https://votre-domaine.com/bot)"
        })
        
        #  Stratégie de retry automatique (429, 5xx)
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
            logger.info(f" robots.txt chargé pour {self.source_url}")
        except Exception as e:
            logger.warning(f" Impossible de lire robots.txt : {e}")

    def is_allowed(self, path: str) -> bool:
        """Vérifie si le scraping est autorisé pour un chemin donné"""
        return self.robot_parser.can_fetch("*", path)

    def fetch_html(self, url: str) -> str | None:
        """Récupère le HTML avec timeout et gestion d'erreurs réseau"""
        if not self.is_allowed("/"):
            logger.warning(f" Scraping bloqué par robots.txt pour {url}")
            return None
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f" Erreur HTTP pour {url} : {e}")
            return None

    def parse(self, soup: BeautifulSoup) -> list[dict]:
        """
         MÉTHODE ABSTRAITE : Doit être surchargée par chaque parser spécifique.
        Retourne une liste de dictionnaires contenant UNIQUEMENT les métadonnées (CDC Section 3).
        """
        raise NotImplementedError("Chaque site doit implémenter sa logique de parsing dans offers/scraping/parsers/")

    def run(self) -> list[dict]:
        """Pipeline d'exécution sécurisé et respectueux"""
        logger.info(f" Démarrage du scraping pour {self.source_url}")
        html = self.fetch_html(self.source_url)
        if not html:
            return []
        
        time.sleep(self.delay)  #  Rate-limiting CDC
        return self.parse(BeautifulSoup(html, "html.parser"))