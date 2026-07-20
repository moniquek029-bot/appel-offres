import re
from datetime import datetime
from bs4 import BeautifulSoup
from offres.scraping.base import BaseScraper
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class DGCMEFParser(BaseScraper):
    """Parser spécialisé pour la DGCMEF (liste de PDF)"""
    
    def __init__(self, source_url, **kwargs):
        super().__init__(source_url, **kwargs)
        self.base_url = "https://www.dgcmef.gov.bf"
        self.source_name = "DGCMEF"
    
    def run(self):
        return self.parse()

    def parse(self):  # ✅ DOIT S'APPELER 'run' ET NON 'parse'
        """Extraction des offres depuis la liste de PDF"""
        offres = []
        
        try:
            # Récupérer la page HTML
            soup = self.fetch_and_parse(use_js=False)
            if not soup:
                logger.error("❌ Impossible de récupérer la page DGCMEF")
                return []
            
            logger.info(f"🔍 Analyse de la page DGCMEF...")
            
            # Stratégie 1 : Chercher les liens dans les listes/blocs
            liens_pdf = self._extraire_liens_pdf(soup)
            
            if not liens_pdf:
                logger.warning("⚠️ Aucun lien PDF trouvé sur la page")
                return []
            
            logger.info(f"✅ {len(liens_pdf)} liens PDF trouvés")
            
            # Traiter chaque lien
            for lien_info in liens_pdf:
                try:
                    offre = self._creer_offre_depuis_pdf(lien_info)
                    if offre:
                        offres.append(offre)
                except Exception as e:
                    logger.debug(f"⚠️ Erreur traitement lien: {e}")
                    continue
            
            return offres
            
        except Exception as e:
            logger.error(f"❌ Erreur parser DGCMEF: {e}")
            return []
    
    def _extraire_liens_pdf(self, soup):
        """Extrait tous les liens PDF/DOC de la page"""
        liens = []
        
        # Sélecteurs communs pour les listes d'appels d'offres
        selecteurs = [
            'a[href*=".pdf"]',
            'a[href*=".doc"]',
            'a[href*=".DOC"]',
            'a[href*=".PDF"]',
            '.download a[href]',
            '.attachment a[href]',
            'li a[href*="pdf"]',
            'p a[href*="pdf"]',
        ]
        
        for selecteur in selecteurs:
            elements = soup.select(selecteur)
            for el in elements:
                href = el.get('href', '')
                if href and ('.pdf' in href.lower() or '.doc' in href.lower()):
                    # Nettoyer l'URL
                    if not href.startswith('http'):
                        href = self.base_url + '/' + href.lstrip('/')
                    
                    # Extraire le texte environnant (titre)
                    titre = self._extraire_titre_proche(el)
                    
                    # Essayer d'extraire une date
                    date_pub = self._extraire_date_proche(el)
                    
                    liens.append({
                        'url': href,
                        'titre': titre or self._extraire_nom_fichier(href),
                        'date_publication': date_pub
                    })
        
        # Supprimer les doublons (basé sur l'URL)
        urls_uniques = {}
        for lien in liens:
            if lien['url'] not in urls_uniques:
                urls_uniques[lien['url']] = lien
        
        return list(urls_uniques.values())
    
    def _extraire_titre_proche(self, element):
        """Essaie de trouver un titre près du lien PDF"""
        if element.get_text(strip=True):
            texte = element.get_text(strip=True)
            if len(texte) > 10 and 'pdf' not in texte.lower():
                return texte
        
        parent = element.parent
        if parent:
            for tag in ['strong', 'b', 'h3', 'h4', 'h5', 'h6']:
                found = parent.find(tag)
                if found and found.get_text(strip=True):
                    return found.get_text(strip=True)
            
            texte_parent = parent.get_text(strip=True)
            if texte_parent and len(texte_parent) > 10:
                texte_parent = re.sub(r'\s*(PDF|DOC|Télécharger|Download)\s*', '', texte_parent, flags=re.IGNORECASE)
                return texte_parent.strip()
        
        return None
    
    def _extraire_date_proche(self, element):
        """Essaie d'extraire une date près du lien"""
        parent = element.parent
        if parent:
            texte = parent.get_text()
            dates_trouvees = self._trouver_dates_dans_texte(texte)
            if dates_trouvees:
                return dates_trouvees[0]
        
        return timezone.now().date()
    
    def _trouver_dates_dans_texte(self, texte):
        """Trouve des dates dans un texte (format JJ/MM/AAAA ou JJ mois AAAA)"""
        dates = []
        
        # Pattern 1: 12/03/2024
        pattern1 = r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b'
        for match in re.finditer(pattern1, texte):
            try:
                jour, mois, annee = match.groups()
                date_obj = datetime(int(annee), int(mois), int(jour)).date()
                dates.append(date_obj)
            except:
                continue
        
        # Pattern 2: 12 mars 2024
        mois_fr = {
            'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
            'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
            'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
        }
        pattern2 = r'\b(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})\b'
        for match in re.finditer(pattern2, texte, re.IGNORECASE):
            try:
                jour, mois_str, annee = match.groups()
                mois_num = mois_fr.get(mois_str.lower())
                if mois_num:
                    date_obj = datetime(int(annee), mois_num, int(jour)).date()
                    dates.append(date_obj)
            except:
                continue
        
        return dates
    
    def _extraire_nom_fichier(self, url):
        """Extrait le nom du fichier depuis l'URL"""
        nom_fichier = url.split('/')[-1]
        nom_fichier = re.sub(r'\.(pdf|doc|docx)$', '', nom_fichier, flags=re.IGNORECASE)
        nom_fichier = nom_fichier.replace('_', ' ').replace('-', ' ')
        nom_fichier = re.sub(r'\s+', ' ', nom_fichier).strip()
        return nom_fichier if nom_fichier else "Appel d'offres"
    
    def _creer_offre_depuis_pdf(self, lien_info):
        """Crée un dictionnaire offre depuis les infos du lien PDF"""
        return {
            'titre': lien_info['titre'],
            'organisme': 'DGCMEF - Burkina Faso',
            'description': f"Avis d'appel d'offres publié par la DGCMEF. Document: {lien_info['titre']}",
            'pays': 'BF',
            'domaine': self._detecter_domaine(lien_info['titre']),
            'date_publication': lien_info['date_publication'],
            'date_cloture': None,
            'url_source': self.source_url,
            'url_tdr': lien_info['url'],
            'type_offre': 'APPEL_D_OFFRES',
            'statut': 'Ouvert'
        }
    
    def _detecter_domaine(self, titre):
        """Déduit le domaine depuis le titre"""
        titre_lower = titre.lower()
        
        if any(mot in titre_lower for mot in ['travaux', 'construction', 'bâtiment', 'route', 'infrastructure']):
            return 'Ingénierie & Construction'
        elif any(mot in titre_lower for mot in ['santé', 'médical', 'hôpital', 'clinique']):
            return 'Santé & Médical'
        elif any(mot in titre_lower for mot in ['informatique', 'numérique', 'software', 'IT']):
            return 'IT & Digital'
        elif any(mot in titre_lower for mot in ['formation', 'éducation', 'école', 'université']):
            return 'Éducation & Formation'
        elif any(mot in titre_lower for mot in ['audit', 'consulting', 'conseil', 'étude']):
            return 'Finance, Audit & Conseil'
        elif any(mot in titre_lower for mot in ['fourniture', 'équipement', 'matériel']):
            return 'Fournitures & Équipements'
        else:
            return 'Autres'