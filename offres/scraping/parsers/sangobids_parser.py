"""
Parser pour SangoBids Burkina
URL: https://bf.sangobids.com/tenders
"""
import re
import logging
from datetime import date
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text
from offres.scraping.extraction_helpers import (
    extract_publication_date_from_text,
    extract_deadline_from_text,
    is_offer_valid
)
from offres.utils.search_keywords import est_appel_offres, detecter_domaine

logger = logging.getLogger(__name__)


class SangoBidsParser(BaseScraper):
    """Parser robuste pour SangoBids, indépendant des classes CSS fragiles"""
    
    def __init__(self, source_url: str, **kwargs):
        super().__init__(source_url, **kwargs)
        self.base_domain = urlparse(source_url).netloc
        self.pays_defaut = 'BF'
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        """Parse la page de liste en cherchant des liens pertinents"""
        offres_candidates = []
        if not soup:
            return offres_candidates
        
        for link in soup.find_all('a', href=True):
            texte = link.get_text(strip=True)
            
            if len(texte) > 20 and any(mot in texte.lower() for mot in [
                'appel d\'offres', 'avis', 'manifestation d\'intérêt', 
                'consultation', 'marché', 'expression of interest'
            ]):
                href = link.get('href', '').strip()
                
                if any(skip in href.lower() for skip in ['login', 'register', 'faq', 'blog', 'pricing', '#']):
                    continue
                
                if href.startswith('/'):
                    url_source = f"https://bf.sangobids.com{href}"
                elif href.startswith('http'):
                    url_source = href
                else:
                    url_source = urljoin(self.source_url, href)
                
                if any(c['url_source'] == url_source for c in offres_candidates):
                    continue
                
                offres_candidates.append({
                    'titre': clean_text(texte)[:300],
                    'description': texte[:500],
                    'url_source': url_source,
                })
                
                if len(offres_candidates) >= 30:
                    break
                    
        return offres_candidates
    
    def run(self) -> list[dict]:
        """Exécute le scraping"""
        logger.info(f"🕷️ SangoBidsParser: {self.source_url}")
        try:
            soup = self.fetch_and_parse(use_js=False)
            if not soup:
                return []
            
            candidates = self.parse(soup)
            logger.info(f"📊 {len(candidates)} candidats trouvés sur la page de liste")
            
            offres_valides = []
            for candidate in candidates:
                try:
                    offre = self._enrichir_offre(candidate)
                    if offre:
                        is_valid, reason = is_offer_valid(offre)
                        if not is_valid:
                            logger.info(f"  ⏭️ REJETÉ: {reason} - {offre.get('titre', '')[:40]}")
                            continue
                        offres_valides.append(offre)
                except Exception as e:
                    logger.debug(f"⚠️ Erreur enrichissement: {e}")
                    continue
            
            logger.info(f"✅ SangoBidsParser: {len(offres_valides)} offres valides extraites")
            return offres_valides
            
        except Exception as e:
            logger.error(f"❌ Erreur SangoBidsParser: {e}")
            return []
    
    def _enrichir_offre(self, candidate: dict) -> dict | None:
        """Enrichit une offre en extrayant les détails de la page cible"""
        titre = candidate['titre']
        url_source = candidate['url_source']
        
        detail_soup = self.fetch_page(url_source)
        if not detail_soup:
            return None
        
        texte_complet = detail_soup.get_text(separator=' ', strip=True)
        
        date_pub = None
        date_cloture = None
        
        match_pub = re.search(r'Publié le\s+(?:\n\s*)+([^\n]+)', texte_complet, re.IGNORECASE)
        if match_pub:
            date_str = match_pub.group(1).strip()
            date_pub = extract_publication_date_from_text(f"Publié le {date_str}")
            
        match_clot = re.search(r'Date limite\s+(?:\n\s*)+([^\n]+)', texte_complet, re.IGNORECASE)
        if match_clot:
            date_str = match_clot.group(1).strip()
            date_cloture = extract_deadline_from_text(f"Date limite {date_str}")
            
        if not date_pub:
            date_pub = extract_publication_date_from_text(texte_complet)
        if not date_cloture:
            date_cloture = extract_deadline_from_text(texte_complet)
        
        organisme = "SangoBids"
        match_org = re.search(r'Autorité contractante\s+(?:\n\s*)+([^\n]+)', texte_complet, re.IGNORECASE)
        if match_org:
            organisme = clean_text(match_org.group(1).strip())
        
        # ✅ CORRECTION : Forcer le pays à BF pour ce site spécifique
        pays = 'BF'
        
        pdf_url = None
        for link in detail_soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            texte_link = link.get_text(strip=True).lower()
            if href.endswith('.pdf') or 'pdf' in texte_link or 'télécharger' in texte_link:
                if href.startswith('http'):
                    pdf_url = href
                else:
                    pdf_url = urljoin(url_source, href)
                break
        
        url_tdr = pdf_url or url_source
        
        if not date_pub:
            logger.info(f"   ⏭️ REJETÉ (pas de date publication): {titre[:50]}")
            return None
            
        if date_cloture and date_cloture < date.today():
            logger.info(f"   ⏭️ REJETÉ (expirée): {titre[:50]}")
            return None
            
        return {
            'titre': titre,
            'organisme': organisme,
            'description': candidate.get('description', '')[:2000],
            'date_publication': date_pub,
            'date_cloture': date_cloture,
            'url_source': url_source,
            'url_tdr': url_tdr,
            'pays': pays,
            'domaine': detecter_domaine(titre, candidate.get('description', '')) or 'Autres',
            'statut': 'Ouvert',
            'type_offre': 'APPEL_D_OFFRES',
            'mode_acquisition': 'AUTO',
        }