# offres/scraping/auth_scrapers/selenium_scraper.py
"""
Scraper avec Selenium pour sites JavaScript complexes avec authentification
"""
import logging
import time
from urllib.parse import urljoin, urlparse
from datetime import date, timedelta

from bs4 import BeautifulSoup

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url
from offres.scraping.extraction_helpers import extract_all_details, extract_pdf_url, is_offer_valid
from offres.utils.search_keywords import detecter_domaine, est_appel_offres
from offres.utils.offer_validator import is_valid_offer_title

logger = logging.getLogger(__name__)


class SeleniumScraper(BaseScraper):
    """
    Scraper avec Selenium pour sites JavaScript complexes
    
    Utilisation :
        scraper = SeleniumScraper(
            source_url="https://example.com/offers",
            credentials={
                'username': 'user@example.com',
                'password': 'mypassword',
                'login_url': 'https://example.com/login',
                'username_selector': '#email',
                'password_selector': '#password',
                'submit_selector': 'button[type=submit]',
                'success_indicator': '.user-menu',
            }
        )
        offers = scraper.run()
    """
    
    def __init__(self, source_url: str, credentials: dict = None, **kwargs):
        super().__init__(source_url, **kwargs)
        self.credentials = credentials or {}
        self.login_url = self.credentials.get('login_url')
        self.driver = None
        self.is_authenticated = False
        
        # Sélecteurs CSS
        self.username_selector = self.credentials.get('username_selector', 'input[name="username"], input[name="email"], #username, #email')
        self.password_selector = self.credentials.get('password_selector', 'input[name="password"], input[type="password"], #password')
        self.submit_selector = self.credentials.get('submit_selector', 'button[type="submit"], input[type="submit"], .login-button')
        self.success_indicator = self.credentials.get('success_indicator', '')
    
    def setup_driver(self):
        """Configure le driver Selenium"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            # Configuration Chrome
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Mode sans interface
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument(f'user-agent={self.USER_AGENT}')
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Démarrer le driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
            
            logger.info("✅ Driver Selenium configuré")
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration Selenium: {e}")
            raise
    
    def login(self) -> bool:
        """Effectue la connexion via Selenium"""
        if not self.login_url:
            logger.error("❌ URL de login non fournie")
            return False
        
        try:
            if not self.driver:
                self.setup_driver()
            
            logger.info(f"🔐 Connexion Selenium à {self.login_url}")
            
            # Aller à la page de login
            self.driver.get(self.login_url)
            time.sleep(2)  # Attendre le chargement
            
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            wait = WebDriverWait(self.driver, 10)
            
            # Trouver et remplir le champ username
            username_selectors = self.username_selector.split(',')
            username_field = None
            for selector in username_selectors:
                try:
                    username_field = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector.strip()))
                    )
                    if username_field:
                        break
                except:
                    continue
            
            if not username_field:
                logger.error("❌ Champ username non trouvé")
                return False
            
            # Trouver et remplir le champ password
            password_selectors = self.password_selector.split(',')
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector.strip())
                    if password_field:
                        break
                except:
                    continue
            
            if not password_field:
                logger.error("❌ Champ password non trouvé")
                return False
            
            # Remplir les champs
            username_field.clear()
            username_field.send_keys(self.credentials['username'])
            time.sleep(0.5)
            
            password_field.clear()
            password_field.send_keys(self.credentials['password'])
            time.sleep(0.5)
            
            # Trouver et cliquer le bouton submit
            submit_selectors = self.submit_selector.split(',')
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, selector.strip())
                    if submit_button:
                        break
                except:
                    continue
            
            if submit_button:
                submit_button.click()
            else:
                # Fallback : soumettre le formulaire
                password_field.submit()
            
            # Attendre la connexion
            time.sleep(3)
            
            # Vérifier le succès
            if self.success_indicator:
                try:
                    wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, self.success_indicator))
                    )
                    self.is_authenticated = True
                    logger.info("✅ Connexion Selenium réussie")
                    return True
                except:
                    logger.warning("⚠️ Indicateur de succès non trouvé")
            
            # Vérification alternative : URL a changé
            current_url = self.driver.current_url
            if self.login_url not in current_url:
                self.is_authenticated = True
                logger.info("✅ Connexion Selenium réussie (redirection détectée)")
                return True
            
            logger.warning("⚠️ Connexion incertaine")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erreur connexion Selenium: {e}")
            return False
    
    def fetch_page(self, url: str, use_js: bool = True) -> BeautifulSoup | None:
        """Récupère une page avec Selenium"""
        if not self.is_authenticated:
            if not self.login():
                return None
        
        try:
            if not self.driver:
                self.setup_driver()
            
            self.driver.get(url)
            time.sleep(2)  # Attendre le chargement JavaScript
            
            # Récupérer le HTML après exécution JavaScript
            html = self.driver.page_source
            return BeautifulSoup(html, 'html.parser')
            
        except Exception as e:
            logger.error(f"❌ Erreur fetch Selenium: {e}")
            return None
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        """Parse la page et retourne les offres"""
        offers = []
        
        if not soup:
            return offers
        
        # Chercher les liens vers les offres
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            titre = link.get_text(strip=True)
            
            if not titre or len(titre) < 15:
                continue
            
            # Filtrer les liens pertinents
            if not any(kw in href.lower() for kw in ['offer', 'tender', 'procurement', 'appel', 'offre']):
                continue
            
            offre_url = urljoin(self.source_url, href)
            
            # Visiter la page de détail
            detail_soup = self.fetch_page(offre_url)
            if not detail_soup:
                continue
            
            # Extraire les détails
            details = extract_all_details(
                detail_soup,
                url=offre_url,
                pays_defaut=self.pays_defaut,
                titre=titre,
                description=titre
            )
            
            # Validation
            if not est_appel_offres(titre, titre):
                continue
            
            # Détection du domaine
            domaine = detecter_domaine(titre)
            if details.get('domaine') and details.get('domaine') != 'Autres':
                domaine = details.get('domaine')
            
            offer = {
                'titre': clean_text(titre)[:300],
                'organisme': urlparse(self.source_url).netloc,
                'description': clean_text(titre)[:1000],
                'date_publication': details.get('date_publication'),
                'date_cloture': details.get('date_cloture'),
                'url_source': offre_url,
                'url_tdr': details.get('url_tdr') or offre_url,
                'pays': details.get('pays', self.pays_defaut),
                'domaine': domaine,
                'statut': 'Ouvert',
                'type_offre': 'APPEL_D_OFFRES',
                'mode_acquisition': 'AUTO',
            }
            
            # Validation finale
            is_valid, reason = is_offer_valid(offer)
            if is_valid:
                offers.append(offer)
                logger.info(f"   ✅ {titre[:60]}")
        
        return offers
    
    def run(self) -> list[dict]:
        """Exécute le scraping complet"""
        logger.info(f"🔐 Scraping Selenium: {self.source_url}")
        
        try:
            # Connexion
            if not self.login():
                logger.error("❌ Connexion Selenium échouée")
                return []
            
            # Récupérer la page principale
            soup = self.fetch_page(self.source_url)
            if not soup:
                return []
            
            return self.parse(soup)
            
        except Exception as e:
            logger.error(f"❌ Erreur scraping Selenium: {e}")
            return []
        finally:
            # Fermer le driver
            if self.driver:
                try:
                    self.driver.quit()
                    logger.info("✅ Driver Selenium fermé")
                except:
                    pass