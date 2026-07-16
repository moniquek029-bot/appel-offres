"""
Parser spécifique pour Jao Guinée
✅ FILTRAGE STRICT :
- Rejette les offres d'emploi
- Ignore les faux PDFs (liens .pdf qui retournent du HTML)
- Dates de clôture optionnelles (None si non trouvées)
- Pays détecté : GN (Guinée)
"""
import re
import logging
import requests
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


class JaoGuineeParser(BaseScraper):
    """Parser spécifique pour Jao Guinée avec filtrage strict"""
    
    def __init__(self, source_url: str, **kwargs):
        super().__init__(source_url, **kwargs)
        self.base_domain = urlparse(source_url).netloc
        self.pays_defaut = 'GN'  # Guinée
    
    def _est_vrai_pdf(self, url: str) -> bool:
        """Vérifie qu'une URL pointe vers un vrai PDF"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            if response.status_code == 200:
                return response.content.startswith(b'%PDF')
        except Exception as e:
            logger.debug(f"⚠️ Vérification PDF échouée: {e}")
        return False
    
    def _extraire_pdf_valide(self, soup: BeautifulSoup, base_url: str) -> str | None:
        """Extrait uniquement les vrais PDFs (ignore les faux)"""
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            if href.endswith('.pdf'):
                full_url = urljoin(base_url, link.get('href'))
                if self._est_vrai_pdf(full_url):
                    return full_url
                else:
                    logger.warning(f"   ⚠️ Faux PDF ignoré: {full_url[:60]}")
        return None
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        """Parse la page principale avec filtrage strict"""
        offres_candidates = []
        
        if not soup:
            return offres_candidates
        
        # Jao Guinée utilise WordPress avec des articles
        articles = soup.find_all('article')
        
        for article in articles[:30]:
            try:
                # Titre
                titre_elem = article.find(['h2', 'h3', 'a'])
                if not titre_elem:
                    continue
                
                titre = titre_elem.get_text(strip=True)
                
                if not titre or len(titre) < 15:
                    continue
                
                # ✅ FILTRAGE STRICT : Rejeter les offres d'emploi
                if not est_appel_offres(titre):
                    logger.debug(f"   ⏭️ Rejeté (pas un appel d'offres): {titre[:40]}")
                    continue
                
                # URL
                url_source = None
                link_elem = article.find('a', href=True)
                if link_elem:
                    href = link_elem.get('href', '').strip()
                    if href and not href.startswith('#'):
                        url_source = urljoin(self.source_url, href)
                
                if not url_source:
                    continue
                
                description = article.get_text(strip=True)[:1000]
                
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
        logger.info(f"🕷️ JaoGuineeParser: {self.source_url}")
        
        try:
            soup = self.fetch_and_parse(use_js=False)
            if not soup:
                return []
            
            candidates = self.parse(soup)
            if not candidates:
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
            
            logger.info(f"✅ JaoGuineeParser: {len(offres_valides)} offres valides")
            return offres_valides
            
        except Exception as e:
            logger.error(f"❌ Erreur JaoGuineeParser: {e}")
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
        
        # Extraction des dates
        date_pub = extract_publication_date_from_text(texte_complet)
        date_cloture = extract_deadline_from_text(texte_complet)
        
        # Si pas de date de clôture, chercher dans des patterns spécifiques Jao Guinée
        if not date_cloture:
            patterns_specifiques = [
                r'(?:clôture|cloture|deadline|date\s*limite|remise)[:\s]+(?:le\s+)?(\d{1,2})\s+(janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre)\s+(\d{4})',
                r'(?:jusqu\'au|au\s*plus\s*tard\s*le|before)[:\s]+(\d{1,2})\s+(janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre)\s+(\d{4})',
            ]
            
            for pattern in patterns_specifiques:
                match = re.search(pattern, texte_complet, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    if len(groups) >= 3:
                        from offres.scraping.extraction_helpers import _parse_date_groups
                        date_cloture = _parse_date_groups(groups)
                        if date_cloture:
                            logger.info(f"   📅 Clôture JaoGuinée: {date_cloture}")
                            break
        
        # ✅ EXTRACTEUR DE PDF VALIDE (ignore les faux PDFs)
        pdf_url = self._extraire_pdf_valide(detail_soup, url_source)
        url_tdr = pdf_url or url_source  # Fallback vers url_source si pas de PDF
        
        # Pays
        pays = detecter_pays_smart(texte_complet, url=url_source, pays_defaut='GN')
        
        # Domaine
        domaine = detecter_domaine(titre, description_base) or 'Autres'
        
        # ✅ VALIDATION STRICTE
        if not date_pub:
            logger.info(f"   ⏭️ REJETÉ (pas de date publication): {titre[:50]}")
            return None
        
        # Date de clôture OPTIONNELLE (peut être None)
        if date_cloture and date_cloture < date.today():
            logger.info(f"   ⏭️ REJETÉ (expirée {date_cloture}): {titre[:50]}")
            return None
        
        # Trop ancienne
        age_jours = (date.today() - date_pub).days
        if age_jours > 365:
            logger.info(f"   ⏭️ REJETÉ (trop ancienne {age_jours}j): {titre[:50]}")
            return None
        
        offre = {
            'titre': titre,
            'organisme': 'Jao Guinée',
            'description': description_base[:2000],
            'date_publication': date_pub,
            'date_cloture': date_cloture,  # ✅ Peut être None
            'url_source': url_source,
            'url_tdr': url_tdr,  # ✅ url_source si pas de PDF
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