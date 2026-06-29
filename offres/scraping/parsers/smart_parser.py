# offres/scraping/parsers/smart_parser.py
import re
import logging
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import date, timedelta

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url, parse_french_date
from offres.scraping.site_validator import SiteValidator, is_valid_offer_title, is_rejected_content
from offres.scraping.country_detector import detecter_pays_smart
from offres.scraping.constantes import detecter_domaine
from offres.scraping.extraction_helpers import is_offer_expired, extract_all_details

logger = logging.getLogger(__name__)

# Détection de Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
    logger.info("✅ Selenium disponible")
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning("⚠️ Selenium non installé. Installez avec: pip install selenium webdriver-manager")

# Configuration globale pour accélérer Playwright
PLAYWRIGHT_TIMEOUT = 15000
PLAYWRIGHT_WAIT_UNTIL = "domcontentloaded"


class SmartParser(BaseScraper):
    """Parser intelligent avec support Selenium anti-détection et validation"""
    
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
    
    # =========================================================================
    # SELENIUM - Initialisation et gestion du driver
    # =========================================================================
    
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
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("✅ Driver Selenium initialisé")
        except Exception as e:
            logger.error(f"❌ Erreur initialisation Selenium: {e}")
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
                
                logger.info(f"🌐 Selenium: Chargement {url[:80]}...")
                self.driver.get(url)
                time.sleep(3)
                
                html = self.driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                logger.info(f"✅ HTML récupéré ({len(html)} chars)")
                return soup
                
            except Exception as e:
                logger.error(f"❌ Erreur Selenium: {e}")
                return None
        else:
            return self.fetch_and_parse(use_js=False)
    
    # =========================================================================
    # DÉTECTION INTELLIGENTE DU PAYS
    # =========================================================================
    
    def _detecter_pays(self, texte: str, url: str = None) -> str:
        """Détection intelligente du pays avec le nouveau détecteur"""
        try:
            return detecter_pays_smart(
                texte, 
                url=url or self.source_url,
                pays_defaut=self.pays_defaut
            )
        except Exception as e:
            logger.debug(f"⚠️ Erreur détection pays: {e}")
            return self.pays_defaut
    
    # =========================================================================
    # EXTRACTION DES ÉLÉMENTS
    # =========================================================================
    
    def _est_une_offre(self, texte: str) -> bool:
        """Vérifie si le texte correspond à une offre"""
        texte_lower = texte.lower()
        return any(mot in texte_lower for mot in self.MOTS_CLES_OFFRES) or len(texte) > 30
    
    def _trouver_conteneurs(self, soup: BeautifulSoup) -> list:
        """Trouve les conteneurs d'offres dans la page"""
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
        """Extrait le titre d'un conteneur"""
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
        """Extrait le lien principal d'un conteneur"""
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
        """Extrait l'organisme émetteur"""
        for sel in ['.company', '.organization', '.buyer', '.author']:
            elem = conteneur.select_one(sel)
            if elem and len(elem.get_text(strip=True)) > 3:
                return elem.get_text(strip=True)
        return None
    
    def _extraire_date(self, conteneur) -> date:
        """Extrait la date de clôture"""
        for sel in ['.date', '.deadline', '.closing', '.cloture', 'time']:
            elem = conteneur.select_one(sel)
            if elem:
                return parse_french_date(elem.get_text(strip=True))
        return parse_french_date(conteneur.get_text())
    
    def _extraire_description(self, conteneur) -> str:
        """Extrait la description de l'offre"""
        paragraphes = conteneur.find_all('p')
        if paragraphes:
            texte = ' '.join(p.get_text(strip=True) for p in paragraphes[:3])
            if len(texte) > 50:
                return clean_text(texte)[:1000]
        return clean_text(conteneur.get_text())[:1000]
    
    def _trouver_pdf_dans_page(self, soup: BeautifulSoup, base_url: str) -> str | None:
        """Détecte les PDF/TDR dans la page de détail"""
        candidats = []
        
        # Liens directs vers PDF
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').strip()
            if href.lower().endswith('.pdf'):
                full_url = urljoin(base_url, href)
                if not any(mot in href.lower() for mot in ['logo', 'favicon', 'icon']):
                    candidats.append((100, full_url))
        
        # Liens avec mots-clés de documents
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
        
        candidats.sort(key=lambda x: x[0], reverse=True)
        
        if candidats:
            return candidats[0][1]
        
        return None
    
    # =========================================================================
    # PARSING PRINCIPAL
    # =========================================================================
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        """Extrait les offres de la page avec détection intelligente du pays et du domaine"""
        offres = []
        conteneurs = self._trouver_conteneurs(soup)
        
        logger.info(f"📦 {len(conteneurs)} conteneurs détectés")
        
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
                
                # ✅ DÉTECTION INTELLIGENTE DU PAYS
                texte_complet = titre + ' ' + description + ' ' + (organisme or '')
                pays = self._detecter_pays(texte_complet, url=url_source)
                
                # ✅ DÉTECTION DU DOMAINE
                domaine = detecter_domaine(texte_complet)
                
                offre = {
                    'titre': clean_text(titre)[:300],
                    'organisme': clean_text(organisme)[:200],
                    'description': description[:1000],
                    'date_publication': date.today(),
                    'date_cloture': date_cloture,
                    'url_source': url_source,
                    'url_tdr': None,
                    'pays': pays,
                    'domaine': domaine,  # ✅ DOMAINE DÉTECTÉ
                    'statut': 'Ouvert',
                    'mode_acquisition': 'AUTO',
                }
                
                offres.append(offre)
                
            except Exception as e:
                logger.debug(f"⚠️ Erreur parsing: {e}")
                continue
        
        logger.info(f"📊 {len(offres)} offre(s) extraite(s)")
        return offres[:50]
    
    # =========================================================================
    # MÉTHODE PRINCIPALE : RUN (avec validation du site et des offres)
    # =========================================================================
    
    def run(self) -> list[dict]:
        """Exécute le scraping complet avec validation du site et des offres"""
        logger.info(f"🕷️ SmartParser: {self.source_url}")
        logger.info(f"🔍 Mode JS: {'✅ Selenium' if self.use_js else '❌ Désactivé'}")
        
        try:
            # =================================================================
            # ÉTAPE 1 : VALIDER LE SITE AVANT DE SCRAPER
            # =================================================================
            logger.info(f"🔍 Validation du site: {self.source_url}")
            soup_check = self.fetch_html_smart(self.source_url)
            
            if not soup_check:
                logger.error("❌ Impossible de récupérer la page")
                return []
            
            validator = SiteValidator(soup=soup_check, url=self.source_url)
            validation = validator.validate()
            
            if not validation.get('is_valid', False):
                logger.warning(f"❌ Site REJETÉ - Score: {validation.get('score', 0)}, Confiance: {validation.get('confidence', 'low')}")
                logger.warning(f"   Raisons: {validation.get('rejection_reasons', [])}")
                logger.warning(f"   → Ce site ne semble pas publier d'appels d'offres")
                return []
            
            logger.info(f"✅ Site VALIDÉ - Score: {validation.get('score', 0)}, Confiance: {validation.get('confidence', 'low')}")
            
            # =================================================================
            # ÉTAPE 2 : PARSER LES OFFRES
            # =================================================================
            soup = soup_check
            offres = self.parse(soup)
            
            if not offres:
                logger.warning("⚠️ Aucune offre extraite")
                return []
            
            # =================================================================
            # ÉTAPE 3 : VALIDER CHAQUE OFFRE INDIVIDUELLEMENT
            # =================================================================
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
            
            # =================================================================
            # ÉTAPE 4 : CHERCHER LES PDFs ET AFFINER PAYS/DOMAINE DANS LES PAGES DE DÉTAIL
            # =================================================================
            logger.info(f"📄 Recherche de documents pour {len(offres_valides)} offres...")
            
            for i, offre in enumerate(offres_valides, 1):
                if offre.get('url_source'):
                    try:
                        time.sleep(random.uniform(1, 2))
                        logger.info(f"  [{i}/{len(offres_valides)}] {offre['titre'][:50]}...")
                        
                        detail_soup = self.fetch_html_smart(offre['url_source'])
                        
                        if detail_soup:
                            # ✅ EXTRACTION UNIFIÉE avec les helpers centralisés
                            details = extract_all_details(
                                detail_soup,
                                url=offre['url_source'],
                                pays_defaut=self.pays_defaut
                            )
                            
                            # PDF
                            pdf_url = self._trouver_pdf_dans_page(detail_soup, offre['url_source'])
                            if pdf_url:
                                offre['url_tdr'] = pdf_url
                                logger.info(f"     📄 Document: {pdf_url[:80]}...")
                            elif details.get('url_tdr'):
                                offre['url_tdr'] = details['url_tdr']
                                logger.info(f"     📄 Document: {details['url_tdr'][:80]}...")
                            
                            # ✅ AFFINER LE PAYS avec la page de détail
                            if details.get('pays') and details['pays'] != self.pays_defaut:
                                offre['pays'] = details['pays']
                                logger.debug(f"     🌍 Pays affiné: {details['pays']}")
                            
                            # ✅ AFFINER LE DOMAINE avec la page de détail
                            if details.get('domaine') and details['domaine'] != 'Autres':
                                offre['domaine'] = details['domaine']
                                logger.debug(f"     📊 Domaine affiné: {details['domaine']}")
                            
                            # ✅ AFFINER LA DATE DE CLÔTURE si nécessaire
                            if details.get('date_cloture'):
                                offre['date_cloture'] = details['date_cloture']
                                
                    except Exception as e:
                        logger.debug(f"    ❌ Erreur: {e}")
            
            # =================================================================
            # ÉTAPE 5 : FILTRER LES OFFRES EXPIRÉES
            # =================================================================
            offres_finales = []
            expired_count = 0
            
            for offre in offres_valides:
                if is_offer_expired(offre.get('date_cloture')):
                    expired_count += 1
                    logger.info(f"   ⏭️ EXPIRÉE rejetée: {offre.get('titre', '')[:50]}... (clôture: {offre.get('date_cloture')})")
                else:
                    offres_finales.append(offre)
            
            if expired_count > 0:
                logger.info(f"   📊 {expired_count} offre(s) expirée(s) rejetée(s)")
            
            avec_doc = sum(1 for o in offres_finales if o.get('url_tdr'))
            logger.info(f"✅ Résultat: {len(offres_finales)} offres valides, {avec_doc} avec document")
            
            return offres_finales
            
        except Exception as e:
            logger.error(f"❌ Erreur: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
        finally:
            self._close_driver()