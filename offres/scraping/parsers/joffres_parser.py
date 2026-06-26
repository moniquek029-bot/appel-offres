# offres/scraping/parsers/joffres_parser.py
from bs4 import BeautifulSoup
from datetime import date, timedelta
import logging
import re

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url

logger = logging.getLogger(__name__)


def detecter_pays(texte: str, pays_defaut: str = 'BF') -> str:
    """Détecte le pays à partir du texte"""
    pays_mapping = {
        'burkina': 'BF', 'burkina faso': 'BF', 'ouagadougou': 'BF',
        'sénégal': 'SN', 'senegal': 'SN', 'dakar': 'SN',
        'côte d\'ivoire': 'CI', 'cote d\'ivoire': 'CI', 'abidjan': 'CI',
        'mali': 'ML', 'bamako': 'ML',
        'niger': 'NE', 'niamey': 'NE',
        'togo': 'TG', 'lomé': 'TG', 'lome': 'TG',
        'bénin': 'BJ', 'benin': 'BJ', 'cotonou': 'BJ',
        'guinée': 'GN', 'guinea': 'GN', 'conakry': 'GN',
        'cameroun': 'CM', 'cameroon': 'CM', 'yaoundé': 'CM', 'yaounde': 'CM',
        'gabon': 'GA', 'libreville': 'GA',
        'nigeria': 'NG', 'abuja': 'NG', 'lagos': 'NG',
        'ghana': 'GH', 'accra': 'GH',
        'tchad': 'TD', 'chad': 'TD', 'ndjamena': 'TD',
        'rdc': 'CD', 'congo': 'CD', 'kinshasa': 'CD',
        'rwanda': 'RW', 'kigali': 'RW',
        'afrique': 'REGIONAL', 'africa': 'REGIONAL',
        'uemoa': 'REGIONAL', 'cedao': 'REGIONAL', 'ecowas': 'REGIONAL',
    }
    
    texte_lower = texte.lower()
    for mot_cle, code_pays in pays_mapping.items():
        if mot_cle in texte_lower:
            return code_pays
    
    return pays_defaut


class JoffresParser(BaseScraper):
    """Parser JOFFRES optimisé avec JavaScript activé"""
    
    def __init__(self, source_url: str, base_url: str = "https://www.joffres.net", pays_defaut: str = 'BF', **kwargs):
        super().__init__(source_url, delay_seconds=2, base_url=base_url, pays_defaut=pays_defaut, **kwargs)
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        """Parse les offres depuis la page JOFFRES"""
        offres = []
        
        # Mots-clés pour identifier les offres
        keywords = [
            'appel', 'offre', 'marché', 'marche', 'tender', 'avis',
            'consultation', 'recrutement', 'contrat', 'projet',
            'bid', 'procurement', 'contract'
        ]
        
        # Stratégie 1 : Chercher dans les liens
        for link in soup.find_all('a', href=True):
            try:
                titre = clean_text(link.get_text(strip=True))
                href = link['href']
                
                # Filtres de base
                if len(titre) < 15:  # Réduit de 20 à 15
                    continue
                if href in ['#', '/', 'javascript:void(0)']:
                    continue
                if not any(kw in titre.lower() for kw in keywords):
                    continue
                
                # Construire l'URL complète
                url_source = normalize_url(href, self.base_url)
                
                # Éviter les doublons
                if any(o['url_source'] == url_source for o in offres):
                    continue
                
                # Détecter le pays
                pays = detecter_pays(titre, self.pays_defaut)
                
                # Extraire les dates si possible
                date_pub, date_clot = self._extraire_dates(titre)
                
                offre = {
                    'titre': titre[:300],
                    'organisme': "JOFFRES",
                    'description': titre[:2000],
                    'date_publication': date_pub,
                    'date_cloture': date_clot,
                    'url_source': url_source,
                    'url_tdr': url_source,  # Utiliser url_source comme fallback
                    'pays': pays,
                    'statut': 'Ouvert',
                    'mode_acquisition': 'AUTO',
                }
                
                offres.append(offre)
                
            except Exception as e:
                logger.debug(f"⚠️ Erreur parsing lien: {e}")
                continue
        
        # Stratégie 2 : Chercher dans les éléments structurés
        for article in soup.find_all(['article', 'div', 'li'], class_=re.compile(r'offer|tender|job|annonce|avis', re.I)):
            try:
                titre_elem = article.find(['h1', 'h2', 'h3', 'h4', 'a'])
                if not titre_elem:
                    continue
                
                titre = clean_text(titre_elem.get_text(strip=True))
                if len(titre) < 15:
                    continue
                
                # Chercher le lien
                link = article.find('a', href=True)
                if not link:
                    continue
                
                href = link['href']
                url_source = normalize_url(href, self.base_url)
                
                # Éviter les doublons
                if any(o['url_source'] == url_source for o in offres):
                    continue
                
                pays = detecter_pays(titre, self.pays_defaut)
                date_pub, date_clot = self._extraire_dates(article.get_text())
                
                offre = {
                    'titre': titre[:300],
                    'organisme': "JOFFRES",
                    'description': clean_text(article.get_text())[:2000],
                    'date_publication': date_pub,
                    'date_cloture': date_clot,
                    'url_source': url_source,
                    'url_tdr': url_source,
                    'pays': pays,
                    'statut': 'Ouvert',
                    'mode_acquisition': 'AUTO',
                }
                
                offres.append(offre)
                
            except Exception as e:
                logger.debug(f"⚠️ Erreur parsing article: {e}")
                continue
        
        logger.info(f"✅ JOFFRES: {len(offres)} offre(s) extraite(s)")
        return offres[:50]  # Augmenté de 30 à 50
    
    def _extraire_dates(self, texte: str) -> tuple:
        """Extrait les dates de publication et de clôture du texte"""
        date_pub = date.today() - timedelta(days=1)
        date_clot = date.today() + timedelta(days=30)
        
        # Chercher des patterns de dates
        # Pattern: "Date limite: 15/06/2026" ou "Clôture le 15 juin 2026"
        patterns = [
            r'(?:date\s*limite|clôture|deadline|limit).*?(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
            r'(?:jusqu\'au|until|before).*?(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texte, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                try:
                    # Essayer différents formats
                    for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%d/%m/%y']:
                        try:
                            date_clot = date.strptime(date_str, fmt)
                            break
                        except ValueError:
                            continue
                except Exception:
                    pass
        
        return date_pub, date_clot
    
    def run(self) -> list[dict]:
        """Exécute le scraping JOFFRES avec JavaScript activé"""
        logger.info(f" JOFFRES scraping: {self.source_url}")
        
        try:
            #  ACTIVATION DE JAVASCRIPT
            soup = self.fetch_and_parse(use_js=True)
            
            if not soup:
                logger.warning("⚠️ Aucune page récupérée pour JOFFRES")
                return []
            
            offres = self.parse(soup)
            
            if not offres:
                logger.warning("⚠️ Aucune offre trouvée sur JOFFRES")
                return []
            
            logger.info(f"✅ JOFFRES terminé: {len(offres)} offres")
            return offres
            
        except Exception as e:
            logger.error(f"❌ Erreur JOFFRES: {e}", exc_info=True)
            return []