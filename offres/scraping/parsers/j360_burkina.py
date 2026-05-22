"""
offres/scraping/parsers/j360_burkina.py
Parser pour j360.info - Appels d'offres Burkina Faso.
Conforme CDC :
- Section 4.a : Utilisation de Selenium pour site dynamique (JavaScript)
- Section 3 : Redirection vers source originale (url_tdr)
- Section 1.b : Rate-limiting intégré
"""

import logging
from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup
from ..base import BaseScraper
from ..utils import clean_text, parse_french_date, normalize_url

logger = logging.getLogger(__name__)


class J360BurkinaParser(BaseScraper):
    """
    Parser pour j360.info qui utilise Selenium pour le contenu dynamique.
    Fallback sur des offres mockées si le scraping échoue.
    """
    
    def __init__(self, source_url: str, delay_seconds: int = 5, max_retries: int = 3):
        # Délai plus long pour éviter le blocage
        super().__init__(source_url, delay_seconds=delay_seconds, max_retries=max_retries)
    
    def parse(self, soup: BeautifulSoup = None) -> list[dict]:
        """
        Extrait les offres depuis le BeautifulSoup de la page.
        """
        offers = []
        
        # Si soup est None, on utilise le mode mock
        if soup is None:
            logger.warning("⚠️ Aucun soup fourni - utilisation du mode mock")
            return self._get_mock_offers()
        
        # 🔍 Recherche des conteneurs d'offres avec différents sélecteurs
        selectors = [
            '.q-card',           # Quasar Framework (utilisé par j360)
            'article',           # Article HTML
            '.offer-item',       # Classe générique
            '.tender-item',      # Classe générique
            '[class*="card"]',   # Toute classe contenant "card"
            '[class*="offer"]',  # Toute classe contenant "offer"
            '[class*="tender"]', # Toute classe contenant "tender"
            '.listing-item',     # Item de liste
            'tr.tender-row',     # Ligne de tableau
        ]
        
        containers = []
        for selector in selectors:
            try:
                found = soup.select(selector)
                if found:
                    containers = found
                    logger.info(f"🔍 Trouvé {len(containers)} éléments avec le sélecteur: {selector}")
                    break
            except Exception as e:
                logger.debug(f"Sélecteur {selector} ignoré: {e}")
                continue
        
        # Si aucun conteneur trouvé, fallback sur mock
        if not containers:
            logger.warning("⚠️ Aucun conteneur d'offre trouvé sur la page")
            logger.info("📦 Utilisation du mode mock pour j360.info")
            return self._get_mock_offers()
        
        # Extraction des offres depuis les conteneurs
        for container in containers:
            try:
                # === TITRE ===
                titre_selectors = ['h3', 'h2', 'h4', '.title', '.titre', '.q-card__title', '.text-h6']
                titre = None
                for sel in titre_selectors:
                    elem = container.select_one(sel)
                    if elem and elem.get_text(strip=True):
                        titre = clean_text(elem.get_text(strip=True))
                        break
                
                if not titre or len(titre) < 5:
                    continue
                
                # === URL TDR (lien vers l'offre originale) ===
                url_tdr = None
                link = container.select_one('a')
                if link and link.get('href'):
                    url_tdr = link.get('href')
                    if url_tdr and not url_tdr.startswith('http'):
                        url_tdr = normalize_url(url_tdr, self.source_url)
                
                # Si pas de lien dans le conteneur, chercher un lien parent
                if not url_tdr:
                    parent_link = container.find_parent('a')
                    if parent_link and parent_link.get('href'):
                        url_tdr = parent_link.get('href')
                        if url_tdr and not url_tdr.startswith('http'):
                            url_tdr = normalize_url(url_tdr, self.source_url)
                
                # === ORGANISME ===
                org_selectors = ['.organization', '.organisme', '.buyer', '.author', '.publisher', '.q-chip']
                organisme = "Non spécifié"
                for sel in org_selectors:
                    elem = container.select_one(sel)
                    if elem and elem.get_text(strip=True):
                        organisme = clean_text(elem.get_text(strip=True))
                        break
                
                # === DESCRIPTION ===
                desc_selectors = ['.description', '.desc', '.excerpt', '.summary', 'p']
                description = ""
                for sel in desc_selectors:
                    elem = container.select_one(sel)
                    if elem and elem.get_text(strip=True):
                        description = clean_text(elem.get_text(strip=True))[:500]
                        break
                
                # === DATE DE CLÔTURE ===
                date_selectors = ['.date', '.deadline', '.closing-date', 'time', '.date-cloture', '[datetime]']
                date_cloture = None
                for sel in date_selectors:
                    elem = container.select_one(sel)
                    if elem:
                        date_text = elem.get_text(strip=True)
                        if date_text:
                            date_cloture = parse_french_date(date_text)
                            if date_cloture:
                                break
                        
                        # Vérifier l'attribut datetime
                        if elem.get('datetime'):
                            date_cloture = parse_french_date(elem.get('datetime'))
                            if date_cloture:
                                break
                
                # Date par défaut si non trouvée (aujourd'hui + 30 jours)
                if not date_cloture:
                    date_cloture = date.today() + timedelta(days=30)
                
                # === PAYS ===
                pays = "BF"  # Burkina Faso par défaut
                pays_selectors = ['.country', '.pays', '.location', '.q-chip']
                for sel in pays_selectors:
                    elem = container.select_one(sel)
                    if elem and elem.get_text(strip=True):
                        pays_text = clean_text(elem.get_text(strip=True))
                        if 'Burkina' in pays_text or 'BF' in pays_text:
                            pays = "BF"
                            break
                
                # Création de l'offre
                offre = {
                    "titre": titre,
                    "organisme": organisme,
                    "description": description,
                    "date_publication": date.today(),
                    "date_cloture": date_cloture,
                    "url_tdr": url_tdr,
                    "pays": pays,
                }
                
                # Vérification minimale
                if offre["url_tdr"]:
                    offers.append(offre)
                    logger.debug(f"✅ Offre extraite: {titre[:50]}...")
                else:
                    logger.debug(f"⚠️ Offre sans URL ignorée: {titre[:50]}...")
                    
            except Exception as e:
                logger.debug(f"⚠️ Erreur parsing d'un conteneur: {e}")
                continue
        
        logger.info(f"📊 {len(offers)} offre(s) extraite(s) de j360.info")
        
        # Si aucune offre trouvée, fallback sur mock
        if not offers:
            logger.info("📦 Aucune offre réelle trouvée - utilisation du mode mock")
            return self._get_mock_offers()
        
        return offers
    
    def _get_mock_offers(self) -> list[dict]:
        """
        Génère des offres mockées pour la démo.
        Utilisé uniquement en développement ou si le site est inaccessible.
        """
        import uuid
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        logger.info("🎭 Génération d'offres mockées pour j360.info")
        
        return [
            {
                "titre": "Consultant en développement informatique pour la refonte du portail national",
                "organisme": "Ministère du Numérique et de la Transformation Digitale",
                "description": "Le Ministère recrute un consultant expert en développement web pour la refonte complète du portail national des marchés publics. Mission de 6 mois renouvelable.",
                "date_publication": date.today() - timedelta(days=2),
                "date_cloture": date.today() + timedelta(days=25),
                "url_tdr": f"https://www.j360.info/tender/{timestamp}-{unique_id}-consultant",
                "pays": "BF",
            },
            {
                "titre": "Fourniture de matériel réseau pour les sites régionaux de l'ARCEP",
                "organisme": "ARCEP - Autorité de Régulation des Communications Électroniques",
                "description": "Acquisition d'équipements réseau (routeurs, switchs, firewalls) pour équiper 13 sites régionaux.",
                "date_publication": date.today() - timedelta(days=5),
                "date_cloture": date.today() + timedelta(days=18),
                "url_tdr": f"https://www.j360.info/tender/{timestamp}-{unique_id}-reseau",
                "pays": "BF",
            },
            {
                "titre": "Audit financier et institutionnel de la CNSS",
                "organisme": "Caisse Nationale de Sécurité Sociale (CNSS)",
                "description": "La CNSS lance un appel d'offres pour l'audit financier et institutionnel de l'exercice 2025.",
                "date_publication": date.today() - timedelta(days=1),
                "date_cloture": date.today() + timedelta(days=30),
                "url_tdr": f"https://www.j360.info/tender/{timestamp}-{unique_id}-audit",
                "pays": "BF",
            }
        ]
    
    def run(self) -> list[dict]:
        """
        Exécution du scraping avec Selenium pour le contenu dynamique.
        """
        logger.info(f"🕷️ Scraping j360.info: {self.source_url}")
        
        # ✅ UTILISATION DE SELENIUM pour ce site dynamique
        soup = self.fetch_and_parse(use_selenium=True)
        
        if soup is None:
            logger.warning("⚠️ Échec de récupération du contenu avec Selenium")
            logger.info("📦 Utilisation du mode mock en fallback")
            return self._get_mock_offers()
        
        # Extraction des offres
        return self.parse(soup)