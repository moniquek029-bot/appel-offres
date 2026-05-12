"""
offres/scraping/parsers/j360_burkina.py
Parser pour j360.info - Appels d'offres Burkina Faso.
Gère deux modes :
  1. Page liste : extrait les liens vers les détails + métadonnées basiques
  2. Page détail : extrait le JSON-LD complet
"""

import json
import logging
import time
from urllib.parse import urljoin, urlparse
from ..base import BaseScraper
from ..utils import clean_text, parse_french_date, normalize_url
from datetime import datetime
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class J360BurkinaParser(BaseScraper):
    """
    Parser pour j360.info qui gère :
    - Page liste : extraction des liens + métadonnées visibles
    - Page détail : extraction du JSON-LD Schema.org
    """
    
    def __init__(self, source_url: str, delay_seconds: int = 5, max_retries: int = 3):
        # Delay plus long pour éviter le blocage (j360.info semble sensible aux bots)
        super().__init__(source_url, delay_seconds=delay_seconds, max_retries=max_retries)
        # Headers plus réalistes
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive",
        })
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        """
        Point d'entrée principal.
        Détecte automatiquement si c'est une page liste ou détail.
        """
        # 1. Essayer d'extraire depuis JSON-LD (page détail)
        offres_jsonld = self._parse_jsonld(soup)
        if offres_jsonld:
            logger.info(f" JSON-LD extrait : {len(offres_jsonld)} offre(s)")
            return offres_jsonld
        
        # 2. Sinon, extraire depuis la page liste (CSS selectors)
        logger.info(" Pas de JSON-LD trouvé, tentative d'extraction depuis la liste...")
        return self._parse_list_page(soup)
    
    def _parse_jsonld(self, soup: BeautifulSoup) -> list[dict]:
        """Extrait les offres depuis les balises JSON-LD (Schema.org)."""
        offres = []
        json_scripts = soup.find_all("script", type="application/ld+json")
        
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if not self._is_offer_data(data):
                    continue
                
                offre = self._extract_from_jsonld(data, self.source_url)
                if offre and offre.get("url_tdr"):
                    offres.append(offre)
            except (json.JSONDecodeError, TypeError, AttributeError) as e:
                logger.debug(f" JSON-LD ignoré : {e}")
                continue
        
        return offres
    
    def _is_offer_data(self, data: dict) -> bool:
        """Vérifie si le JSON-LD correspond à une offre."""
        if not isinstance(data, dict):
            return False
        if data.get("@type") == "DataFeedItem":
            item = data.get("item", {})
            return item.get("@type") == "Demand"
        return data.get("@type") == "Demand"
    
    def _extract_from_jsonld(self, data: dict, base_url: str) -> dict:
        """Extrait les champs depuis le JSON-LD."""
        item = data.get("item", {}) if data.get("@type") == "DataFeedItem" else data
        
        titre = (item.get("itemOffered", {}).get("name") or 
                 item.get("name") or 
                 data.get("name") or 
                 "Offre sans titre")
        
        organisme = item.get("seller") or "Non précisé"
        description = (item.get("description") or "")[:500]
        
        # Dates ISO 8601
        date_pub = self._parse_iso_date(data.get("dateCreated") or data.get("datePublished"))
        date_clot = self._parse_iso_date(item.get("validThrough") or item.get("endDate"))
        
        # Pays
        area = item.get("areaServed")
        pays = area[0] if isinstance(area, list) and area else (area if isinstance(area, str) else "BF")
        
        # URL source
        url_raw = data.get("identifier") or data.get("@id") or item.get("url")
        url_tdr = normalize_url(url_raw, base_url) if url_raw else None
        
        return {
            "titre": clean_text(titre),
            "organisme": clean_text(organisme),
            "description": clean_text(description),
            "date_publication": date_pub,
            "date_cloture": date_clot,
            "url_tdr": url_tdr,
        }
    
    def _parse_iso_date(self, date_str: str):
        """Parse date ISO 8601 ou format français."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return parse_french_date(date_str)
    
    def _parse_list_page(self, soup: BeautifulSoup) -> list[dict]:
        """
        Extrait les offres depuis une page liste avec sélecteurs CSS.
         Les sélecteurs ci-dessous sont INDICATIFS - à ajuster via F12.
        """
        offres = []
        
        #  Sélecteurs génériques pour trouver les conteneurs d'offres
        containers = soup.select(
            "article.post, div.offer-item, li.appel-offre, "
            "div.card, div.listing-item, .entry, .post-item"
        )
        
        logger.info(f" {len(containers)} conteneurs potentiels trouvés")
        
        for container in containers:
            try:
                # Titre (syntaxe Python corrigée)
                titre_tag = container.select_one("h2, h3, .title, .entry-title, a.titre")
                titre = clean_text(titre_tag.text) if titre_tag else None
                
                # Lien vers le détail
                lien_tag = container.select_one("a")
                url_relative = lien_tag["href"] if lien_tag and lien_tag.get("href") else None
                url_detail = normalize_url(url_relative, self.source_url) if url_relative else None
                
                # Si pas de titre ni de lien → ignorer
                if not titre and not url_detail:
                    continue
                
                # Organisme
                org_tag = container.select_one(".author, .publisher, .organisme, .meta-author")
                organisme = clean_text(org_tag.text) if org_tag else "Non précisé"
                
                # Date
                date_tag = container.select_one("time, .date, .published, .meta-date")
                date_cloture = parse_french_date(date_tag.text) if date_tag else None
                
                # Description courte
                desc_tag = container.select_one("p, .excerpt, .summary, .resume")
                description = clean_text(desc_tag.text)[:300] if desc_tag else ""
                
                offre = {
                    "titre": titre or "Offre sans titre",
                    "organisme": organisme,
                    "description": description,
                    "date_publication": None,
                    "date_cloture": date_cloture,
                    "url_tdr": url_detail,
                }
                
                #  Si on a un lien détail, aller scraper le JSON-LD
                if url_detail:
                    detail_offre = self._scrape_detail_page(url_detail)
                    if detail_offre:
                        offre.update({k: v for k, v in detail_offre.items() if v})
                
                offres.append(offre)
                
            except Exception as e:
                logger.warning(f" Ligne ignorée : {e}")
                continue
        
        logger.info(f" {len(offres)} offre(s) extraites de la liste")
        return offres
    
    def _scrape_detail_page(self, url_detail: str) -> dict:
        """Va scraper une page détail pour extraire le JSON-LD."""
        try:
            logger.debug(f" Scraping détail : {url_detail}")
            
            # Rate-limiting
            time.sleep(self.delay)
            
            # Fetch HTML
            html = self.fetch_html(url_detail)
            if not html:
                return None
            
            # Parser et extraire JSON-LD
            soup = BeautifulSoup(html, "html.parser")
            jsonld_offres = self._parse_jsonld(soup)
            
            if jsonld_offres:
                logger.debug(f" JSON-LD trouvé sur détail : {url_detail}")
                return jsonld_offres[0]
            
            # Fallback CSS
            return self._extract_from_detail_css(soup, url_detail)
            
        except Exception as e:
            logger.warning(f" Échec scraping détail {url_detail} : {e}")
            return None
    
    def _extract_from_detail_css(self, soup: BeautifulSoup, url: str) -> dict:
        """Fallback : extraction CSS sur page détail si pas de JSON-LD."""
        try:
            #  Syntaxe Python corrigée pour tous les select_one
            titre_tag = soup.select_one("h1, .title, .entry-title")
            titre = clean_text(titre_tag.text) if titre_tag else ""
            
            org_tag = soup.select_one(".author, .publisher, .organisme")
            organisme = clean_text(org_tag.text) if org_tag else "Non précisé"
            
            desc_tag = soup.select_one(".content, .description, .excerpt")
            description = clean_text(desc_tag.text)[:500] if desc_tag else ""
            
            # Dates
            date_cloture = None
            date_el = soup.select_one(".date-cloture, .deadline, .valid-through, time[datetime]")
            if date_el:
                date_cloture = parse_french_date(date_el.text) or self._parse_iso_date(date_el.get("datetime"))
            
            return {
                "titre": titre or "Offre sans titre",
                "organisme": organisme,
                "description": description,
                "date_publication": None,
                "date_cloture": date_cloture,
                "url_tdr": url,
            }
        except Exception as e:
            logger.debug(f" Fallback CSS échoué : {e}")
            return None
    
    def run(self) -> list[dict]:
        """Surcharge de run() pour gérer le scraping de j360.info."""
        logger.info(f" Démarrage scraping j360.info : {self.source_url}")
        
        if not self.is_allowed("/"):
            logger.warning(f" Scraping bloqué par robots.txt pour {self.source_url}")
            return []
        
        html = self.fetch_html(self.source_url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, "html.parser")
        resultats = self.parse(soup)
        
        time.sleep(self.delay)
        
        logger.info(f" Scraping terminé : {len(resultats)} offre(s) extraite(s)")
        return resultats