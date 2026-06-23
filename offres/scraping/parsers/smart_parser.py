# offres/scraping/parsers/smart_parser.py
# SmartParser Ultra-Intelligent - Fonctionne avec N'IMPORTE QUEL site

import re
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import date, timedelta

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url, parse_french_date, detecter_pays

logger = logging.getLogger(__name__)


class SmartParser(BaseScraper):
    """
    Parser ultra-intelligent et adaptatif.
    Fonctionne avec N'IMPORTE QUEL site d'appels d'offres.
    Détecte automatiquement : pays, PDF/TDR, dates, montants.
    """
    
    # Mots-clés pour détecter les documents
    MOTS_CLES_DOCUMENTS = [
        'tdr', 'pdf', 'document', 'annexe', 'cahier', 'dossier',
        'tender', 'dossier de consultation', 'règlement', 'spécification',
        'termes de référence', 'terms of reference', 'bidding document',
        'avis', 'manifestation', 'dao', 'dce', 'download', 'télécharger'
    ]
    
    # Extensions de fichiers
    EXTENSIONS_DOCUMENTS = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar']
    
    # Mots-clés pour identifier les offres
    MOTS_CLES_OFFRES = [
        'appel', 'offre', 'tender', 'consultation', 'avis', 'marché',
        'recrutement', 'bidding', 'procurement', 'rfp', 'rfq', 'ito',
        'projet', 'programme', 'subvention', 'grant', 'contrat'
    ]
    
    def __init__(self, source_url: str, **kwargs):
        super().__init__(source_url, **kwargs)
        self.base_domain = urlparse(source_url).netloc
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        """Analyse la structure de la page pour en extraire des offres."""
        offres = []
        conteneurs = self._trouver_conteneurs(soup)
        
        logger.info(f"🔍 SmartParser: {len(conteneurs)} conteneurs potentiels détectés")
        
        for conteneur in conteneurs:
            try:
                # 1. Extraire le titre
                titre = self._extraire_titre(conteneur)
                if not titre or len(titre) < 15:
                    continue
                
                # 2. Vérifier que c'est une offre
                if not self._est_une_offre(titre):
                    continue
                
                # 3. Extraire le lien
                url_source = self._extraire_lien(conteneur)
                if not url_source:
                    continue
                
                # 4. Organisme
                organisme = self._extraire_organisme(conteneur) or self.base_domain
                
                # 5. Date de clôture
                date_cloture = self._extraire_date(conteneur)
                
                # 6. Description
                description = self._extraire_description(conteneur)
                
                # 7. 🎯 DÉTECTION AUTOMATIQUE DU PAYS
                pays = self._detecter_pays(titre + ' ' + description)
                
                # 8. Montant (optionnel)
                montant = self._extraire_montant(conteneur.get_text())
                
                offre = {
                    'titre': clean_text(titre)[:300],
                    'organisme': clean_text(organisme)[:200],
                    'description': description[:500],
                    'date_publication': date.today(),
                    'date_cloture': date_cloture,
                    'url_source': url_source,
                    'url_tdr': None,  # Sera rempli dans run()
                    'pays': pays,  # ← PAYS DÉTECTÉ AUTOMATIQUEMENT
                    'statut': 'Ouvert',
                    'mode_acquisition': 'AUTO',
                }
                
                # Ajouter le montant s'il existe
                if montant:
                    offre['description'] += f"\n\n💰 Montant : {montant}"
                
                offres.append(offre)
                
            except Exception as e:
                logger.debug(f"⚠️ Erreur parsing conteneur: {e}")
                continue
        
        logger.info(f"✅ SmartParser: {len(offres)} offre(s) extraite(s)")
        return offres[:50]
    
    def _est_une_offre(self, texte: str) -> bool:
        """Vérifie si le texte correspond à une offre."""
        texte_lower = texte.lower()
        score = sum(1 for mot in self.MOTS_CLES_OFFRES if mot in texte_lower)
        return score > 0 or len(texte) > 30
    
    def _detecter_pays(self, texte: str) -> str:
        """🎯 DÉTECTION AUTOMATIQUE DU PAYS depuis le texte"""
        # Utiliser la fonction utilitaire si disponible
        try:
            return detecter_pays(texte, self.pays_defaut)
        except:
            pass
        
        # Fallback : détection manuelle
        pays_mapping = {
            'burkina': 'BF', 'bf': 'BF', 'ouagadougou': 'BF',
            'sénégal': 'SN', 'senegal': 'SN', 'dakar': 'SN',
            'côte d\'ivoire': 'CI', 'ci': 'CI', 'abidjan': 'CI',
            'mali': 'ML', 'bamako': 'ML',
            'niger': 'NE', 'niamey': 'NE',
            'togo': 'TG', 'lomé': 'TG', 'lome': 'TG',
            'bénin': 'BJ', 'benin': 'BJ', 'cotonou': 'BJ',
            'guinée': 'GN', 'conakry': 'GN',
            'cameroun': 'CM', 'yaoundé': 'CM',
            'rdc': 'CD', 'congo': 'CD', 'kinshasa': 'CD',
            'tchad': 'TD', 'ndjamena': 'TD',
            'gabon': 'GA', 'libreville': 'GA',
            'france': 'FR', 'paris': 'FR',
            'belgique': 'BE', 'bruxelles': 'BE',
            'canada': 'CA', 'ottawa': 'CA',
            'états-unis': 'US', 'usa': 'US', 'washington': 'US',
        }
        
        texte_lower = texte.lower()
        for mot, code in pays_mapping.items():
            if mot in texte_lower:
                return code
        
        return self.pays_defaut
    
    def _trouver_conteneurs(self, soup: BeautifulSoup) -> list:
        """Identifie les blocs répétitifs."""
        conteneurs = []
        
        # Sélecteurs CSS courants
        selecteurs = [
            'div.offre', 'div.offer', 'div.tender', 'div.appel-offre',
            'div.ao-item', 'div.listing-item', 'div.job-item',
            'article', 'div.item', 'div.post', 'div.card',
            '.views-row', '.node', '.result-item', '.tender-item',
            'li.list-group-item', 'div.row-item', 'div.procurement-item',
            'table tbody tr', 'div.search-result', 'div.bid-item'
        ]
        
        for selecteur in selecteurs:
            trouves = soup.select(selecteur)
            if len(trouves) >= 2:
                return trouves
        
        # Détection heuristique
        divs = soup.find_all(['div', 'article', 'section'], recursive=True)
        groupes = {}
        for div in divs:
            classes = ' '.join(div.get('class', []))
            if classes:
                if classes not in groupes:
                    groupes[classes] = []
                groupes[classes].append(div)
        
        if groupes:
            meilleur_groupe = max(groupes.values(), key=len)
            if len(meilleur_groupe) >= 3:
                return meilleur_groupe
        
        # Fallback sur les liens longs
        for link in soup.find_all('a', href=True):
            texte = link.get_text(strip=True)
            if len(texte) > 35 and self._est_une_offre(texte):
                parent = link.find_parent(['div', 'article', 'li', 'tr', 'section'])
                if parent and parent not in conteneurs:
                    conteneurs.append(parent)
        
        return conteneurs
    
    def _extraire_titre(self, conteneur) -> str:
        """Extrait le titre."""
        selecteurs_titre = [
            'h1', 'h2', 'h3', 'h4', 'h5',
            '.title', '.titre', '.offer-title', '.tender-title',
            '.name', '.heading', 'a.title', 'strong.title'
        ]
        
        for sel in selecteurs_titre:
            elem = conteneur.select_one(sel)
            if elem:
                texte = elem.get_text(strip=True)
                if len(texte) > 10:
                    return texte
        
        # Fallback : lien le plus long
        liens = conteneur.find_all('a', href=True)
        if liens:
            liens_tries = sorted(liens, key=lambda x: len(x.get_text(strip=True)), reverse=True)
            texte = liens_tries[0].get_text(strip=True)
            if len(texte) > 15:
                return texte
        
        return conteneur.get_text(strip=True)[:200]
    
    def _extraire_lien(self, conteneur) -> str | None:
        """Trouve l'URL vers la fiche descriptive."""
        liens = conteneur.find_all('a', href=True)
        
        # Stratégie 1 : Lien avec mot-clé
        for link in liens:
            href = link.get('href', '').strip()
            texte = link.get_text().lower()
            
            if href and not href.startswith('#') and not href.startswith('javascript:'):
                if any(kw in texte for kw in self.MOTS_CLES_OFFRES):
                    return urljoin(self.base_url, href)
        
        # Stratégie 2 : Premier lien valide
        for link in liens:
            href = link.get('href', '').strip()
            if href and not href.startswith('#') and not href.startswith('javascript:'):
                if not any(href.lower().endswith(ext) for ext in self.EXTENSIONS_DOCUMENTS):
                    return urljoin(self.base_url, href)
        
        return None
    
    def _extraire_organisme(self, conteneur) -> str | None:
        """Extrait le nom de l'organisme."""
        selecteurs_org = [
            '.company', '.organization', '.buyer', '.author',
            '.client', '.publisher', '.entity', '.institution'
        ]
        
        for sel in selecteurs_org:
            elem = conteneur.select_one(sel)
            if elem and len(elem.get_text(strip=True)) > 3:
                return elem.get_text(strip=True)
        
        return None
    
    def _extraire_date(self, conteneur) -> date:
        """Extrait la date de clôture."""
        selecteurs_date = [
            '.date', '.deadline', '.closing', '.cloture', '.end-date',
            'time', '.date-cloture', '.limit-date'
        ]
        
        for sel in selecteurs_date:
            elem = conteneur.select_one(sel)
            if elem:
                if elem.get('datetime'):
                    return parse_french_date(elem.get('datetime'))
                return parse_french_date(elem.get_text(strip=True))
        
        # Fallback : recherche dans le texte
        return parse_french_date(conteneur.get_text())
    
    def _extraire_description(self, conteneur) -> str:
        """Extrait la description."""
        paragraphes = conteneur.find_all('p')
        if paragraphes:
            texte = ' '.join(p.get_text(strip=True) for p in paragraphes[:3])
            if len(texte) > 50:
                return clean_text(texte)[:500]
        
        return clean_text(conteneur.get_text())[:500]
    
    def _extraire_montant(self, texte: str) -> str | None:
        """Extrait le montant si présent."""
        patterns = [
            r'(?:montant|budget|subvention|financement)\s*:\s*([^\n\.]+)',
            r'(\d+[\s\d.,]*\s*(?:FCFA|EUR|USD|XOF|€|\$))',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texte, re.IGNORECASE)
            if match:
                return clean_text(match.group(1))
        
        return None
    
    def _trouver_pdf_dans_page(self, soup: BeautifulSoup, base_url: str) -> str | None:
        """🎯 DÉTECTION AUTOMATIQUE DES PDF/TDR"""
        # Stratégie 1 : Liens directs vers PDF
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').strip()
            
            if href.lower().endswith('.pdf'):
                full_url = urljoin(base_url, href)
                if not self._est_pdf_generique(href):
                    return full_url
        
        # Stratégie 2 : Liens avec mots-clés
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').strip()
            texte = link.get_text(strip=True).lower()
            
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue
            
            texte_match = any(mot in texte for mot in self.MOTS_CLES_DOCUMENTS)
            url_match = any(mot in href.lower() for mot in self.MOTS_CLES_DOCUMENTS)
            ext_match = any(href.lower().endswith(ext) for ext in self.EXTENSIONS_DOCUMENTS)
            
            if texte_match or url_match or ext_match:
                if not self._est_lien_generique(href):
                    return urljoin(base_url, href)
        
        # Stratégie 3 : Boutons de téléchargement
        selecteurs_boutons = [
            'a.download', 'a.btn-download', '.download-link',
            'a[href*="download"]', 'a[href*="telecharger"]',
            '.attachment a', '.document-link'
        ]
        
        for selecteur in selecteurs_boutons:
            elem = soup.select_one(selecteur)
            if elem:
                href = elem.get('href')
                if href:
                    return urljoin(base_url, href)
        
        return None
    
    def _est_pdf_generique(self, url: str) -> bool:
        """Vérifie si le PDF est générique."""
        url_lower = url.lower()
        mots_generiques = ['logo', 'favicon', 'icon', 'banner', 'header', 'footer']
        return any(mot in url_lower for mot in mots_generiques)
    
    def _est_lien_generique(self, url: str) -> bool:
        """Vérifie si le lien est générique."""
        url_lower = url.lower()
        mots_generiques = [
            'accueil', 'home', 'contact', 'about', 'login', 'register',
            'signup', 'privacy', 'terms', 'faq', 'help', 'search'
        ]
        return any(mot in url_lower for mot in mots_generiques)
    
    def run(self) -> list[dict]:
        """Exécute le scraping avec détection automatique des PDF."""
        logger.info(f"🕷️ SmartParser scraping: {self.source_url}")
        
        try:
            # 1. Récupérer la page principale
            soup = self.fetch_and_parse(use_js=False)
            if not soup:
                return []
            
            # 2. Extraire les offres
            offres = self.parse(soup)
            
            # 3. Pour chaque offre, chercher le PDF/TDR
            for offre in offres:
                if offre.get('url_source'):
                    try:
                        import time
                        time.sleep(0.5)
                        
                        # Récupérer la page de détail
                        detail_soup = self.fetch_page(offre['url_source'], use_js=False)
                        
                        if detail_soup:
                            # 🎯 DÉTECTION AUTOMATIQUE DU PDF
                            pdf_url = self._trouver_pdf_dans_page(detail_soup, offre['url_source'])
                            if pdf_url:
                                offre['url_tdr'] = pdf_url
                                logger.info(f" PDF trouvé: {offre['titre'][:50]}")
                    except Exception as e:
                        logger.debug(f" Erreur inspection détail: {e}")
            
            return offres
            
        except Exception as e:
            logger.error(f"❌ Erreur SmartParser: {e}")
            return []