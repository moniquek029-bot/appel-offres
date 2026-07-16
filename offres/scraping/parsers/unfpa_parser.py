# offres/scraping/parsers/unfpa_parser.py
from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url
from offres.scraping.extraction_helpers import (
    extract_all_details,
    extract_pdf_url,
)
from offres.scraping.pdf_date_extractor import extract_dates_from_pdf
from offres.utils.search_keywords import detecter_domaine, est_appel_offres
import logging
from urllib.parse import urljoin
from datetime import date, timedelta
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

class UNFPAParser(BaseScraper):
    """Parser UNFPA - Correction : Scraping PUBLIC forcé (pas d'auth)"""
    
    MOTS_CLES_OFFRES = [
        'recrutement', 'cotation', 'appel', 'achat', 'demande',
        'consultant', 'manifestation', 'intérêt', 'interet',
        'avis', 'tender', 'bureau', 'fourniture', 'acquisition',
        'consultation', 'rfq', 'rfp', 'production', 'travaux',
        'équipement', 'equipement', 'kits', 'santé', 'sante',
        'motocyclette', 'laptop', 'matériel', 'subvention', 'offre'
    ]
    
    def __init__(self, source_url, **kwargs):
        super().__init__(source_url, **kwargs)
        self.base_url = "https://burkinafaso.unfpa.org"
        # ✅ CORRECTION : Forcer le mode public, désactiver toute tentative de login
        self.requires_auth = False 
    
    def _normaliser_texte(self, texte: str) -> str:
        if not texte:
            return ""
        texte = texte.replace(''', "'").replace(''', "'")
        return texte
    
    def _extraire_dates_pdf(self, pdf_url: str) -> tuple[date | None, date | None]:
        if not pdf_url or not pdf_url.endswith('.pdf'):
            return None, None
        try:
            return extract_dates_from_pdf(pdf_url)
        except Exception as e:
            logger.warning(f"   ⚠️ Erreur extraction PDF: {e}")
            return None, None
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        offers = []
        processed_urls = set()
        
        if not soup:
            return offers
        
        logger.info(f"🔍 UNFPA: Analyse de la page {self.source_url}")
        
        # ✅ CORRECTION : Élargir la recherche de liens au-delà de "/fr/submission/"
        # UNFPA utilise aussi /fr/appels-d-offres, /fr/call-for-proposals, etc.
        liens_cibles = soup.find_all('a', href=True)
        
        for link in liens_cibles:
            href = link.get('href', '')
            titre = link.get_text(strip=True)
            
            # Filtrer les liens évidents de navigation
            if any(x in href.lower() for x in ['/login', '/user/', '/fr/about', '/fr/contact', '#', 'javascript:']):
                continue
            
            if not titre or len(titre) < 15:
                continue
            
            titre_norm = self._normaliser_texte(titre).lower()
            mots_trouves = [mot for mot in self.MOTS_CLES_OFFRES if mot in titre_norm]
            
            if not mots_trouves:
                continue
            
            offre_url = urljoin(self.source_url, href)
            
            if offre_url in processed_urls:
                continue
            processed_urls.add(offre_url)
            
            logger.info(f"   📌 Offre potentielle: {titre[:60]}")
            
            # Visiter la page de détail
            detail_soup = self.fetch_page(offre_url)
            if not detail_soup:
                continue
            
            pdf_url = extract_pdf_url(detail_soup, self.base_url)
            
            details = extract_all_details(
                detail_soup,
                url=offre_url,
                pays_defaut='BF',
                titre=titre,
                description=titre
            )
            
            if not est_appel_offres(titre, titre):
                logger.info(f"   ⏭️ REJETÉ (pas un appel d'offres): {titre[:50]}...")
                continue
            
            domaine = detecter_domaine(titre)
            if details.get('domaine') and details.get('domaine') != 'Autres':
                domaine = details.get('domaine')
            
            url_tdr = pdf_url or details.get('url_tdr') or offre_url
            
            date_pub = details.get('date_publication')
            date_cloture = details.get('date_cloture')
            
            if pdf_url and pdf_url.endswith('.pdf'):
                date_pub_pdf, date_cloture_pdf = self._extraire_dates_pdf(pdf_url)
                if date_pub_pdf: date_pub = date_pub_pdf
                if date_cloture_pdf: date_cloture = date_cloture_pdf
            
            if not date_pub:
                date_pub = date.today()
            
            if date_cloture and date_cloture < date.today():
                logger.info(f"   ⏭️ REJETÉ (offre expirée): {titre[:50]}...")
                continue
            
            if not date_cloture:
                date_cloture = date.today() + timedelta(days=60)
            
            offer = {
                'titre': clean_text(titre)[:300],
                'url_source': offre_url,
                'organisme': 'UNFPA Burkina Faso',
                'pays': details.get('pays', 'BF'),
                'description': clean_text(titre)[:1000],
                'date_publication': date_pub,
                'date_cloture': date_cloture,
                'url_tdr': url_tdr,
                'domaine': domaine,
                'statut': 'Ouvert',
                'type_offre': 'APPEL_D_OFFRES',
                'mode_acquisition': 'AUTO',
            }
            
            offers.append(offer)
            logger.info(f"  ✅ UNFPA Extrait: {titre[:50]}...")
        
        logger.info(f"✅ UNFPA: {len(offers)} appel(s) d'offres extraits")
        return offers
    
    def run(self) -> list[dict]:
        logger.info(f"🌍 Scraping UNFPA (Mode Public): {self.source_url}")
        try:
            # ✅ CORRECTION : use_js=False pour éviter les blocages, et pas d'auth
            soup = self.fetch_and_parse(use_js=False)
            if not soup:
                logger.error("❌ Page non récupérée")
                return []
            
            return self.parse(soup)
        except Exception as e:
            logger.error(f"❌ Erreur UNFPA: {e}")
            return []