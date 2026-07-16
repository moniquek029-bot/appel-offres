# offres/scraping/auth_scrapers/authenticated_scraper.py
"""
Scraper pour sites nécessitant une authentification par formulaire HTML
"""
import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import date, timedelta

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url
from offres.scraping.extraction_helpers import extract_all_details, extract_pdf_url, is_offer_valid
from offres.utils.search_keywords import detecter_domaine, est_appel_offres
from offres.utils.offer_validator import is_valid_offer_title

logger = logging.getLogger(__name__)


class AuthenticatedScraper(BaseScraper):
    """
    Scraper avec authentification par formulaire HTML
    
    Utilisation :
        scraper = AuthenticatedScraper(
            source_url="https://example.com/offers",
            credentials={
                'username': 'user@example.com',
                'password': 'mypassword',
                'login_url': 'https://example.com/login',
                'username_field': 'email',
                'password_field': 'password',
            }
        )
        offers = scraper.run()
    """
    
    def __init__(self, source_url: str, credentials: dict = None, **kwargs):
        super().__init__(source_url, **kwargs)
        self.credentials = credentials or {}
        self.login_url = self.credentials.get('login_url')
        self.username_field = self.credentials.get('username_field', 'username')
        self.password_field = self.credentials.get('password_field', 'password')
        self.session = requests.Session()
        self.is_authenticated = False
        
        # Configuration session
        self.session.headers.update({
            'User-Agent': self.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr,fr-FR;q=0.9,en;q=0.8',
        })
    
    def login(self) -> bool:
        """
        Effectue la connexion au site via formulaire HTML
        Retourne True si succès, False sinon
        """
        if not self.login_url:
            logger.error("❌ URL de login non fournie")
            return False
        
        if not self.credentials.get('username') or not self.credentials.get('password'):
            logger.error("❌ Username ou password manquant")
            return False
        
        try:
            logger.info(f"🔐 Tentative de connexion à {self.login_url}")
            
            # Étape 1 : Récupérer la page de login (pour les tokens CSRF)
            login_page = self.session.get(self.login_url, verify=False, timeout=30)
            soup = BeautifulSoup(login_page.text, 'html.parser')
            
            # Étape 2 : Extraire le token CSRF si présent
            csrf_data = {}
            csrf_selectors = [
                {'name': 'csrfmiddlewaretoken'},
                {'name': '_token'},
                {'name': 'csrf_token'},
                {'name': 'authenticity_token'},
                {'name': '__RequestVerificationToken'},
            ]
            
            for selector in csrf_selectors:
                csrf_input = soup.find('input', selector)
                if csrf_input:
                    csrf_data[csrf_input.get('name')] = csrf_input.get('value')
                    break
            
            # Étape 3 : Préparer les données de login
            login_data = {
                self.username_field: self.credentials['username'],
                self.password_field: self.credentials['password'],
            }
            login_data.update(csrf_data)
            
            # Étape 4 : Envoyer le formulaire
            headers = {
                'Referer': self.login_url,
                'Origin': urlparse(self.login_url).scheme + '://' + urlparse(self.login_url).netloc,
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            
            response = self.session.post(
                self.login_url,
                data=login_data,
                headers=headers,
                verify=False,
                allow_redirects=True,
                timeout=30
            )
            
            # Étape 5 : Vérifier le succès
            if response.status_code == 200:
                # Vérifier si on est bien connecté
                response_text = response.text.lower()
                
                # Indicateurs de succès
                success_indicators = ['logout', 'déconnexion', 'mon compte', 'my account', 'profile']
                failure_indicators = ['invalid password', 'mot de passe incorrect', 'login failed', 'erreur']
                
                has_success = any(ind in response_text for ind in success_indicators)
                has_failure = any(ind in response_text for ind in failure_indicators)
                
                if has_success and not has_failure:
                    self.is_authenticated = True
                    logger.info("✅ Connexion réussie")
                    return True
                elif 'login' not in response.url.lower():
                    # Si l'URL a changé, c'est probablement réussi
                    self.is_authenticated = True
                    logger.info("✅ Connexion réussie (redirection détectée)")
                    return True
            
            logger.warning(f"⚠️ Échec de connexion: Status {response.status_code}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erreur de connexion: {e}")
            return False
    
    def fetch_page(self, url: str, use_js: bool = False) -> BeautifulSoup | None:
        """Récupère une page en utilisant la session authentifiée"""
        if not self.is_authenticated:
            if not self.login():
                return None
        
        try:
            for attempt in range(1, self.MAX_RETRIES + 1):
                try:
                    response = self.session.get(url, verify=False, timeout=self.TIMEOUT)
                    
                    if response.status_code == 200:
                        return BeautifulSoup(response.text, 'html.parser')
                    elif response.status_code == 401 or response.status_code == 403:
                        logger.warning(f"⚠️ Session expirée, reconnexion...")
                        if self.login():
                            continue
                        return None
                    else:
                        logger.warning(f"⚠️ Status HTTP {response.status_code}")
                        return None
                        
                except Exception as e:
                    logger.warning(f"⚠️ Tentative {attempt} échouée: {e}")
                    if attempt < self.MAX_RETRIES:
                        import time
                        time.sleep(self.RETRY_DELAY * attempt)
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur fetch: {e}")
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
        logger.info(f"🔐 Scraping authentifié: {self.source_url}")
        
        try:
            # Connexion
            if not self.login():
                logger.error("❌ Connexion échouée, arrêt du scraping")
                return []
            
            # Récupérer la page principale
            soup = self.fetch_and_parse()
            if not soup:
                return []
            
            return self.parse(soup)
            
        except Exception as e:
            logger.error(f"❌ Erreur scraping authentifié: {e}")
            return []