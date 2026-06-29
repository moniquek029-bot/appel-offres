# offres/scraping/parsers/agetib_parser.py
from bs4 import BeautifulSoup
from datetime import date, timedelta
import logging

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url
from offres.scraping.extraction_helpers import extract_pdf_url
from offres.utils.search_keywords import detecter_domaine, est_appel_offres

logger = logging.getLogger(__name__)


class AgetibParser(BaseScraper):
    """Parser AGETIB - UNIQUEMENT les appels d'offres"""
    
    def __init__(self, source_url: str, base_url: str = "https://www.agetib.net", pays_defaut: str = 'BF', **kwargs):
        super().__init__(source_url, delay_seconds=3, base_url=base_url, pays_defaut=pays_defaut, **kwargs)
    
    def detecter_domaine(self, titre, description=""):
        return detecter_domaine(titre, description)
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        offres = []
        cards = soup.select('.offer-card, .appel-offre, article')
        if not cards:
            cards = soup.find_all(['div', 'article'], limit=30)
        
        for card in cards:
            try:
                titre_elem = card.select_one('h3, h4, .title, a')
                if not titre_elem:
                    continue
                
                titre = clean_text(titre_elem.text)
                if len(titre) < 10:
                    continue
                
                link_elem = card.select_one('a[href]')
                url_source = normalize_url(link_elem.get('href'), self.base_url) if link_elem else None
                
                # ✅ REJET STRICT : UNIQUEMENT les appels d'offres
                if not est_appel_offres(titre):
                    logger.info(f"   ⏭️ REJETÉ (pas un appel d'offres): {titre[:50]}...")
                    continue
                
                # ✅ Extraire le PDF si disponible
                pdf_url = None
                if url_source:
                    detail_soup = self.fetch_page(url_source)
                    if detail_soup:
                        pdf_url = extract_pdf_url(detail_soup, self.base_url)
                
                url_tdr = pdf_url or url_source
                
                domaine = self.detecter_domaine(titre)
                texte_brut = card.get_text()
                description = f"AGETIB Travaux Publics et Infrastructures - {clean_text(texte_brut)}"

                offre = {
                    'titre': titre[:300],
                    'organisme': "AGETIB",
                    'description': description[:500],
                    'date_publication': date.today() - timedelta(days=1),
                    'date_cloture': date.today() + timedelta(days=21),
                    'url_source': url_source,
                    'url_tdr': url_tdr,  # ✅ PDF/TDR trouvé
                    'pays': self.pays_defaut,
                    'domaine': domaine,
                    'statut': 'Ouvert',
                    'type_offre': 'APPEL_D_OFFRES',
                    'mode_acquisition': 'AUTO',
                }
                
                if titre and url_source:
                    offres.append(offre)
                    logger.info(f"  ✅ Appel d'offres extrait (domaine: {domaine}, PDF: {bool(pdf_url)})")
                    
            except Exception as e:
                logger.debug(f"Erreur parsing AGETIB: {e}")
                continue
        
        return offres
    
    def run(self) -> list[dict]:
        logger.info(f"🕷️ AGETIB scraping: {self.source_url}")
        try:
            soup = self.fetch_and_parse(use_js=True)
            if not soup:
                return []
            return self.parse(soup)
        except Exception as e:
            logger.error(f"❌ Erreur AGETIB: {e}")
            return []