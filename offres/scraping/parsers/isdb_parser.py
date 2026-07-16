"""
Parser spécifique pour ISDB (Banque Islamique de Développement)
✅ FILTRAGE STRICT :
- Rejette les offres d'emploi
- Pays détecté depuis le contenu
- Dates extraites du HTML et PDF
- Dates de clôture optionnelles
"""
import re
import logging
from datetime import date, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url
from offres.scraping.extraction_helpers import (
    extract_publication_date_from_text,
    extract_deadline_from_text,
    is_offer_valid 
)
from offres.scraping.country_detector import detecter_pays_smart
from offres.utils.search_keywords import est_appel_offres, detecter_domaine

logger = logging.getLogger(__name__)


class ISDBParser(BaseScraper):
    """Parser spécifique pour ISDB avec filtrage strict"""
    
    def __init__(self, source_url: str, **kwargs):
        super().__init__(source_url, **kwargs)
        self.base_domain = urlparse(source_url).netloc
        self.pays_defaut = 'GLOBAL'
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        """Parse la page principale avec filtrage strict"""
        offres_candidates = []
        
        if not soup:
            return offres_candidates
        
        # ISDB utilise des tableaux ou des listes structurées
        # Pattern 1 : Tableaux
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    link = cells[0].find('a', href=True)
                    if link:
                        titre = link.get_text(strip=True)
                        href = link.get('href', '')
                        
                        if titre and len(titre) > 15 and href:
                            # ✅ FILTRAGE STRICT
                            if not est_appel_offres(titre):
                                continue
                            
                            url_source = urljoin(self.source_url, href)
                            description = row.get_text(strip=True)[:1000]
                            
                            offres_candidates.append({
                                'titre': clean_text(titre)[:300],
                                'description': clean_text(description),
                                'url_source': url_source,
                            })
        
        # Pattern 2 : Divs avec classe spécifique ISDB
        if not offres_candidates:
            divs = soup.find_all('div', class_=re.compile(r'view-content|tender|procurement|notice'))
            for div in divs:
                link = div.find('a', href=True)
                if link:
                    titre = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    if titre and len(titre) > 15 and href:
                        if not est_appel_offres(titre):
                            continue
                        
                        url_source = urljoin(self.source_url, href)
                        description = div.get_text(strip=True)[:1000]
                        
                        offres_candidates.append({
                            'titre': clean_text(titre)[:300],
                            'description': clean_text(description),
                            'url_source': url_source,
                        })
        
        # Pattern 3 : Liens génériques
        if not offres_candidates:
            for link in soup.find_all('a', href=True):
                texte = link.get_text(strip=True)
                href = link.get('href', '')
                
                if len(texte) > 30 and any(mot in texte.lower() for mot in [
                    'consultancy', 'works', 'goods', 'services', 'eoi', 'rfq', 'spn'
                ]):
                    if href and not href.startswith('#'):
                        if not est_appel_offres(texte):
                            continue
                        
                        url_source = urljoin(self.source_url, href)
                        
                        offres_candidates.append({
                            'titre': clean_text(texte)[:300],
                            'description': '',
                            'url_source': url_source,
                        })
        
        return offres_candidates
    
    def run(self) -> list[dict]:
        """Exécute le scraping complet"""
        logger.info(f"🕷️ ISDBParser: {self.source_url}")
        
        try:
            soup = self.fetch_and_parse(use_js=False)
            if not soup:
                return []
            
            candidates = self.parse(soup)
            if not candidates:
                logger.warning(f"⚠️ Aucun candidat trouvé sur ISDB")
                return []
            
            logger.info(f"📊 {len(candidates)} candidats après filtrage")
            
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
            
            logger.info(f"✅ ISDBParser: {len(offres_valides)} offres valides")
            return offres_valides
            
        except Exception as e:
            logger.error(f"❌ Erreur ISDBParser: {e}")
            return []
    
    def _enrichir_offre(self, candidate: dict) -> dict | None:
        """Enrichit une offre avec filtrage strict"""
        titre = candidate['titre']
        url_source = candidate['url_source']
        description_base = candidate.get('description', '')
        
        # Page de détail
        detail_soup = self.fetch_page(url_source)
        if not detail_soup:
            logger.debug(f"   ⚠️ Page inaccessible: {url_source[:60]}")
            return None
        
        texte_complet = detail_soup.get_text(separator=' ')
        
        # ✅ FILTRAGE STRICT : Re-vérifier
        if not est_appel_offres(titre, texte_complet):
            logger.info(f"   ⏭️ REJETÉ (offre d'emploi): {titre[:50]}")
            return None
        
        # Dates - ISDB a souvent les dates dans des balises spécifiques
        date_pub = None
        date_cloture = None
        
        for elem in detail_soup.find_all(['td', 'th', 'dt', 'dd', 'div', 'span']):
            text = elem.get_text(strip=True).lower()
            
            if any(kw in text for kw in ['posted', 'publication', 'published', 'date de publication']):
                next_elem = elem.find_next()
                if next_elem:
                    date_text = next_elem.get_text(strip=True)
                    parsed = extract_publication_date_from_text(date_text)
                    if parsed and not date_pub:
                        date_pub = parsed
                        logger.info(f"   📅 Pub ISDB: {date_pub}")
            
            if any(kw in text for kw in ['deadline', 'closing', 'clôture', 'date limite']):
                next_elem = elem.find_next()
                if next_elem:
                    date_text = next_elem.get_text(strip=True)
                    parsed = extract_deadline_from_text(date_text)
                    if parsed and not date_cloture:
                        date_cloture = parsed
                        logger.info(f"   📅 Clôture ISDB: {date_cloture}")
        
        # Fallback
        if not date_pub:
            date_pub = extract_publication_date_from_text(texte_complet)
        
        if not date_cloture:
            date_cloture = extract_deadline_from_text(texte_complet)
        
        # Pays
        pays = detecter_pays_smart(texte_complet, url=url_source, pays_defaut='GLOBAL')
        
        # PDF
        pdf_url = None
        for link in detail_soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            text = link.get_text(strip=True).lower()
            
            if href.endswith('.pdf') or any(kw in text for kw in ['download', 'télécharger']):
                pdf_url = urljoin(url_source, link.get('href'))
                break
        
        url_tdr = pdf_url or url_source
        
        # Domaine
        domaine = detecter_domaine(titre, description_base) or 'Autres'
        
        # ✅ VALIDATION STRICTE
        if not date_pub:
            logger.info(f"   ⏭️ REJETÉ (pas de date publication): {titre[:50]}")
            return None
        
        # Date de clôture OPTIONNELLE
        if date_cloture and date_cloture < date.today():
            logger.info(f"   ⏭️ REJETÉ (expirée): {titre[:50]}")
            return None
        
        age_jours = (date.today() - date_pub).days
        if age_jours > 365:
            logger.info(f"   ⏭️ REJETÉ (trop ancienne): {titre[:50]}")
            return None
        
        offre = {
            'titre': titre,
            'organisme': 'ISDB',
            'description': description_base[:2000],
            'date_publication': date_pub,
            'date_cloture': date_cloture,  # ✅ Peut être None
            'url_source': url_source,
            'url_tdr': url_tdr,
            'pays': pays,
            'domaine': domaine,
            'statut': 'Ouvert',
            'type_offre': 'APPEL_D_OFFRES',
            'mode_acquisition': 'AUTO',
        }
        
        cloture_info = f"Clôture: {date_cloture}" if date_cloture else "Clôture: None"
        pdf_status = "📄 PDF" if pdf_url else "🔗 URL source"
        logger.info(f"   ✅ {titre[:50]} | {pays} | {domaine} | {pdf_status} | Pub: {date_pub} | {cloture_info}")
        
        return offre