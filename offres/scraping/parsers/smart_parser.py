"""
SmartParser - Parser universel qui fonctionne sur n'importe quel site
✅ NE CASSE RIEN - Ajoute simplement une nouvelle fonctionnalité
✅ Fonctionne pour tous les sites ajoutés via l'admin
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import date, timedelta
import logging

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url

logger = logging.getLogger(__name__)


class SmartParser(BaseScraper):
    """
    Parser intelligent qui s'adapte à n'importe quel site
    - Détecte automatiquement les offres
    - Extrait les PDF de manière générique
    - Fonctionne sans configuration préalable
    - Compatible avec tous les sites ajoutés via l'admin
    """
    
    def __init__(self, source_url: str, **kwargs):
        super().__init__(source_url, **kwargs)
        self.offres_trouvees = []
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        """Parse intelligemment n'importe quelle page"""
        offres = []
        
        # Mots-clés pour identifier une offre
        mots_cles_offre = [
            'appel', 'offre', 'tender', 'consultation', 'recrutement',
            'avis', 'demande', 'proposition', 'proposal', 'notice',
            'marché', 'marche', 'prestation', 'fourniture', 'travaux',
            'service', 'pre-qualification', 'prequalification'
        ]
        
        # 1. Chercher les conteneurs d'offres
        conteneurs = self._trouver_conteneurs(soup)
        
        for conteneur in conteneurs:
            try:
                # Extraire le titre
                titre = self._extraire_titre(conteneur)
                if not titre or len(titre) < 15:
                    continue
                
                # Extraire le lien
                url_source = self._extraire_lien(conteneur)
                if not url_source:
                    continue
                
                # Extraire l'organisme
                organisme = self._extraire_organisme(conteneur) or self.source_url.split('//')[1].split('/')[0]
                
                # Extraire la date de clôture
                date_cloture = self._extraire_date(conteneur)
                
                offre = {
                    'titre': clean_text(titre)[:300],
                    'organisme': clean_text(organisme)[:200],
                    'description': self._extraire_description(conteneur),
                    'date_publication': date.today() - timedelta(days=3),
                    'date_cloture': date_cloture or (date.today() + timedelta(days=30)),
                    'url_source': url_source,
                    'url_tdr': None,
                    'pays': self.pays_defaut,
                    'statut': 'Ouvert',
                    'mode_acquisition': 'AUTO',
                }
                
                offres.append(offre)
                
            except Exception as e:
                logger.debug(f"Erreur extraction offre: {e}")
                continue
        
        logger.info(f"✅ SmartParser: {len(offres)} offre(s) extraite(s) pour {self.source_url}")
        return offres[:30]  # Limiter à 30 offres par source
    
    def _trouver_conteneurs(self, soup: BeautifulSoup) -> list:
        """Trouve les conteneurs d'offres de manière générique"""
        conteneurs = []
        
        # Sélecteurs CSS courants
        selecteurs = [
            'div.offre', 'div.offer', 'div.tender', 'article', 
            'div.item', 'div.post', 'div.job', 'div.listing-item',
            'div.card', 'div.ao-item', 'div.appel-offre',
            'tr', 'li', '.views-row', '.node'
        ]
        
        for selecteur in selecteurs:
            trouves = soup.select(selecteur)
            if len(trouves) > 2:
                conteneurs = trouves
                logger.debug(f"Conteneurs trouvés avec: {selecteur} ({len(conteneurs)})")
                break
        
        if not conteneurs:
            for link in soup.find_all('a', href=True):
                if len(link.get_text(strip=True)) > 30:
                    parent = link.find_parent(['div', 'article', 'li', 'tr'])
                    if parent and parent not in conteneurs:
                        conteneurs.append(parent)
        
        return conteneurs
    
    def _extraire_titre(self, conteneur) -> str:
        """Extrait le titre de l'offre"""
        selecteurs_titre = ['h1', 'h2', 'h3', 'h4', 'h5', '.title', '.titre', '.name', '.offer-title']
        
        for sel in selecteurs_titre:
            elem = conteneur.select_one(sel)
            if elem:
                texte = elem.get_text(strip=True)
                if len(texte) > 10:
                    return texte
        
        for link in conteneur.find_all('a', href=True):
            texte = link.get_text(strip=True)
            if len(texte) > 15:
                return texte
        
        return conteneur.get_text(strip=True)[:200]
    
    def _extraire_lien(self, conteneur) -> str | None:
        """Extrait l'URL de l'offre"""
        for link in conteneur.find_all('a', href=True):
            href = link.get('href', '')
            if href and not href.startswith('#') and not href.startswith('javascript'):
                if href.startswith('/'):
                    return urljoin(self.base_url, href)
                if href.startswith('http'):
                    return href
        return None
    
    def _extraire_organisme(self, conteneur) -> str | None:
        """Extrait le nom de l'organisme"""
        selecteurs_org = ['.company', '.organization', '.buyer', '.author', '.client', '.publisher']
        
        for sel in selecteurs_org:
            elem = conteneur.select_one(sel)
            if elem:
                texte = elem.get_text(strip=True)
                if len(texte) > 3:
                    return texte
        
        for elem in conteneur.find_all(['span', 'div'], class_=True):
            texte = elem.get_text(strip=True)
            if len(texte) > 5 and len(texte) < 100:
                if any(mot in texte.lower() for mot in ['ministère', 'agence', 'société', 'entreprise', 'institut']):
                    return texte
        
        return None
    
    def _extraire_date(self, conteneur) -> date | None:
        """Extrait la date de clôture"""
        selecteurs_date = ['.date', '.deadline', '.closing', '.cloture', '.end-date', 'time']
        
        for sel in selecteurs_date:
            elem = conteneur.select_one(sel)
            if elem:
                texte = elem.get_text(strip=True)
                date_parsee = self._parser_date(texte)
                if date_parsee:
                    return date_parsee
        
        texte = conteneur.get_text()
        patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
            r'(\d{4}-\d{2}-\d{2})',
            r'clôture\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
            r'deadline\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texte, re.IGNORECASE)
            if match:
                return self._parser_date(match.group(1))
        
        return None
    
    def _parser_date(self, date_str: str) -> date | None:
        """Parse une date dans différents formats"""
        from datetime import datetime
        
        formats = [
            '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d',
            '%d/%m/%y', '%d-%m-%y',
            '%d %B %Y', '%d %b %Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue
        
        return None
    
    def _extraire_description(self, conteneur) -> str:
        """Extrait la description de l'offre"""
        paragraphes = conteneur.find_all('p')
        if paragraphes:
            return clean_text(' '.join(p.text for p in paragraphes[:3]))[:500]
        
        return clean_text(conteneur.get_text())[:500]
    
    def parse_detail_page(self, soup: BeautifulSoup, base_url: str) -> dict | None:
        """Extrait le PDF de la page détail - UNIVERSEL"""
        pdf_url = None
        
        # 1. Chercher les liens PDF directs
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.lower().endswith('.pdf'):
                pdf_url = normalize_url(href, base_url)
                if pdf_url:
                    return {'url_tdr': pdf_url}
        
        # 2. Chercher les liens contenant des mots-clés
        mots_cles = ['pdf', 'tdr', 'download', 'telecharger', 'document', 'cahier', 'fichier']
        for link in soup.find_all('a', href=True):
            text = link.get_text().lower()
            href = link['href']
            if any(kw in text for kw in mots_cles):
                if '.pdf' in href.lower():
                    pdf_url = normalize_url(href, base_url)
                    if pdf_url:
                        return {'url_tdr': pdf_url}
        
        # 3. Chercher dans les iframes
        for iframe in soup.find_all('iframe', src=True):
            src = iframe['src']
            if '.pdf' in src.lower():
                pdf_url = normalize_url(src, base_url)
                return {'url_tdr': pdf_url}
        
        return None
    
    def run(self) -> list[dict]:
        """Exécute le scraping intelligent"""
        logger.info(f"🕷️ SmartParser scraping: {self.source_url}")
        
        try:
            soup = self.fetch_and_parse()
            if not soup:
                return []
            
            offres = self.parse(soup)
            
            for offre in offres:
                if offre.get('url_source'):
                    try:
                        detail_soup = self.fetch_page(offre['url_source'])
                        if detail_soup:
                            pdf_data = self.parse_detail_page(detail_soup, self.base_url)
                            if pdf_data and pdf_data.get('url_tdr'):
                                offre['url_tdr'] = pdf_data['url_tdr']
                                logger.info(f"📎 PDF trouvé pour: {offre['titre'][:50]}...")
                    except Exception as e:
                        logger.debug(f"Erreur extraction PDF: {e}")
            
            return offres
            
        except Exception as e:
            logger.error(f"❌ Erreur SmartParser: {e}")
            return []