# offres/scraping/parsers/unfpa_parser.py
from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url
from offres.scraping.country_detector import detecter_pays_smart
from offres.scraping.extraction_helpers import (
    extract_all_details,
    is_offer_valid,
    extract_pdf_url
)
from offres.utils.search_keywords import detecter_domaine, est_appel_offres
from offres.utils.offer_validator import is_valid_offer_title
import logging
from urllib.parse import urljoin
from datetime import date, timedelta

logger = logging.getLogger(__name__)


class UNFPAParser(BaseScraper):
    """Parser UNFPA - UNIQUEMENT les appels d'offres avec PDF"""
    
    MOTS_CLES_OFFRES = [
        'recrutement', 'cotation', 'appel', 'achat', 'demande',
        'consultant', 'manifestation', 'intérêt', 'interet',
        'avis', 'tender', 'bureau d\'études', 'bureau d\'etudes',
        'fourniture', 'acquisition', 'consultation', 'rfq', 'rfp',
        'production', 'travaux', 'équipement', 'equipement',
    ]
    
    def __init__(self, source_url, **kwargs):
        super().__init__(source_url, **kwargs)
        self.offers = []
        self.base_url = "https://burkinafaso.unfpa.org"
    
    def detecter_domaine(self, titre, description=""):
        return detecter_domaine(titre, description)
    
    def extraire_pdf_unfpa(self, soup, base_url="", url_source=""):
        """
        Extraction de PDF spécifique pour UNFPA
        """
        if not soup:
            return None
        
        # 1. Chercher les liens de téléchargement directs
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            texte = link.get_text(strip=True).lower()
            
            if any(kw in href.lower() or kw in texte for kw in ['download', 'telecharger', 'télécharger']):
                return normalize_url(href, base_url)
            if href.lower().endswith('.pdf'):
                return normalize_url(href, base_url)
        
        # 2. Chercher les fichiers dans /sites/default/files/
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if '/sites/default/files/' in href:
                return normalize_url(href, base_url)
        
        # 3. Chercher les extensions de documents
        extensions_doc = ['.doc', '.docx', '.xls', '.xlsx', '.pdf']
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            for ext in extensions_doc:
                if href.lower().endswith(ext):
                    return normalize_url(href, base_url)
        
        # 4. Chercher les boutons de téléchargement
        for btn in soup.find_all(['button', 'a']):
            href = btn.get('href', '')
            texte = btn.get_text(strip=True).lower()
            classe = ' '.join(btn.get('class', []))
            if 'download' in classe.lower() or 'telecharger' in classe.lower() or 'download' in texte:
                if href:
                    return normalize_url(href, base_url)
        
        # 5. Chercher dans les divs avec classe download
        for div in soup.find_all('div', class_=lambda x: x and 'download' in x.lower()):
            for link in div.find_all('a', href=True):
                href = link.get('href', '')
                if href:
                    return normalize_url(href, base_url)
        
        # 6. Fallback : URL source
        if url_source:
            logger.info(f"  📄 Aucun PDF trouvé, utilisation de l'URL source")
            return url_source
        
        return None
    
    def run(self) -> list[dict]:
        logger.info(f"🌍 Scraping UNFPA: {self.source_url}")
        
        try:
            soup = self.fetch_and_parse()
            if not soup:
                logger.error("❌ Page non récupérée")
                return []
            
            title = soup.title.string if soup.title else 'Sans titre'
            logger.info(f"📄 Page: {title}")
            
            self.offers = []
            processed_urls = set()
            
            for link in soup.find_all('a', href=True):
                titre = link.get_text(strip=True)
                
                if not titre or len(titre) < 15:
                    continue
                
                if not any(mot in titre.lower() for mot in self.MOTS_CLES_OFFRES):
                    continue
                
                offre_url = urljoin(self.source_url, link['href'])
                
                if offre_url in processed_urls:
                    continue
                processed_urls.add(offre_url)
                
                if any(x in offre_url.lower() for x in [
                    '/fr/node/add/', '/login', '/logout', '/user/',
                    '#', 'javascript:', '/fr/about', '/fr/contact'
                ]):
                    continue
                
                if not is_valid_offer_title(titre):
                    logger.debug(f"⏭️ Titre invalide: {titre[:50]}")
                    continue
                
                logger.info(f"📄 Récupération des détails: {titre[:50]}...")
                
                detail_soup = self.fetch_page(offre_url)
                if not detail_soup:
                    logger.warning(f"⚠️ Impossible de récupérer la page: {offre_url}")
                    continue
                
                # ✅ Extraire le PDF
                pdf_url = self.extraire_pdf_unfpa(detail_soup, self.base_url, offre_url)
                
                details = extract_all_details(
                    detail_soup,
                    url=offre_url,
                    pays_defaut='BF',
                    titre=titre,
                    description=titre
                )
                
                # ✅ REJET STRICT
                if not est_appel_offres(titre, titre):
                    logger.info(f"   ⏭️ REJETÉ (pas un appel d'offres): {titre[:50]}...")
                    continue
                
                domaine = self.detecter_domaine(titre)
                if details.get('domaine') and details.get('domaine') != 'Autres':
                    domaine = details.get('domaine')
                
                # ✅ Fallback URL source
                url_tdr = pdf_url or details.get('url_tdr') or offre_url
                
                offer = {
                    'titre': clean_text(titre)[:300],
                    'url_source': offre_url,
                    'organisme': 'UNFPA Burkina Faso',
                    'pays': details.get('pays', 'BF'),
                    'description': clean_text(titre)[:1000],
                    'date_publication': details.get('date_publication', date.today()),
                    'date_cloture': details.get('date_cloture', date.today() + timedelta(days=30)),
                    'url_tdr': url_tdr,
                    'domaine': domaine,
                    'statut': 'Ouvert',
                    'type_offre': 'APPEL_D_OFFRES',
                    'mode_acquisition': 'AUTO',
                }
                
                is_valid, reason = is_offer_valid(offer)
                if not is_valid:
                    logger.info(f"   ⏭️ REJETÉ: {reason}")
                    continue
                
                self.offers.append(offer)
                pdf_status = "PDF trouvé" if pdf_url and pdf_url != offre_url else "URL source"
                logger.info(f"  ✅ Appel d'offres validé (domaine: {domaine}, {pdf_status})")
            
            logger.info(f"✅ UNFPA: {len(self.offers)} appel(s) d'offres extraits")
            return self.offers
            
        except Exception as e:
            logger.error(f"❌ Erreur UNFPA: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []