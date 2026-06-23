# offres/scraping/parsers/unfpa_parser.py
from offres.scraping.base import BaseScraper
import logging
from urllib.parse import urljoin
import re

logger = logging.getLogger(__name__)

class UNFPAParser(BaseScraper):
    """Parser pour UNFPA Burkina Faso"""
    
    def __init__(self, source_url, **kwargs):
        super().__init__(source_url, **kwargs)
        self.offers = []
    
    def run(self):
        """Exécute le scraping UNFPA"""
        logger.info(f"🌍 Scraping UNFPA: {self.source_url}")
        
        soup = self.fetch_and_parse()
        if not soup:
            return []
        
        # Mots-clés pour identifier les appels d'offres
        keywords = ['recrutement', 'cotation', 'appel', 'achat', 'demande', 'consultant']
        
        for link in soup.find_all('a', href=True):
            titre = link.get_text(strip=True)
            
            # Filtrer les liens pertinents
            if titre and len(titre) > 25 and any(mot in titre.lower() for mot in keywords):
                offre_url = urljoin(self.source_url, link['href'])
                
                # Visiter la page de détail pour extraire les documents
                documents = self._extract_documents(offre_url)
                pays = detecter_pays(titre, self.pays_defaut)

                offer = {
                    'titre': titre[:300],
                    'url_source': offre_url,
                    'organisme': 'UNFPA Burkina Faso',
                    'pays': 'pays',
                    'description': titre,
                    'url_tdr': documents[0]['url'] if documents else None,
                }
                
                self.offers.append(offer)
                logger.info(f"  ✅ Offre trouvée: {titre[:60]}...")
        
        logger.info(f"✅ UNFPA: {len(self.offers)} offres extraites")
        return self.offers
    
    def _extract_documents(self, page_url):
        """Extrait les documents PDF/ZIP depuis une page d'offre"""
        documents = []
        
        try:
            soup = self.fetch_page(page_url)
            if not soup:
                return documents
            
            for link in soup.find_all('a', href=True):
                href = link['href'].lower()
                text = link.get_text(strip=True).lower()
                
                # Détecter les documents
                is_doc = any(ext in href for ext in ['.pdf', '.doc', '.zip', '.docx'])
                is_doc = is_doc or any(word in text for word in ['telecharger', 'tdr', 'dossier', 'dao'])
                
                if is_doc:
                    doc_url = urljoin(page_url, link['href'])
                    documents.append({
                        'nom': link.get_text(strip=True) or doc_url.split('/')[-1],
                        'url': doc_url
                    })
            
            return documents
        except Exception as e:
            logger.error(f"Erreur extraction documents: {e}")
            return documents