"""
Smart Parser - VERSION STRICTE SANS FALLBACK
✅ Si une donnée essentielle n'est pas trouvée → REJET de l'offre
"""
import re
import logging
from datetime import date, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url
from offres.scraping.extraction_helpers import (
    extract_all_details, extract_pdf_url, is_offer_valid,
    extract_publication_date_from_text, extract_deadline_from_text
)
from offres.scraping.constantes import detecter_domaine
from offres.scraping.country_detector import detecter_pays_smart
from offres.utils.search_keywords import est_appel_offres
from offres.utils.search_keywords import detecter_domaine

logger = logging.getLogger(__name__)


class SmartParser(BaseScraper):
    """Parser intelligent SANS valeurs par défaut"""
    
    MOTS_CLES_OFFRES = ['appel', 'offre', 'tender', 'consultation', 'avis', 'marché', 'recrutement', 'procurement']
    
    def __init__(self, source_url: str, use_js: bool = False, **kwargs):
        super().__init__(source_url, **kwargs)
        self.base_domain = urlparse(source_url).netloc
        self.use_js = use_js
        # ✅ PAS de pays_defaut ici, on laisse le détecteur faire
    
    def extraire_pdf_generique(self, soup, base_url="", url_source=""):
        """Extrait l'URL d'un PDF"""
        if not soup:
            return None
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if href.lower().endswith('.pdf'):
                return normalize_url(href, base_url)
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            texte = link.get_text(strip=True).lower()
            if any(kw in href.lower() or kw in texte for kw in ['download', 'telecharger', 'télécharger', 'tdr', 'document']):
                return normalize_url(href, base_url)
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if '/sites/default/files/' in href or '/files/' in href or '/documents/' in href:
                return normalize_url(href, base_url)
        
        return None
    
    def extraire_dates_depuis_pdf(self, pdf_url: str):
        """Extrait les dates depuis un PDF"""
        if not pdf_url or not pdf_url.endswith('.pdf'):
            return None, None
        
        try:
            from offres.scraping.pdf_date_extractor import extract_dates_from_pdf
            logger.info(f"   📥 Extraction PDF: {pdf_url[:60]}")
            return extract_dates_from_pdf(pdf_url)
        except Exception as e:
            logger.warning(f"   ⚠️ Erreur PDF: {e}")
            return None, None
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        """Parse la page principale"""
        offres_candidates = []
        conteneurs = []
        
        for sel in ['article', 'div.card', 'div.item', '.views-row']:
            found = soup.select(sel)
            if len(found) >= 2:
                conteneurs = found
                break
        
        if not conteneurs:
            for link in soup.find_all('a', href=True):
                texte = link.get_text(strip=True)
                if len(texte) > 35 and any(mot in texte.lower() for mot in self.MOTS_CLES_OFFRES):
                    parent = link.find_parent(['div', 'article', 'li'])
                    if parent and parent not in conteneurs:
                        conteneurs.append(parent)
        
        for conteneur in conteneurs[:20]:
            try:
                titre = None
                for sel in ['h1', 'h2', 'h3', 'h4', 'h5', '.title', 'a.title']:
                    elem = conteneur.select_one(sel)
                    if elem:
                        titre = elem.get_text(strip=True)
                        break
                
                if not titre or len(titre) < 15:
                    continue
                
                if not est_appel_offres(titre):
                    continue
                
                url_source = None
                for link in conteneur.find_all('a', href=True):
                    href = link.get('href', '').strip()
                    if href and not href.startswith('#') and not href.startswith('javascript:'):
                        url_source = urljoin(self.base_url, href)
                        break
                
                if not url_source:
                    continue
                
                description = conteneur.get_text(strip=True)[:1000]
                
                offres_candidates.append({
                    'titre': clean_text(titre)[:300],
                    'description': description,
                    'url_source': url_source,
                })
                
            except Exception as e:
                logger.debug(f"⚠️ Erreur extraction: {e}")
                continue
        
        return offres_candidates
    
    def run(self) -> list[dict]:
        """Exécute le scraping"""
        logger.info(f"🕷️ SmartParser: {self.source_url}")
        try:
            soup = self.fetch_and_parse(use_js=self.use_js)
            if not soup:
                return []
            
            candidates = self.parse(soup)
            if not candidates:
                return []
            
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
            
            logger.info(f"✅ SmartParser: {len(offres_valides)} offres extraites")
            return offres_valides
        except Exception as e:
            logger.error(f"❌ Erreur SmartParser: {e}")
            return []
    
    def _enrichir_offre(self, candidate: dict) -> dict | None:
        """
        ✅ SANS AUCUNE VALEUR PAR DÉFAUT
        - Pas de date de clôture → None
        - Pas de PDF → url_source comme url_tdr
        """
        titre = candidate['titre']
        url_source = candidate['url_source']
        description_base = candidate.get('description', '')
        
        # ✅ VÉRIFIER QUE C'EST UN APPEL D'OFFRES (pas une offre d'emploi)
        if not est_appel_offres(titre, description_base):
            logger.info(f"   ⏭️ REJETÉ (pas un appel d'offres): {titre[:50]}")
            return None
        
        # Page de détail
        detail_soup = self.fetch_page(url_source)
        if not detail_soup:
            logger.debug(f"   ⚠️ Page inaccessible: {url_source[:60]}")
            return None
        
        # Extraction des détails
        details = extract_all_details(
            detail_soup,
            url=url_source,
            pays_defaut=None,  # ✅ AUCUN pays par défaut
            titre=titre,
            description=description_base
        )
        
        date_pub = details.get('date_publication')
        date_cloture = details.get('date_cloture')  # ✅ Peut être None
        pays = details.get('pays')
        organisme = details.get('organisme')
        domaine = details.get('domaine')
        
        # Texte complet pour détections supplémentaires
        texte_complet = f"{titre} {description_base} {details.get('texte_complet', '')}"
        
        # Si pas de pays, essayer avec le texte complet
        if not pays:
            pays = detecter_pays_smart(texte_complet, url=url_source, pays_defaut=None)
        
        # PDF
        pdf_url = self.extraire_pdf_generique(detail_soup, self.base_domain, url_source)
        
        # ✅ Vérifier que c'est un vrai PDF
        vrai_pdf = False
        if pdf_url and pdf_url.endswith('.pdf'):
            try:
                import requests
                response = requests.get(pdf_url, timeout=15, verify=False)
                if response.status_code == 200 and response.content.startswith(b'%PDF'):
                    vrai_pdf = True
                    url_tdr = pdf_url
                else:
                    logger.warning(f"   ⚠️ Lien PDF invalide (HTML): {pdf_url[:60]}")
            except:
                pass
        
        # ✅ SI PAS DE VRAI PDF → url_tdr = url_source
        if not vrai_pdf:
            url_tdr = url_source
            logger.info(f"   🔗 Pas de PDF → url_tdr = url_source")
        
        # Essayer d'extraire les dates depuis le PDF si manquantes
        if vrai_pdf and (not date_pub or not date_cloture):
            logger.info(f"   📥 Extraction PDF pour dates...")
            date_pub_pdf, date_cloture_pdf = self.extraire_dates_depuis_pdf(pdf_url)
            
            if date_pub_pdf and not date_pub:
                date_pub = date_pub_pdf
                logger.info(f"   ✅ Pub PDF: {date_pub}")
            
            if date_cloture_pdf and not date_cloture:
                date_cloture = date_cloture_pdf
                logger.info(f"   ✅ Clôture PDF: {date_cloture}")
        
        # ========================================================================
        # ✅ VALIDATION STRICTE
        # ========================================================================
        
        # Date de publication OBLIGATOIRE
        if not date_pub:
            logger.info(f"   ⏭️ REJETÉ (pas de date publication): {titre[:50]}")
            return None
        
        # Pays OBLIGATOIRE
        if not pays:
            logger.info(f"   ⏭️ REJETÉ (pas de pays): {titre[:50]}")
            return None
        
        # Date de clôture OPTIONNELLE (peut être None)
        # ❌ PAS DE J+30 PAR DÉFAUT
        
        # Si date de clôture existe, vérifier expiration
        if date_cloture and date_cloture < date.today():
            logger.info(f"   ⏭️ REJETÉ (expirée {date_cloture}): {titre[:50]}")
            return None
        
        # Offre trop ancienne
        age_jours = (date.today() - date_pub).days
        if age_jours > 365:
            logger.info(f"   ⏭️ REJETÉ (trop ancienne {age_jours}j): {titre[:50]}")
            return None
        
        # Organisme : nom de domaine si non trouvé
        if not organisme:
            organisme = self.base_domain
        
        # Domaine : détection si non trouvé
        if not domaine:
            domaine = detecter_domaine(titre, description_base) or 'Autres'
        
        offre = {
            'titre': titre,
            'organisme': organisme,
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
        pdf_status = "📄 PDF" if vrai_pdf else "🔗 URL source"
        logger.info(f"   ✅ {titre[:50]} | {pays} | {domaine} | {pdf_status} | Pub: {date_pub} | {cloture_info}")
        
        return offre