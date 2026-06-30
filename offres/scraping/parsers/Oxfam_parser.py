# offres/scraping/parsers/oxfam_parser.py
from offres.scraping.base import BaseScraper
from offres.scraping.extraction_helpers import is_offer_valid, extract_pdf_url
from offres.scraping.utils import normalize_url
from offres.utils.search_keywords import detecter_domaine, est_appel_offres
import logging

logger = logging.getLogger(__name__)


class OxfamParser(BaseScraper):
    """Parser Oxfam - UNIQUEMENT les appels d'offres"""
    
    def __init__(self, source_url, **kwargs):
        super().__init__(source_url, **kwargs)
        self.base_url = source_url
    
    def detecter_domaine(self, titre, description=""):
        return detecter_domaine(titre, description)
    
    def run(self):
        soup = self.fetch_and_parse()
        if not soup:
            return []
        
        offers = []
        # Logique de scraping spécifique à Oxfam
        
        for offer in offers:
            if 'domaine' not in offer or not offer['domaine']:
                offer['domaine'] = self.detecter_domaine(
                    offer.get('titre', ''),
                    offer.get('description', '')
                )
            
            if not est_appel_offres(offer.get('titre', ''), offer.get('description', '')):
                logger.info(f"   ⏭️ REJETÉ (pas un appel d'offres): {offer.get('titre', '')[:50]}...")
                continue
            
            # ✅ Extraire le PDF
            url_source = offer.get('url_source')
            if url_source:
                detail_soup = self.fetch_page(url_source)
                if detail_soup:
                    pdf_url = extract_pdf_url(detail_soup, self.base_url)
                    if pdf_url:
                        offer['url_tdr'] = pdf_url
                    else:
                        # Fallback URL source
                        offer['url_tdr'] = url_source
            
            is_valid, reason = is_offer_valid(offer)
            if is_valid:
                offer['type_offre'] = 'APPEL_D_OFFRES'
                logger.info(f"  ✅ Appel d'offres validé (domaine: {offer.get('domaine', 'Autres')})")
        
        return [o for o in offers if o.get('type_offre') == 'APPEL_D_OFFRES']