# offres/scraping/parsers/agetib_parser.py
from bs4 import BeautifulSoup
from datetime import date, timedelta
import logging
import re

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url
from offres.scraping.extraction_helpers import extract_pdf_url
from offres.utils.search_keywords import detecter_domaine, est_appel_offres

logger = logging.getLogger(__name__)

class AgetibParser(BaseScraper):
    """Parser AGETIB - Correction de l'extraction des titres"""
    
    def __init__(self, source_url: str, base_url: str = "https://www.agetib.net", pays_defaut: str = 'BF', **kwargs):
        super().__init__(source_url, delay_seconds=3, base_url=base_url, pays_defaut=pays_defaut, **kwargs)
    
    def detecter_domaine(self, titre, description=""):
        return detecter_domaine(titre, description)
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        offres = []
        # Cible plus large pour attraper les cartes d'offres
        cards = soup.select('.offer-card, .appel-offre, article, .post, .entry')
        if not cards:
            cards = soup.find_all(['div', 'article'], limit=40)
        
        for card in cards:
            try:
                # ✅ CORRECTION : Chercher d'abord un vrai titre (h2, h3, h4)
                titre_elem = card.select_one('h2, h3, h4, .entry-title, .post-title')
                
                # Si pas de titre, chercher un lien avec du texte substantiel (pas "en savoir plus")
                if not titre_elem:
                    for a in card.find_all('a'):
                        txt = clean_text(a.get_text(strip=True))
                        if len(txt) > 15 and not re.search(r'en savoir plus|lire la suite|voir plus', txt, re.I):
                            titre_elem = a
                            break
                
                if not titre_elem:
                    continue
                
                titre = clean_text(titre_elem.get_text(strip=True))
                
                # ✅ CORRECTION : Rejet explicite des faux titres
                if len(titre) < 15 or re.search(r'en savoir plus|lire la suite|navigation|menu', titre, re.I):
                    continue
                
                link_elem = card.select_one('a[href]')
                url_source = normalize_url(link_elem.get('href'), self.base_url) if link_elem else None
                
                # ✅ Validation stricte
                if not est_appel_offres(titre):
                    logger.info(f"   ⏭️ REJETÉ (pas un appel d'offres): {titre[:50]}...")
                    continue
                
                # ✅ Extraire le PDF si on a une page de détail
                pdf_url = None
                if url_source and url_source != self.source_url:
                    detail_soup = self.fetch_page(url_source)
                    if detail_soup:
                        pdf_url = extract_pdf_url(detail_soup, self.base_url)
                
                url_tdr = pdf_url or url_source
                domaine = self.detecter_domaine(titre)
                
                # Essayer de trouver une description réelle
                desc_elem = card.select_one('.entry-content, .post-content, p')
                description = clean_text(desc_elem.get_text(strip=True)) if desc_elem else titre

                offre = {
                    'titre': titre[:300],
                    'organisme': "AGETIB",
                    'description': description[:500],
                    'date_publication': date.today() - timedelta(days=1),
                    'date_cloture': date.today() + timedelta(days=21), # Fallback, à améliorer si date trouvée
                    'url_source': url_source,
                    'url_tdr': url_tdr,
                    'pays': self.pays_defaut,
                    'domaine': domaine,
                    'statut': 'Ouvert',
                    'type_offre': 'APPEL_D_OFFRES',
                    'mode_acquisition': 'AUTO',
                }
                
                if titre and url_source:
                    # Éviter les doublons
                    if not any(o['url_source'] == url_source for o in offres):
                        offres.append(offre)
                        logger.info(f"  ✅ AGETIB extrait: {titre[:50]}... (PDF: {bool(pdf_url)})")
                    
            except Exception as e:
                logger.debug(f"Erreur parsing AGETIB: {e}")
                continue
        
        return offres
    
    def run(self) -> list[dict]:
        logger.info(f"🕷️ AGETIB scraping: {self.source_url}")
        try:
            # use_js=True est souvent nécessaire pour AGETIB car c'est un site WordPress moderne
            soup = self.fetch_and_parse(use_js=True)
            if not soup:
                return []
            return self.parse(soup)
        except Exception as e:
            logger.error(f"❌ Erreur AGETIB: {e}")
            return []