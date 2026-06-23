# offres/scraping/parsers/uemoa_parser.py
from bs4 import BeautifulSoup
from datetime import date, timedelta
import logging
import re

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url

logger = logging.getLogger(__name__)

class UEMOAParser(BaseScraper):
    """Parser UEMOA - Version simplifiée et permissive"""
    
    def __init__(self, source_url: str, base_url: str = "https://www.uemoa.int", pays_defaut: str = 'BF', **kwargs):
        super().__init__(source_url, delay_seconds=3, base_url=base_url, pays_defaut=pays_defaut, **kwargs)
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        offres = []
        
        # Mots-clés à rechercher
        keywords = ['appel', 'offre', 'marché', 'avis', 'recrutement', 'consultant']
        
        # Parcourir tous les liens
        for link in soup.find_all('a', href=True):
            titre = clean_text(link.get_text(strip=True))
            href = link.get('href', '')
            
            # Filtrer par longueur
            if len(titre) < 15:
                continue
            
            # Vérifier la présence d'un mot-clé
            titre_lower = titre.lower()
            if not any(kw in titre_lower for kw in keywords):
                continue
            
            # Exclure les liens de navigation évidents
            if href in ['#', '/', '/fr/appel-d-offre', '/appel-d-offre', '/fr/', '/']:
                continue
            
            # Exclure les pages institutionnelles génériques
            if any(excl in titre_lower for excl in ['le traité', 'mot du président', 'présentation de l\'uemoa']):
                continue
            
            url_source = normalize_url(href, self.base_url)
            
            offre = {
                'titre': titre[:300],
                'organisme': "UEMOA",
                'description': titre,
                'date_publication': date.today() - timedelta(days=7),
                'date_cloture': date.today() + timedelta(days=30),
                'url_source': url_source,
                'url_tdr': None,
                'pays': self.pays_defaut,
                'statut': 'Ouvert',
                'mode_acquisition': 'AUTO',
            }
            
            # Éviter les doublons
            if not any(o['url_source'] == url_source for o in offres):
                offres.append(offre)
        
        logger.info(f"✅ UEMOA: {len(offres)} offre(s) extraite(s)")
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