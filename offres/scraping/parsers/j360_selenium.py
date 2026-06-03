# offres/scraping/parsers/j360_selenium.py
"""
PARSER SELENIUM POUR APP.J360.INFO (SPA DYNAMIQUE + AUTHENTIFICATION)
✅ CORRIGÉ : Extraction PDF + parse_detail_page() + Structure cohérente
"""

import logging
import time
import pickle
from pathlib import Path
from urllib.parse import urljoin
from datetime import date, timedelta

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from ..base import BaseScraper
from ..utils import clean_text, parse_french_date, normalize_url, get_first_pdf_url, is_valid_pdf_url

logger = logging.getLogger(__name__)


class J360SeleniumParser(BaseScraper):
    """Parser Selenium avec persistance de session via cookies."""
    
    def __init__(self, source_url: str, delay_seconds: int = 5, max_retries: int = 2, base_url: str = "https://app.j360.info", pays_defaut: str = 'BF', **kwargs):
        super().__init__(source_url, delay_seconds, max_retries, **kwargs)
        self.base_url = base_url
        self.pays_defaut = pays_defaut
        self.cookie_path = Path("offres/scraping/parsers/j360_cookies.pkl")
        self.user_data_dir = r"C:\Users\sebas\chrome-scraper-profile"

    def _setup_driver(self):
        """Configure Chrome avec profil dédié et options stables."""
        options = Options()
        options.add_argument(f"--user-data-dir={self.user_data_dir}")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")  # Mode headless pour serveur
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    def _save_cookies(self, driver):
        with open(self.cookie_path, "wb") as f:
            pickle.dump(driver.get_cookies(), f)
        logger.info("✅ Cookies sauvegardés")

    def _load_cookies(self, driver):
        if not self.cookie_path.exists():
            return False
        try:
            with open(self.cookie_path, "rb") as f:
                cookies = pickle.load(f)
            driver.get("https://app.j360.info")
            time.sleep(2)
            for cookie in cookies:
                try:
                    if "domain" in cookie and cookie["domain"].startswith("."):
                        cookie["domain"] = cookie["domain"][1:]
                    cookie.pop("sameSite", None)
                    cookie.pop("httpOnly", None)
                    driver.add_cookie(cookie)
                except:
                    continue
            driver.refresh()
            time.sleep(3)
            return True
        except:
            return False
        
    def _wait_for_dynamic_content(self, driver, timeout=30):
        try:
            wait = WebDriverWait(driver, timeout)
            wait.until(lambda d: d.current_url.startswith("https://app.j360.info"))
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "q-page")))
            time.sleep(5)
            cards = driver.find_elements(By.CSS_SELECTOR, ".q-card")
            if len(cards) == 0:
                with open("debug_j360.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                return False
            return True
        except:
            return False

    def parse(self, soup=None):
        driver = None
        offres = []
        
        try:
            logger.info(f"🌐 Lancement Chrome avec profil dédié...")
            driver = self._setup_driver()
            
            if not self._load_cookies(driver):
                logger.info("🔐 PREMIÈRE EXÉCUTION : Connectez-vous manuellement")
                driver.get(self.source_url)
                print("\n⏳ En attente de votre connexion manuelle...")
                print("💡 Une fois connecté, appuyez sur ENTRÉE dans ce terminal.")
                input()
                self._save_cookies(driver)
            
            driver.get(self.source_url)
            if not self._wait_for_dynamic_content(driver):
                return []
            
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            
            containers = soup.select(".q-card")
            if len(containers) == 0:
                containers = soup.select(".q-list > .q-item, .tender-list > div, [data-testid*='offer']")
            
            for container in containers:
                try:
                    titre_tag = container.select_one(".text-h6")
                    titre = clean_text(titre_tag.text) if titre_tag else "Offre sans titre"
                    
                    lien_tag = container.select_one("a, [href], router-link")
                    url_relative = lien_tag.get("href") if lien_tag else None
                    if not url_relative:
                        parent_link = container.find_parent("a") or container.find_parent("[href]")
                        url_relative = parent_link.get("href") if parent_link else None
                    url_source = normalize_url(url_relative, self.base_url) if url_relative else None
                    
                    pays_tag = container.select_one(".q-chip span:last-child")
                    pays = clean_text(pays_tag.text) if pays_tag else self.pays_defaut
                    
                    if url_source:
                        offres.append({
                            "titre": titre,
                            "organisme": "Non précisé",
                            "description": "",
                            "date_publication": date.today(),
                            "date_cloture": date.today() + timedelta(days=30),
                            "url_source": url_source,
                            "url_tdr": None,  # Sera extrait par parse_detail_page
                            "pays": pays,
                            "statut": "Ouvert",
                            "mode_acquisition": "AUTO",
                        })
                except Exception as e:
                    logger.debug(f"⚠️ Ligne ignorée : {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Erreur Selenium : {type(e).__name__} - {e}")
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
        
        logger.info(f"✅ {len(offres)} offre(s) extraite(s)")
        return offres

    def parse_detail_page(self, soup: BeautifulSoup, base_url: str) -> dict | None:
        """Extrait le lien PDF depuis la page détail j360 Selenium"""
        try:
            url_tdr = get_first_pdf_url(soup, base_url)
            if url_tdr and is_valid_pdf_url(url_tdr):
                return {'url_tdr': url_tdr}
            
            # Chercher dans les sections Quasar spécifiques
            doc_section = soup.select_one('.q-expansion-item, .documents, .attachments')
            if doc_section:
                pdf_link = doc_section.select_one('a[href*=".pdf"]')
                if pdf_link:
                    return {'url_tdr': normalize_url(pdf_link['href'], base_url)}
            
            return None
        except Exception as e:
            logger.warning(f"⚠️ Erreur parse_detail_page j360 Selenium: {e}")
            return None

    def run(self):
        """Surcharge : applique rate-limiting via BaseScraper."""
        time.sleep(self.delay)
        return self.parse()