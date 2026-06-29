# offres/scraping/parsers/smart_parser.py
import re
import logging
from datetime import date, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url  # ✅ AJOUT DE normalize_url
from offres.scraping.extraction_helpers import extract_all_details, extract_pdf_url
from offres.scraping.constantes import detecter_domaine
from offres.scraping.country_detector import detecter_pays_smart
from offres.utils.search_keywords import est_appel_offres

logger = logging.getLogger(__name__)


class SmartParser(BaseScraper):
    """Parser intelligent - UNIQUEMENT les appels d'offres"""
    
    MOTS_CLES_OFFRES = ['appel', 'offre', 'tender', 'consultation', 'avis', 'marché', 'recrutement', 'procurement']
    
    def __init__(self, source_url: str, use_js: bool = False, **kwargs):
        super().__init__(source_url, **kwargs)
        self.base_domain = urlparse(source_url).netloc
        self.use_js = use_js
        self.pays_defaut = 'BF'
    
    def detecter_domaine(self, titre, description=""):
        return detecter_domaine(titre, description)
    
    def extraire_pdf_generique(self, soup, base_url="", url_source=""):
        """
        Extraction de PDF générique pour SmartParser
        """
        if not soup:
            return None
        
        # 1. Chercher les liens .pdf directs
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if href.lower().endswith('.pdf'):
                return normalize_url(href, base_url)
        
        # 2. Chercher les liens de téléchargement
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            texte = link.get_text(strip=True).lower()
            
            if any(kw in href.lower() or kw in texte for kw in ['download', 'telecharger', 'télécharger', 'tdr', 'document']):
                return normalize_url(href, base_url)
        
        # 3. Chercher les fichiers dans /sites/default/files/ ou /files/
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if '/sites/default/files/' in href or '/files/' in href or '/documents/' in href:
                return normalize_url(href, base_url)
        
        # 4. Chercher les extensions de documents
        extensions_doc = ['.doc', '.docx', '.xls', '.xlsx', '.pdf']
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            for ext in extensions_doc:
                if href.lower().endswith(ext):
                    return normalize_url(href, base_url)
        
        # 5. Chercher les boutons de téléchargement
        for btn in soup.find_all(['button', 'a']):
            href = btn.get('href', '')
            texte = btn.get_text(strip=True).lower()
            classe = ' '.join(btn.get('class', []))
            
            if 'download' in classe.lower() or 'telecharger' in classe.lower() or 'download' in texte:
                if href:
                    return normalize_url(href, base_url)
        
        # 6. Fallback : URL source si disponible
        if url_source:
            logger.info(f"  📄 Aucun PDF trouvé, utilisation de l'URL source: {url_source[:60]}...")
            return url_source
        
        return None
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        offres = []
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
                
                # ✅ REJET STRICT : UNIQUEMENT les appels d'offres
                if not est_appel_offres(titre):
                    logger.info(f"   ⏭️ REJETÉ (pas un appel d'offres): {titre[:50]}...")
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
                texte_complet = titre + ' ' + description
                
                pays_brut = detecter_pays_smart(texte_complet, url=url_source, pays_defaut=self.pays_defaut)
                pays_iso = 'BF'
                if any(k in str(pays_brut).lower() for k in ['mali', 'ml']): pays_iso = 'ML'
                elif any(k in str(pays_brut).lower() for k in ['niger', 'ne']): pays_iso = 'NE'
                elif any(k in str(pays_brut).lower() for k in ['ivoire', 'ci']): pays_iso = 'CI'
                
                domaine = self.detecter_domaine(texte_complet)
                description = f"Domaine : {domaine}. {description}"
                
                # ✅ Extraire le PDF si disponible
                pdf_url = None
                if url_source:
                    try:
                        detail_soup = self.fetch_page(url_source)
                        if detail_soup:
                            pdf_url = self.extraire_pdf_generique(detail_soup, self.base_url, url_source)
                    except Exception as e:
                        logger.debug(f"⚠️ Erreur extraction PDF: {e}")
                
                # ✅ Si aucun PDF trouvé, utiliser l'URL source
                url_tdr = pdf_url or url_source

                offre = {
                    'titre': clean_text(titre)[:300],
                    'organisme': self.base_domain,
                    'description': description,
                    'date_publication': date.today(),
                    'date_cloture': date.today() + timedelta(days=30),
                    'url_source': url_source,
                    'url_tdr': url_tdr,
                    'pays': pays_iso,
                    'domaine': domaine,
                    'statut': 'Ouvert',
                    'type_offre': 'APPEL_D_OFFRES',
                    'mode_acquisition': 'AUTO',
                }
                offres.append(offre)
                pdf_status = "PDF trouvé" if pdf_url and pdf_url != url_source else "URL source"
                logger.info(f"  ✅ Appel d'offres extrait (domaine: {domaine}, {pdf_status})")
            except Exception as e:
                logger.debug(f"⚠️ Erreur parsing: {e}")
                continue
        return offres
    
    def run(self) -> list[dict]:
        logger.info(f"🕷️ SmartParser: {self.source_url}")
        try:
            soup = self.fetch_and_parse(use_js=self.use_js)
            if not soup:
                return []
            
            offres = self.parse(soup)
            offres_valides = []
            
            for offre in offres:
                if offre.get('url_source'):
                    try:
                        detail_soup = self.fetch_page(offre['url_source'])
                        if detail_soup:
                            details = extract_all_details(detail_soup, url=offre['url_source'], pays_defaut=self.pays_defaut)
                            if details.get('date_cloture'):
                                offre['date_cloture'] = details['date_cloture']
                            if details.get('domaine') and details.get('domaine') != 'Autres':
                                offre['domaine'] = details.get('domaine')
                            # ✅ Mettre à jour le PDF si trouvé
                            pdf_url = self.extraire_pdf_generique(detail_soup, self.base_url, offre['url_source'])
                            if pdf_url:
                                offre['url_tdr'] = pdf_url
                    except Exception as e:
                        logger.debug(f"⚠️ Erreur mise à jour détails: {e}")
                
                if offre.get('date_cloture') and offre['date_cloture'] < date.today():
                    logger.info(f"  ⏭️ EXPIRÉE rejetée: {offre.get('titre', '')[:40]}")
                    continue
                    
                offres_valides.append(offre)
            
            logger.info(f"✅ SmartParser: {len(offres_valides)} offres extraites")
            return offres_valides
        except Exception as e:
            logger.error(f"❌ Erreur SmartParser: {e}")
            return []