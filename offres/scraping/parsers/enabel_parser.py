"""
Parser spécifique pour Enabel (Belgique)
✅ FILTRAGE STRICT :
- Rejette les offres d'emploi
- Pays détecté : BE (Belgique)
- Dates extraites du HTML
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


class EnabelParser(BaseScraper):
    """Parser spécifique pour Enabel avec filtrage strict"""
    
    def __init__(self, source_url: str, **kwargs):
        super().__init__(source_url, **kwargs)
        self.base_domain = urlparse(source_url).netloc
        self.pays_defaut = 'BE'  # Belgique
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        """Parse la page principale avec filtrage strict"""
        offres_candidates = []
        
        if not soup:
            return offres_candidates
        
        # Enabel utilise plusieurs structures possibles
        conteneurs = []
        
        # Pattern 1 : Articles
        articles = soup.find_all('article')
        if articles:
            conteneurs = articles
        
        # Pattern 2 : Divs avec classes spécifiques
        if not conteneurs:
            conteneurs = soup.find_all('div', class_=re.compile(r'view-content|marche|tender|opportunity|card'))
        
        # Pattern 3 : Lignes de tableau
        if not conteneurs:
            rows = soup.find_all('tr')
            for row in rows[1:]:  # Skip header
                conteneurs.append(row)
        
        # Pattern 4 : Liens avec mots-clés
        if not conteneurs:
            for link in soup.find_all('a', href=True):
                texte = link.get_text(strip=True)
                if len(texte) > 30 and any(mot in texte.lower() for mot in [
                    'marché', 'appel', 'offre', 'tender', 'consultant', 'avis'
                ]):
                    parent = link.find_parent(['div', 'li', 'tr'])
                    if parent and parent not in conteneurs:
                        conteneurs.append(parent)
        
        for conteneur in conteneurs[:30]:
            try:
                # Titre
                titre = None
                for sel in ['h2', 'h3', 'h4', 'a', 'strong', '.title']:
                    elem = conteneur.select_one(sel) if hasattr(conteneur, 'select_one') else conteneur.find(sel)
                    if elem:
                        titre = elem.get_text(strip=True)
                        if len(titre) > 15:
                            break
                
                if not titre or len(titre) < 15:
                    continue
                
                # ✅ FILTRAGE STRICT : Rejeter les offres d'emploi
                if not est_appel_offres(titre):
                    logger.debug(f"   ⏭️ Rejeté (pas un appel d'offres): {titre[:40]}")
                    continue
                
                # URL
                url_source = None
                link_elem = conteneur.find('a', href=True) if hasattr(conteneur, 'find') else None
                if link_elem:
                    href = link_elem.get('href', '').strip()
                    if href and not href.startswith('#') and not href.startswith('javascript:'):
                        url_source = urljoin(self.source_url, href)
                
                if not url_source:
                    continue
                
                description = conteneur.get_text(strip=True)[:1000]
                
                offres_candidates.append({
                    'titre': clean_text(titre)[:300],
                    'description': clean_text(description),
                    'url_source': url_source,
                })
                
            except Exception as e:
                logger.debug(f"⚠️ Erreur extraction: {e}")
                continue
        
        return offres_candidates
    
    def run(self) -> list[dict]:
        """Exécute le scraping complet"""
        logger.info(f"🕷️ EnabelParser: {self.source_url}")
        
        try:
            soup = self.fetch_and_parse(use_js=False)
            if not soup:
                return []
            
            candidates = self.parse(soup)
            if not candidates:
                logger.warning(f"⚠️ Aucun candidat trouvé sur Enabel")
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
            
            logger.info(f"✅ EnabelParser: {len(offres_valides)} offres valides")
            return offres_valides
            
        except Exception as e:
            logger.error(f"❌ Erreur EnabelParser: {e}")
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
        
        # ✅ FILTRAGE STRICT : Re-vérifier que c'est un appel d'offres
        if not est_appel_offres(titre, texte_complet):
            logger.info(f"   ⏭️ REJETÉ (offre d'emploi): {titre[:50]}")
            return None
        
        # Dates
        date_pub = extract_publication_date_from_text(texte_complet)
        date_cloture = extract_deadline_from_text(texte_complet)
        
        # Si pas de dates, chercher dans des éléments spécifiques Enabel
        if not date_pub or not date_cloture:
            for elem in detail_soup.find_all(['td', 'th', 'dt', 'dd', 'li', 'span', 'p']):
                text = elem.get_text(strip=True).lower()
                
                if any(kw in text for kw in ['date de publication', 'publié le', 'posted', 'publication']):
                    next_elem = elem.find_next()
                    if next_elem:
                        date_text = next_elem.get_text(strip=True)
                        parsed = extract_publication_date_from_text(date_text)
                        if parsed and not date_pub:
                            date_pub = parsed
                            logger.info(f"   📅 Pub Enabel: {date_pub}")
                
                if any(kw in text for kw in ['clôture', 'deadline', 'date limite', 'expiration']):
                    next_elem = elem.find_next()
                    if next_elem:
                        date_text = next_elem.get_text(strip=True)
                        parsed = extract_deadline_from_text(date_text)
                        if parsed and not date_cloture:
                            date_cloture = parsed
                            logger.info(f"   📅 Clôture Enabel: {date_cloture}")
        
        # Pays
        pays = detecter_pays_smart(texte_complet, url=url_source, pays_defaut='BE')
        
        # PDF
        pdf_url = None
        for link in detail_soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            if href.endswith('.pdf'):
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
            'organisme': 'Enabel',
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