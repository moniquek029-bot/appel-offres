# offres/scraping/parsers/uemoa_parser.py
from bs4 import BeautifulSoup
from datetime import date, timedelta
import logging
import re

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url
from offres.scraping.extraction_helpers import is_offer_valid, extract_pdf_url
from offres.utils.search_keywords import detecter_domaine, est_appel_offres

logger = logging.getLogger(__name__)


class UEMOAParser(BaseScraper):
    """Parser UEMOA - UNIQUEMENT les appels d'offres"""
    
    def __init__(self, source_url: str, base_url: str = "https://www.uemoa.int", pays_defaut: str = 'BF', **kwargs):
        super().__init__(source_url, delay_seconds=3, base_url=base_url, pays_defaut=pays_defaut, **kwargs)
    
    def detecter_domaine(self, titre, description=""):
        return detecter_domaine(titre, description)
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        offres = []
        
        keywords = ['appel', 'offre', 'marché', 'avis', 'recrutement']
        
        for link in soup.find_all('a', href=True):
            titre = clean_text(link.get_text(strip=True))
            href = link.get('href', '')
            
            if len(titre) < 15:
                continue
            
            titre_lower = titre.lower()
            if not any(kw in titre_lower for kw in keywords):
                continue
            
            if href in ['#', '/', '/fr/appel-d-offre', '/appel-d-offre']:
                continue
            
            url_source = normalize_url(href, self.base_url)
            
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
            
            offre = {
                'titre': titre[:300],
                'organisme': "UEMOA",
                'description': titre,
                'date_publication': date.today(),
                'date_cloture': date.today() + timedelta(days=30),
                'url_source': url_source,
                'url_tdr': url_tdr,  # ✅ PDF/TDR trouvé
                'pays': self.pays_defaut,
                'domaine': domaine,
                'statut': 'Ouvert',
                'type_offre': 'APPEL_D_OFFRES',
                'mode_acquisition': 'AUTO',
            }
            
            is_valid, reason = is_offer_valid(offre)
            if not is_valid:
                logger.info(f"   ⏭️ REJETÉ: {reason}")
                continue
            
            if not any(o['url_source'] == url_source for o in offres):
                offres.append(offre)
                logger.info(f"  ✅ Appel d'offres extrait (domaine: {domaine}, PDF: {bool(pdf_url)})")
        
        logger.info(f"✅ UEMOA: {len(offres)} appel(s) d'offres extrait(s)")
        return offres
    
    def run(self) -> list[dict]:
        logger.info(f"🕷️ UEMOA scraping: {self.source_url}")
        try:
            soup = self.fetch_and_parse()
            if not soup:
                return []
            return self.parse(soup)
        except Exception as e:
            logger.error(f"❌ Erreur UEMOA: {e}")
            return []