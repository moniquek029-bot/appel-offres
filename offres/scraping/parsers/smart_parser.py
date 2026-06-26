# offres/scraping/parsers/smart_parser.py
import re
import logging
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import date
from offres.scraping.site_validator import SiteValidator, is_valid_offer_title, is_rejected_content

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url, parse_french_date, detecter_pays
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

# Détection de Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
    logger.info(" Selenium disponible")
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning(" Selenium non installé. Installez avec: pip install selenium webdriver-manager")

# Configuration globale pour accélérer Playwright
PLAYWRIGHT_TIMEOUT = 15000  # 15 secondes au lieu de 30
PLAYWRIGHT_WAIT_UNTIL = "domcontentloaded"  # Plus rapide que "networkidle"

class SmartParser(BaseScraper):
    """Parser intelligent avec support Selenium anti-détection"""
    
    MOTS_CLES_DOCUMENTS = [
        'tdr', 'termes de référence', 'document de référence',
        'cahier des charges', 'dossier de consultation',
        'terms of reference', 'bidding document', 'rfp', 'rfq',
        'télécharger', 'download', 'attachment', 'annex',
    ]
    
    EXTENSIONS_DOCUMENTS = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip']
    
    MOTS_CLES_OFFRES = [
        'appel', 'offre', 'tender', 'consultation', 'avis', 'marché',
        'recrutement', 'procurement', 'rfp', 'rfq', 'projet', 'subvention',
    ]
    
    def __init__(self, source_url: str, use_js: bool = False, **kwargs):
        super().__init__(source_url, **kwargs)
        self.base_domain = urlparse(source_url).netloc
        self.use_js = use_js and SELENIUM_AVAILABLE
        self.driver = None
    
    def _init_driver(self):
        """Initialise le driver Selenium avec configuration anti-détection"""
        if self.driver:
            return
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Masquer webdriver
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info(" Driver Selenium initialisé")
        except Exception as e:
            logger.error(f" Erreur initialisation Selenium: {e}")
            self.driver = None
    
    def _close_driver(self):
        """Ferme le driver Selenium"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def fetch_html_smart(self, url: str) -> BeautifulSoup | None:
        """Récupère le HTML avec Selenium si activé, sinon requests"""
        if self.use_js and SELENIUM_AVAILABLE:
            try:
                self._init_driver()
                if not self.driver:
                    return None
                
                logger.info(f" Selenium: Chargement {url[:80]}...")
                self.driver.get(url)
                time.sleep(3)  # Attendre le chargement
                
                html = self.driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                logger.info(f" HTML récupéré ({len(html)} chars)")
                return soup
                
            except Exception as e:
                logger.error(f" Erreur Selenium: {e}")
                return None
        else:
            # Fallback sur la méthode standard
            return self.fetch_and_parse(use_js=False)
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        """Extrait les offres de la page"""
        offres = []
        conteneurs = self._trouver_conteneurs(soup)
        
        logger.info(f" {len(conteneurs)} conteneurs détectés")
        
        for conteneur in conteneurs:
            try:
                titre = self._extraire_titre(conteneur)
                if not titre or len(titre) < 15:
                    continue
                
                if not self._est_une_offre(titre):
                    continue
                
                url_source = self._extraire_lien(conteneur)
                if not url_source:
                    continue
                
                organisme = self._extraire_organisme(conteneur) or self.base_domain
                date_cloture = self._extraire_date(conteneur)
                description = self._extraire_description(conteneur)
                pays = self._detecter_pays(titre + ' ' + description)
                
                offre = {
                    'titre': clean_text(titre)[:300],
                    'organisme': clean_text(organisme)[:200],
                    'description': description[:1000],
                    'date_publication': date.today(),
                    'date_cloture': date_cloture,
                    'url_source': url_source,
                    'url_tdr': None,
                    'pays': pays,
                    'statut': 'Ouvert',
                    'mode_acquisition': 'AUTO',
                }
                
                offres.append(offre)
                
            except Exception as e:
                logger.debug(f" Erreur parsing: {e}")
                continue
        
        logger.info(f" {len(offres)} offre(s) extraite(s)")
        return offres[:50]
    
    def _est_une_offre(self, texte: str) -> bool:
        texte_lower = texte.lower()
        return any(mot in texte_lower for mot in self.MOTS_CLES_OFFRES) or len(texte) > 30
    
    def _detecter_pays(self, texte: str) -> str:
        try:
            return detecter_pays(texte, self.pays_defaut)
        except:
            return self.pays_defaut
    
    def _trouver_conteneurs(self, soup: BeautifulSoup) -> list:
        selecteurs = [
            'div.offre', 'div.offer', 'div.tender', 'article',
            'div.item', 'div.card', '.views-row', '.node',
            'table tbody tr', 'div.search-result',
        ]
        
        for selecteur in selecteurs:
            trouves = soup.select(selecteur)
            if len(trouves) >= 2:
                return trouves
        
        # Fallback : liens longs
        conteneurs = []
        for link in soup.find_all('a', href=True):
            texte = link.get_text(strip=True)
            if len(texte) > 35 and self._est_une_offre(texte):
                parent = link.find_parent(['div', 'article', 'li', 'tr'])
                if parent and parent not in conteneurs:
                    conteneurs.append(parent)
        
        return conteneurs
    
    def _extraire_titre(self, conteneur) -> str:
        for sel in ['h1', 'h2', 'h3', 'h4', 'h5', '.title', 'a.title']:
            elem = conteneur.select_one(sel)
            if elem:
                texte = elem.get_text(strip=True)
                if len(texte) > 10:
                    return texte
        
        liens = conteneur.find_all('a', href=True)
        if liens:
            liens_tries = sorted(liens, key=lambda x: len(x.get_text(strip=True)), reverse=True)
            return liens_tries[0].get_text(strip=True)
        
        return conteneur.get_text(strip=True)[:200]
    
    def _extraire_lien(self, conteneur) -> str | None:
        for link in conteneur.find_all('a', href=True):
            href = link.get('href', '').strip()
            texte = link.get_text().lower()
            
            if href and not href.startswith('#') and not href.startswith('javascript:'):
                if any(kw in texte for kw in self.MOTS_CLES_OFFRES):
                    return urljoin(self.base_url, href)
        
        for link in conteneur.find_all('a', href=True):
            href = link.get('href', '').strip()
            if href and not href.startswith('#') and not href.startswith('javascript:'):
                if not any(href.lower().endswith(ext) for ext in self.EXTENSIONS_DOCUMENTS):
                    return urljoin(self.base_url, href)
        
        return None
    
    def _extraire_organisme(self, conteneur) -> str | None:
        for sel in ['.company', '.organization', '.buyer', '.author']:
            elem = conteneur.select_one(sel)
            if elem and len(elem.get_text(strip=True)) > 3:
                return elem.get_text(strip=True)
        return None
    
    def _extraire_date(self, conteneur) -> date:
        for sel in ['.date', '.deadline', '.closing', '.cloture', 'time']:
            elem = conteneur.select_one(sel)
            if elem:
                return parse_french_date(elem.get_text(strip=True))
        return parse_french_date(conteneur.get_text())
    
    def _extraire_description(self, conteneur) -> str:
        paragraphes = conteneur.find_all('p')
        if paragraphes:
            texte = ' '.join(p.get_text(strip=True) for p in paragraphes[:3])
            if len(texte) > 50:
                return clean_text(texte)[:1000]
        return clean_text(conteneur.get_text())[:1000]
    
    def _trouver_pdf_dans_page(self, soup: BeautifulSoup, base_url: str) -> str | None:
        """Détecte les PDF/TDR dans la page"""
        candidats = []
        
        # Liens directs vers PDF
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').strip()
            if href.lower().endswith('.pdf'):
                full_url = urljoin(base_url, href)
                if not any(mot in href.lower() for mot in ['logo', 'favicon', 'icon']):
                    candidats.append((100, full_url))
        
        # Liens avec mots-clés
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').strip()
            texte = link.get_text(strip=True).lower()
            
            if not href or href.startswith('#'):
                continue
            
            if any(mot in texte for mot in self.MOTS_CLES_DOCUMENTS):
                if not any(mot in href.lower() for mot in ['accueil', 'home', 'contact']):
                    score = 80
                    if 'tdr' in texte or 'terms of reference' in texte:
                        score = 95
                    candidats.append((score, urljoin(base_url, href)))
        
        # Trier par score
        candidats.sort(key=lambda x: x[0], reverse=True)
        
        if candidats:
            return candidats[0][1]
        
        return None
    
    # Dans offres/scraping/parsers/smart_parser.py

# Ajouter en haut du fichier :

# Modifier la méthode run() :
def run(self) -> list[dict]:
    """Exécute le scraping complet avec validation du site"""
    logger.info(f"🕷️ SmartParser: {self.source_url}")
    logger.info(f"🔍 Mode JS: {'✅ Selenium' if self.use_js else '❌ Désactivé'}")
    
    try:
        # ✅ ÉTAPE 1 : VALIDER LE SITE AVANT DE SCRAPER
        logger.info(f"🔍 Validation du site: {self.source_url}")
        soup_check = self.fetch_html_smart(self.source_url)
        
        if not soup_check:
            logger.error("❌ Impossible de récupérer la page")
            return []
        
        # Valider le site
        validator = SiteValidator(soup=soup_check, url=self.source_url)
        validation = validator.validate()
        
        if not validation['is_valid']:
            logger.warning(f"❌ Site REJETÉ - Score: {validation['score']}, Confiance: {validation['confidence']}")
            logger.warning(f"   Raisons: {validation['rejection_reasons']}")
            logger.warning(f"   Ce site ne semble pas publier d'appels d'offres")
            return []
        
        logger.info(f"✅ Site VALIDÉ - Score: {validation['score']}, Confiance: {validation['confidence']}")
        
        # ✅ ÉTAPE 2 : PARSER LES OFFRES
        soup = soup_check
        offres = self.parse(soup)
        
        if not offres:
            logger.warning("⚠️ Aucune offre extraite")
            return []
        
        # ✅ ÉTAPE 3 : VALIDER CHAQUE OFFRE INDIVIDUELLEMENT
        offres_valides = []
        for offre in offres:
            titre = offre.get('titre', '')
            
            # Vérifier si le titre correspond à un appel d'offres
            if not is_valid_offer_title(titre):
                logger.debug(f"⏭️ Offre rejetée (titre non-valide): {titre[:50]}...")
                continue
            
            # Vérifier si le contenu n'est pas du contenu non-offre
            description = offre.get('description', '')
            if is_rejected_content(titre + ' ' + description):
                logger.debug(f"⏭️ Offre rejetée (contenu non-offre): {titre[:50]}...")
                continue
            
            offres_valides.append(offre)
        
        logger.info(f"📊 Offres valides: {len(offres_valides)}/{len(offres)}")
        
        if not offres_valides:
            logger.warning("⚠️ Aucune offre valide après filtrage")
            return []
        
        # ✅ ÉTAPE 4 : CHERCHER LES PDFs
        logger.info(f"📄 Recherche de documents pour {len(offres_valides)} offres...")
        
        for i, offre in enumerate(offres_valides, 1):
            if offre.get('url_source'):
                try:
                    time.sleep(random.uniform(1, 2))
                    logger.info(f"  [{i}/{len(offres_valides)}] {offre['titre'][:50]}...")
                    
                    detail_soup = self.fetch_html_smart(offre['url_source'])
                    
                    if detail_soup:
                        pdf_url = self._trouver_pdf_dans_page(detail_soup, offre['url_source'])
                        if pdf_url:
                            offre['url_tdr'] = pdf_url
                            logger.info(f"     📄 Document: {pdf_url[:80]}...")
                except Exception as e:
                    logger.debug(f"    ❌ Erreur: {e}")
        
        avec_doc = sum(1 for o in offres_valides if o.get('url_tdr'))
        logger.info(f"✅ Résultat: {len(offres_valides)} offres valides, {avec_doc} avec document")
        
        return offres_valides
        
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []
    finally:
        self._close_driver()