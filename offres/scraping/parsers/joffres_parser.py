# offres/scraping/parsers/joffres_parser.py
from bs4 import BeautifulSoup
from datetime import date, timedelta
import logging
import re

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url
from offres.scraping.extraction_helpers import extract_pdf_url
from offres.utils.search_keywords import detecter_domaine, est_appel_offres

logger = logging.getLogger(__name__)


def detecter_pays(texte: str, pays_defaut: str = 'BF') -> str:
    pays_mapping = {
        'burkina': 'BF', 'burkina faso': 'BF', 'ouagadougou': 'BF', 'bfa': 'BF',
        'sénégal': 'SN', 'senegal': 'SN', 'dakar': 'SN',
        'côte d\'ivoire': 'CI', 'cote d\'ivoire': 'CI', 'abidjan': 'CI',
        'mali': 'ML', 'bamako': 'ML',
        'niger': 'NE', 'niamey': 'NE',
        'togo': 'TG', 'lomé': 'TG',
        'bénin': 'BJ', 'benin': 'BJ',
        'guinée': 'GN', 'conakry': 'GN',
        'cameroun': 'CM', 'yaoundé': 'CM',
        'tchad': 'TD', 'ndjamena': 'TD',
    }
    texte_lower = texte.lower()
    for mot_cle, code_pays in pays_mapping.items():
        if mot_cle in texte_lower:
            return code_pays
    return pays_defaut


class JoffresParser(BaseScraper):
    """Parser JOFFRES - UNIQUEMENT les appels d'offres"""
    
    def __init__(self, source_url: str, base_url: str = "https://www.joffres.net", pays_defaut: str = 'BF', **kwargs):
        super().__init__(source_url, delay_seconds=2, base_url=base_url, pays_defaut=pays_defaut, **kwargs)
    
    def detecter_domaine(self, titre, description=""):
        return detecter_domaine(titre, description)
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        offres = []
        keywords = ['appel', 'offre', 'marché', 'tender', 'avis', 'consultation', 'recrutement']
        
        for link in soup.find_all('a', href=True):
            try:
                titre = clean_text(link.get_text(strip=True))
                href = link['href']
                
                if len(titre) < 15 or href in ['#', '/', 'javascript:void(0)']:
                    continue
                if not any(kw in titre.lower() for kw in keywords):
                    continue
                
                url_source = normalize_url(href, self.base_url)
                pays = detecter_pays(titre, self.pays_defaut)
                date_pub, date_clot = self._extraire_dates(titre)
                
                if date_clot and date_clot < date.today():
                    continue

                if any(o['url_source'] == url_source for o in offres):
                    continue
                
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
                    'organisme': "JOFFRES",
                    'description': f"Opportunité de marché : {titre}",
                    'date_publication': date_pub,
                    'date_cloture': date_clot,
                    'url_source': url_source,
                    'url_tdr': url_tdr,  # ✅ PDF/TDR trouvé
                    'pays': pays,
                    'domaine': domaine,
                    'statut': 'Ouvert',
                    'type_offre': 'APPEL_D_OFFRES',
                    'mode_acquisition': 'AUTO',
                }
                offres.append(offre)
                logger.info(f"  ✅ Appel d'offres extrait (domaine: {domaine}, PDF: {bool(pdf_url)})")
            except Exception as e:
                logger.debug(f"⚠️ Erreur parsing: {e}")
                continue
                
        return offres[:50]
    
    def _extraire_dates(self, texte: str) -> tuple:
        date_pub = date.today() - timedelta(days=1)
        date_clot = date.today() + timedelta(days=30)
        
        patterns = [
            r'(?:date\s*limite|clôture|deadline|limit).*?(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
            r'(?:jusqu\'au|until|before).*?(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
        ]
        for pattern in patterns:
            match = re.search(pattern, texte, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%d/%m/%y']:
                    try:
                        date_clot = date.strptime(date_str, fmt).date()
                        break
                    except ValueError:
                        continue
        return date_pub, date_clot

    def run(self) -> list[dict]:
        logger.info(f"🕷️ JOFFRES scraping: {self.source_url}")
        try:
            soup = self.fetch_and_parse(use_js=True)
            if not soup:
                return []
            return self.parse(soup)
        except Exception as e:
            logger.error(f"❌ Erreur JOFFRES: {e}")
            return []