"""
Parser spécifique pour www.psimali.ml
✅ Gère le format de date français et l'extraction des PDFs
"""
import re
import logging
from datetime import date, datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url
from offres.scraping.extraction_helpers import is_offer_valid
from offres.scraping.constantes import detecter_domaine

logger = logging.getLogger(__name__)


class PSIMaliParser(BaseScraper):
    """Parser spécifique pour PSI Mali"""
    
    # Format date : "mars 17, 2026" ou "février 3, 2026"
    MOIS_FR = {
        'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
        'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
        'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12,
    }
    
    def __init__(self, source_url: str, **kwargs):
        super().__init__(source_url, **kwargs)
        self.base_domain = urlparse(source_url).netloc
        self.pays_defaut = 'ML'  # ✅ Mali par défaut
    
    def parse_date_francais(self, date_str: str) -> date | None:
        """
        ✅ Parse une date au format français : "mars 17, 2026"
        """
        if not date_str:
            return None
        
        date_str = date_str.strip().lower()
        
        # Pattern : "mois jour, année"
        match = re.match(
            r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',
            date_str
        )
        
        if match:
            mois_str = match.group(1)
            jour = int(match.group(2))
            annee = int(match.group(3))
            
            mois = self.MOIS_FR.get(mois_str)
            if mois and 1 <= jour <= 31:
                try:
                    return date(annee, mois, jour)
                except ValueError:
                    pass
        
        return None
    
    def extraire_pdf(self, soup: BeautifulSoup, base_url: str) -> str | None:
        """
        ✅ Extrait l'URL du PDF depuis le bouton "Telecharger"
        """
        if not soup:
            return None
        
        # 1. Chercher les liens avec "Telecharger" ou "Télécharger"
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            texte = link.get_text(strip=True).lower()
            
            # Bouton "Telecharger"
            if 'telecharger' in texte or 'télécharger' in texte:
                # Vérifier si c'est un PDF
                if href.lower().endswith('.pdf'):
                    return normalize_url(href, base_url)
                
                # Sinon, c'est probablement un lien vers le PDF
                if href and not href.startswith('#') and not href.startswith('javascript:'):
                    full_url = normalize_url(href, base_url)
                    # Vérifier si l'URL contient un PDF
                    if '.pdf' in full_url.lower() or '/uploads/' in full_url:
                        return full_url
        
        # 2. Chercher les liens directs .pdf
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if href.lower().endswith('.pdf'):
                return normalize_url(href, base_url)
        
        # 3. Chercher dans wp-content/uploads (WordPress standard)
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if '/wp-content/uploads/' in href:
                return normalize_url(href, base_url)
        
        return None
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        """Parse la page principale et extrait les offres"""
        offres_candidates = []
        
        if not soup:
            return offres_candidates
        
        # PSI Mali utilise des articles WordPress
        # Chercher les conteneurs d'articles
        articles = soup.find_all('article') or soup.find_all('div', class_=re.compile(r'post|entry|item'))
        
        if not articles:
            # Fallback : chercher les liens avec titres d'offres
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                texte = link.get_text(strip=True)
                
                # Vérifier si c'est un lien vers une offre
                if '/2026/' in href or '/2025/' in href:
                    if len(texte) > 20 and any(mot in texte.lower() for mot in [
                        'dao', 'appel d\'offres', 'avis', 'recrutement',
                        'sélection', 'consultant', 'proc'
                    ]):
                        offres_candidates.append({
                            'titre': clean_text(texte)[:300],
                            'description': '',
                            'url_source': urljoin(self.source_url, href),
                        })
        
        for article in articles:
            try:
                # Extraire le titre
                titre_elem = article.find(['h1', 'h2', 'h3', 'a'])
                if not titre_elem:
                    continue
                
                titre = titre_elem.get_text(strip=True)
                
                if not titre or len(titre) < 15:
                    continue
                
                # Vérifier si c'est un appel d'offres
                titre_lower = titre.lower()
                if not any(mot in titre_lower for mot in [
                    'dao', 'appel d\'offres', 'avis', 'recrutement',
                    'sélection', 'consultant', 'proc', 'tender'
                ]):
                    continue
                
                # Extraire l'URL
                url_source = None
                link_elem = article.find('a', href=True)
                if link_elem:
                    href = link_elem.get('href', '')
                    if href and not href.startswith('#'):
                        url_source = urljoin(self.source_url, href)
                
                if not url_source:
                    continue
                
                # Extraire la date
                date_elem = article.find(['time', 'span'], class_=re.compile(r'date|time|posted'))
                date_str = None
                if date_elem:
                    date_str = date_elem.get_text(strip=True)
                else:
                    # Chercher dans le texte
                    texte_article = article.get_text()
                    date_match = re.search(
                        r'(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{1,2},?\s+\d{4}',
                        texte_article,
                        re.IGNORECASE
                    )
                    if date_match:
                        date_str = date_match.group(0)
                
                # Extraire la description
                desc_elem = article.find(['p', 'div'], class_=re.compile(r'excerpt|summary|content'))
                description = desc_elem.get_text(strip=True)[:1000] if desc_elem else ''
                
                offres_candidates.append({
                    'titre': clean_text(titre)[:300],
                    'description': clean_text(description),
                    'url_source': url_source,
                    'date_str': date_str,  # ✅ Date brute à parser
                })
                
            except Exception as e:
                logger.debug(f"⚠️ Erreur extraction article: {e}")
                continue
        
        return offres_candidates
    
    def run(self) -> list[dict]:
        """Exécute le scraping complet"""
        logger.info(f"🕷️ PSIMaliParser: {self.source_url}")
        
        try:
            soup = self.fetch_and_parse(use_js=False)
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
                        offres_valides.append(offre)
                except Exception as e:
                    logger.debug(f"⚠️ Erreur enrichissement: {e}")
                    continue
            
            logger.info(f"✅ PSIMaliParser: {len(offres_valides)} offres extraites")
            return offres_valides
            
        except Exception as e:
            logger.error(f"❌ Erreur PSIMaliParser: {e}")
            return []
    
    def _enrichir_offre(self, candidate: dict) -> dict | None:
        """Enrichit une offre candidate"""
        titre = candidate['titre']
        url_source = candidate['url_source']
        description_base = candidate.get('description', '')
        date_str = candidate.get('date_str')
        
        # Récupérer la page de détail
        detail_soup = self.fetch_page(url_source)
        if not detail_soup:
            logger.debug(f"   ⚠️ Page inaccessible: {url_source[:60]}")
            return None
        
        # ✅ EXTRACTION DE LA DATE (priorité absolue)
        date_pub = None
        
        # 1. Essayer de parser la date du candidat
        if date_str:
            date_pub = self.parse_date_francais(date_str)
            if date_pub:
                logger.info(f"   📅 Date pub (candidate): {date_pub}")
        
        # 2. Chercher dans la page de détail
        if not date_pub:
            # Chercher l'élément time
            time_elem = detail_soup.find('time')
            if time_elem:
                # Vérifier l'attribut datetime
                datetime_attr = time_elem.get('datetime')
                if datetime_attr:
                    try:
                        date_pub = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00')).date()
                    except:
                        pass
                
                # Sinon, parser le texte
                if not date_pub:
                    date_text = time_elem.get_text(strip=True)
                    date_pub = self.parse_date_francais(date_text)
                    if date_pub:
                        logger.info(f"   📅 Date pub (time): {date_pub}")
        
        # 3. Chercher dans le texte complet
        if not date_pub:
            texte_complet = detail_soup.get_text()
            date_match = re.search(
                r'(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{1,2},?\s+\d{4}',
                texte_complet,
                re.IGNORECASE
            )
            if date_match:
                date_pub = self.parse_date_francais(date_match.group(0))
                if date_pub:
                    logger.info(f"   📅 Date pub (texte): {date_pub}")
        
        # 4. Fallback : utiliser aujourd'hui
        if not date_pub:
            date_pub = date.today()
            logger.warning(f"   ⚠️ Date pub non trouvée, fallback: {date_pub}")
        
        # ✅ EXTRACTION DU PDF
        pdf_url = self.extraire_pdf(detail_soup, url_source)
        url_tdr = pdf_url or url_source
        
        if pdf_url:
            logger.info(f"   📄 PDF trouvé: {pdf_url[:60]}")
        
        # ✅ PAYS : ML par défaut (Mali)
        pays = 'ML'
        
        # ✅ DOMAINE
        domaine = detecter_domaine(titre, description_base)
        
        # ✅ DATE DE CLÔTURE : chercher dans le PDF ou la page
        date_cloture = None
        
        # Chercher dans la page
        texte_complet = detail_soup.get_text()
        patterns_cloture = [
            r'(?:date\s*de\s*cl[oô]ture|d[eé]lai|deadline|cl[oô]ture)\s*[:;\s]+(?:le\s+)?(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})',
            r'(?:date\s*de\s*cl[oô]ture|d[eé]lai|deadline)\s*[:;\s]+(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
        ]
        
        for pattern in patterns_cloture:
            match = re.search(pattern, texte_complet, re.IGNORECASE)
            if match:
                groups = match.groups()
                try:
                    if len(groups) == 3 and groups[1].lower() in self.MOIS_FR:
                        jour = int(groups[0])
                        mois = self.MOIS_FR[groups[1].lower()]
                        annee = int(groups[2])
                        date_cloture = date(annee, mois, jour)
                        logger.info(f"   📅 Date clôture trouvée: {date_cloture}")
                        break
                    elif len(groups) == 3:
                        jour = int(groups[0])
                        mois = int(groups[1])
                        annee = int(groups[2])
                        date_cloture = date(annee, mois, jour)
                        logger.info(f"   📅 Date clôture trouvée: {date_cloture}")
                        break
                except:
                    continue
        
        # Fallback : J+30 si pas de date de clôture
        if not date_cloture:
            from datetime import timedelta
            date_cloture = date_pub + timedelta(days=30)
            logger.warning(f"   ⚠️ Date clôture non trouvée, fallback J+30: {date_cloture}")
        
        # ✅ VALIDATION
        if date_cloture < date.today():
            logger.info(f"   ⏭️ REJETÉ (expirée): {titre[:50]}")
            return None
        
        # Construire l'offre
        offre = {
            'titre': titre,
            'organisme': 'PSI Mali',
            'description': description_base[:2000],
            'date_publication': date_pub,
            'date_cloture': date_cloture,
            'url_source': url_source,
            'url_tdr': url_tdr,
            'pays': pays,
            'domaine': domaine,
            'statut': 'Ouvert',
            'type_offre': 'APPEL_D_OFFRES',
            'mode_acquisition': 'AUTO',
        }
        
        logger.info(f"   ✅ {titre[:50]} | {pays} | {domaine} | Pub: {date_pub} | Clôture: {date_cloture}")
        
        return offre