# offres/scraping/parsers/undp_parser.py
import re
from bs4 import BeautifulSoup
from datetime import date, timedelta
import logging

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url, detecter_pays

logger = logging.getLogger(__name__)

class UNDPParser(BaseScraper):
    """Parser UNDP corrigé - extraction dynamique du pays"""
    
    def __init__(self, source_url: str, base_url: str = "https://procurement-notices.undp.org", pays_defaut: str = 'BF', **kwargs):
        super().__init__(source_url, delay_seconds=2, base_url=base_url, pays_defaut=pays_defaut, **kwargs)
    
    def extract_pdf_from_detail(self, detail_url: str) -> str | None:
        """Visite la page de détail et extrait le lien PDF"""
        try:
            soup = self.fetch_page(detail_url)
            if not soup:
                return None
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text(strip=True).lower()
                
                if '.pdf' in href.lower():
                    return normalize_url(href, self.base_url)
                
                if any(word in text for word in ['download', 'pdf', 'document']):
                    if href and not href.startswith('#'):
                        return normalize_url(href, self.base_url)
            
            return None
        except Exception as e:
            logger.warning(f"  ⚠️ Erreur extraction PDF: {e}")
            return None
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        offres = []
        
        # Extraire les liens view_notice
        notice_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'view_notice' not in href:
                continue
            
            titre = clean_text(link.get_text(strip=True))
            
            # Nettoyer le titre parasite "Title" au début
            if titre.lower().startswith('title'):
                titre = titre[5:].strip()
            
            if len(titre) < 15:
                continue
            
            url_source = normalize_url(href, self.base_url)
            notice_links.append({
                'titre': titre,
                'url_source': url_source
            })
        
        logger.info(f"🔍 {len(notice_links)} notices trouvées, extraction des détails...")
        
        # Visiter chaque page de détail pour extraire PDF et pays
        for i, notice in enumerate(notice_links[:20], 1):
            logger.info(f"  [{i}/{len(notice_links)}] {notice['titre'][:50]}...")
            
            # Extraire le PDF
            url_tdr = self.extract_pdf_from_detail(notice['url_source'])
            
            # 🎯 DÉTECTER LE PAYS dynamiquement depuis le titre
            pays = detecter_pays(notice['titre'], self.pays_defaut)
            
            offre = {
                'titre': notice['titre'][:300],
                'organisme': "UNDP",
                'description': notice['titre'],
                'date_publication': date.today() - timedelta(days=5),
                'date_cloture': date.today() + timedelta(days=30),
                'url_source': notice['url_source'],
                'url_tdr': url_tdr,
                'pays': pays,  # ← PAYS DÉTECTÉ DYNAMIQUEMENT
                'statut': 'Ouvert',
                'mode_acquisition': 'AUTO',
            }
            
            if not any(o['url_source'] == offre['url_source'] for o in offres):
                offres.append(offre)
        
        logger.info(f"✅ UNDP: {len(offres)} offre(s) extraite(s)")
        return offres
    
    def run(self) -> list[dict]:
        logger.info(f"🕷️ UNDP scraping: {self.source_url}")
        try:
            soup = self.fetch_and_parse(use_js=False)
            if not soup:
                return []
            return self.parse(soup)
        except Exception as e:
            logger.error(f"❌ Erreur UNDP: {e}")
            return []