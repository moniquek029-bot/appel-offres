"""
offres/scraping/parsers/j360_selenium.py
=================================================================
PARSER SELENIUM POUR APP.J360.INFO (SPA DYNAMIQUE + AUTHENTIFICATION)
Conforme CDC : Selenium pour sites dynamiques, métadonnées uniquement, 
rate-limiting, redirection vers source officielle.
=================================================================
"""

import logging
import time
import pickle
from pathlib import Path
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from ..base import BaseScraper
from ..utils import clean_text, parse_french_date, normalize_url

logger = logging.getLogger(__name__)

class J360SeleniumParser(BaseScraper):
    """Parser Selenium avec persistance de session via cookies."""
    
    def __init__(self, source_url: str, delay_seconds: int = 5, max_retries: int = 2):
        super().__init__(source_url, delay_seconds, max_retries)
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
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    def _save_cookies(self, driver):
        """Sauvegarde les cookies pour réutilisation automatique."""
        with open(self.cookie_path, "wb") as f:
            pickle.dump(driver.get_cookies(), f)
        logger.info("✅ Cookies sauvegardés pour les prochaines exécutions")

    def _load_cookies(self, driver):
        """Restaure les cookies avec gestion des erreurs Quasar/Vue."""
        if not self.cookie_path.exists():
            logger.info("🍪 Aucun fichier de cookies trouvé → première exécution")
            return False
        
        try:
            with open(self.cookie_path, "rb") as f:
                cookies = pickle.load(f)
            
            # Naviguer d'abord vers le domaine pour pouvoir ajouter les cookies
            driver.get("https://app.j360.info")
            time.sleep(2)
            
            added = 0
            for cookie in cookies:
                try:
                    # Nettoyer le domaine si nécessaire
                    if "domain" in cookie and cookie["domain"].startswith("."):
                        cookie["domain"] = cookie["domain"][1:]
                    # Supprimer les champs incompatibles avec Selenium
                    cookie.pop("sameSite", None)
                    cookie.pop("httpOnly", None)  # Selenium ne peut pas ajouter les cookies httpOnly
                    driver.add_cookie(cookie)
                    added += 1
                except Exception as e:
                    logger.debug(f"⚠️ Cookie ignoré : {e}")
            
            logger.info(f"🔑 {added}/{len(cookies)} cookies restaurés")
            
            # Rafraîchir pour appliquer les cookies
            driver.refresh()
            time.sleep(3)  # Attendre le re-rendu Vue.js
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Échec restauration cookies : {e}")
            return False
        
    def _wait_for_dynamic_content(self, driver, timeout=30):  # ← Timeout augmenté à 30s
        """Attend que le JavaScript charge les offres + DEBUG affiché."""
        try:
            wait = WebDriverWait(driver, timeout)
            
            # Attendre que l'URL soit stable (évite les redirections)
            wait.until(lambda d: d.current_url.startswith("https://app.j360.info"))
            
            # Attendre un élément Quasar générique (plus fiable que .q-card)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "q-page")))
            
            # Pause supplémentaire pour le rendu JS
            time.sleep(5)
            
            # DEBUG : Compter les .q-card réellement présents
            cards = driver.find_elements(By.CSS_SELECTOR, ".q-card")
            logger.info(f"🔍 DEBUG : {len(cards)} éléments .q-card trouvés dans le DOM")
            
            if len(cards) == 0:
                # Sauvegarder le HTML pour analyse
                with open("debug_j360.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                logger.warning("⚠️ Aucun .q-card trouvé. HTML sauvegardé dans debug_j360.html")
                return False
                
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Timeout ou erreur : {e}")
            # Sauvegarder le HTML même en cas d'erreur
            try:
                with open("debug_j360_error.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                logger.info("📄 HTML d'erreur sauvegardé dans debug_j360_error.html")
            except:
                pass
            return False

    def parse(self, soup=None):
        driver = None
        offres = []
        
        try:
            logger.info(f"🌐 Lancement Chrome avec profil dédié...")
            driver = self._setup_driver()
            
            if not self._load_cookies(driver):
                logger.info("🔐 PREMIÈRE EXÉCUTION : Connectez-vous sur app.j360.info")
                driver.get(self.source_url)
                print("\n⏳ En attente de votre connexion manuelle...")
                print("💡 Une fois connecté, appuyez sur ENTRÉE dans ce terminal.")
                input()
                self._save_cookies(driver)
            
            driver.get(self.source_url)
            
            if not self._wait_for_dynamic_content(driver):
                return []
            
                        # 🔍 Conteneurs d'offres (Quasar)
            containers = soup.select(".q-card")
            
            # Fallback si 0 .q-card : essayer d'autres sélecteurs Quasar courants
            if len(containers) == 0:
                logger.info("🔄 Fallback : tentative avec d'autres sélecteurs Quasar...")
                containers = soup.select(".q-list > .q-item, .tender-list > div, [data-testid*='offer'], .offer-list > *")
            
            logger.info(f"🔍 {len(containers)} conteneurs détectés après fallback")
            
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            
            # 🔍 Conteneurs d'offres (Quasar)
            containers = soup.select(".q-card")
            logger.info(f"🔍 {len(containers)} cartes Quasar détectées")
            
            for container in containers:
                try:
                    titre_tag = container.select_one(".text-h6")
                    titre = clean_text(titre_tag.text) if titre_tag else "Offre sans titre"
                    
                    lien_tag = container.select_one("a, [href], router-link")
                    url_relative = lien_tag.get("href") if lien_tag else None
                    
                    if not url_relative:
                        parent_link = container.find_parent("a") or container.find_parent("[href]")
                        url_relative = parent_link.get("href") if parent_link else None
                    
                    url_tdr = normalize_url(url_relative, self.source_url) if url_relative else None
                    
                    pays_tag = container.select_one(".q-chip span:last-child")
                    pays = clean_text(pays_tag.text) if pays_tag else "BF"
                    
                    if url_tdr:
                        offres.append({
                            "titre": titre,
                            "organisme": "Non précisé",
                            "description": "",
                            "date_publication": None,
                            "date_cloture": None,
                            "url_tdr": url_tdr,
                            "pays": pays
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
        
        # ✅ CORRECTION CRITIQUE : Retourner la liste des offres
        logger.info(f"✅ {len(offres)} offre(s) extraite(s) | Conforme CDC")
        return offres

    def run(self):
        """Surcharge : applique rate-limiting via BaseScraper."""
        time.sleep(self.delay)
        return self.parse()