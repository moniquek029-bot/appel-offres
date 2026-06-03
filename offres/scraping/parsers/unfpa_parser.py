# offres/scraping/parsers/unfpa_parser.py
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import date, timedelta
from django.core.files.base import ContentFile

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url, extract_pdf_from_page, is_valid_pdf_url

import logging
logger = logging.getLogger(__name__)


class UNFPAParser(BaseScraper):
    """Parser UNFPA avec extraction des VRAIS PDF"""
    
    def __init__(self, source_url: str, base_url: str = "https://burkinafaso.unfpa.org", pays_defaut: str = 'BF', **kwargs):
        super().__init__(source_url, delay_seconds=3, base_url=base_url, pays_defaut=pays_defaut, **kwargs)
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        """Extrait les offres UNFPA"""
        offres = []
        
        # Chercher les articles d'offres
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text().strip()
            
            if len(text) > 20 and any(mot in text.lower() for mot in ['demande', 'recrutement', 'achat', 'cotation', 'appel', 'offre']):
                full_url = urljoin(self.base_url, href)
                
                offre = {
                    'titre': clean_text(text)[:300],
                    'organisme': "UNFPA - Fonds des Nations Unies pour la Population",
                    'description': clean_text(link.get_text())[:500],
                    'date_publication': date.today(),
                    'date_cloture': date.today() + timedelta(days=30),
                    'url_source': full_url,
                    'url_tdr': None,
                    'pays': self.pays_defaut,
                    'statut': 'Ouvert',
                    'mode_acquisition': 'AUTO',
                }
                offres.append(offre)
        
        logger.info(f"✅ UNFPA: {len(offres)} offre(s) extraite(s)")
        return offres
    
    def parse_detail_page(self, soup: BeautifulSoup, base_url: str) -> dict | None:
        """Extrait le VRAI PDF depuis la page détail UNFPA - Version améliorée"""
        try:
            # Utiliser l'utilitaire robuste d'extraction
            pdf_url = extract_pdf_from_page(str(soup), base_url)
            if pdf_url and is_valid_pdf_url(pdf_url):
                return {'url_tdr': pdf_url}
            
            # Fallback : recherche manuelle plus agressive
            for tag in soup.find_all(['a', 'button', 'div'], attrs={'href': True}):
                href = tag.get('href', '')
                if '.pdf' in href.lower():
                    full_url = normalize_url(href, base_url)
                    if is_valid_pdf_url(full_url):
                        return {'url_tdr': full_url}
            
            # Chercher dans les attributs data-*
            for tag in soup.find_all(attrs={'data-file': True}):
                href = tag.get('data-file', '')
                if '.pdf' in href.lower():
                    full_url = normalize_url(href, base_url)
                    if is_valid_pdf_url(full_url):
                        return {'url_tdr': full_url}
            
            return None
        except Exception as e:
            logger.warning(f"Erreur extraction PDF UNFPA: {e}")
            return None
    
    # DANS CHAQUE PARSER - Méthode run() corrigée

    def run(self) -> list[dict]:
        """Exécute le scraping RÉEL"""
        logger.info(f"🕷️ {self.__class__.__name__} scraping RÉEL: {self.source_url}")
    
        try:
            # ✅ Utiliser fetch_and_parse SANS passer headers (ils sont déjà dans self.default_headers)
            soup = self.fetch_and_parse()
            if not soup:
                logger.warning(f"⚠️ Aucune donnée récupérée {self.__class__.__name__}")
                return []
        
            offres = self.parse(soup)
        
            # Extraire les PDF pour chaque offre
            for offre in offres:
                if offre.get('url_source'):
                    try:
                        detail_soup = self.fetch_page(offre['url_source'])
                        if detail_soup:
                            pdf_data = self.parse_detail_page(detail_soup, self.base_url)
                            if pdf_data and pdf_data.get('url_tdr'):
                                offre['url_tdr'] = pdf_data['url_tdr']
                                logger.info(f"📎 PDF trouvé: {offre['titre'][:50]}...")
                    except Exception as e:
                        logger.debug(f"Erreur extraction PDF: {e}")
        
            return offres
        except Exception as e:
            logger.error(f"❌ Erreur {self.__class__.__name__}: {e}")
            return []


# =============================================================================
# FONCTION DE SCRAPING MANUEL (à exécuter dans le shell Django)
# =============================================================================
def scrape_all_unfpa_offres():
    """Scraper toutes les offres UNFPA avec leurs vrais PDF"""
    from offres.models import AppelOffre, SourceScraping
    
    base_url = "https://burkinafaso.unfpa.org"
    list_url = "https://burkinafaso.unfpa.org/fr/call-for-submissions"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    print("🚀 Scraping des offres UNFPA...")
    
    response = requests.get(list_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    offres_trouvees = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        text = link.get_text().strip()
        
        if len(text) > 20 and any(mot in text.lower() for mot in ['demande', 'recrutement', 'achat', 'cotation']):
            full_url = urljoin(base_url, href)
            offres_trouvees.append((text, full_url))
    
    print(f"📊 {len(offres_trouvees)} offres trouvées")
    
    source = SourceScraping.objects.filter(nom__icontains='UNFPA').first()
    
    for titre, offre_url in offres_trouvees:
        print(f"\n📌 Traitement: {titre[:50]}...")
        
        try:
            detail_response = requests.get(offre_url, headers=headers, timeout=30)
            if detail_response.status_code == 200:
                detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
                
                # Utiliser l'extraction robuste
                pdf_url = extract_pdf_from_page(str(detail_soup), offre_url)
                
                fichier_pdf = None
                if pdf_url and is_valid_pdf_url(pdf_url):
                    pdf_response = requests.get(pdf_url, headers=headers)
                    if pdf_response.status_code == 200 and pdf_response.content.startswith(b'%PDF-'):
                        fichier_pdf = ContentFile(pdf_response.content, name=f"unfpa_{int(time.time())}.pdf")
                        print(f"   ✅ PDF téléchargé")
                
                if pdf_url:  # Créer seulement si PDF trouvé
                    offre, created = AppelOffre.objects.get_or_create(
                        url_source=offre_url,
                        defaults={
                            'titre': titre[:300],
                            'organisme': "UNFPA Burkina Faso",
                            'description': detail_soup.get_text()[:1000],
                            'date_publication': date.today(),
                            'date_cloture': date.today() + timedelta(days=30),
                            'url_tdr': pdf_url,
                            'fichier_pdf': fichier_pdf,
                            'statut': 'Ouvert',
                            'pays': 'BF',
                            'mode_acquisition': 'AUTO',
                            'source_origine': source,
                        }
                    )
                    
                    if created:
                        print(f"   ✅ Nouvelle offre créée")
                    else:
                        print(f"   ⏭️ Offre déjà existante")
                else:
                    print(f"   ❌ Rejetée: pas de PDF valide trouvé")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")