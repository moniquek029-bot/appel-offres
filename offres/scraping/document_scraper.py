# offres/scraping/document_scraper.py
"""
Scraper de documents (PDF, TDR, etc.) pour les appels d'offres
Version adaptée pour Django
"""

import requests
import re
import time
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse
import logging
from django.conf import settings
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# ==================== CONFIGURATION ====================
class DocumentScraperConfig:
    """Configuration pour le scraper de documents"""
    
    TIMEOUT = 30
    DELAI = 2
    MAX_DOCS_PER_OFFRE = 10
    
    # Extensions de documents acceptées
    EXTENSIONS_DOCS = [
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
        '.zip', '.rar', '.odt', '.txt', '.rtf'
    ]
    
    # Mots-clés pour identifier les documents
    MOTS_CLES_DOCS = [
        'tdr', 'document', 'dossier', 'cahier des charges',
        'appel d\'offres', 'appel d\'offre', 'dao', 'dce',
        'telecharger', 'télécharger', 'download', 'pdf',
        'specification', 'terms of reference', 'rfq', 'rfp',
        'bidding document', 'procurement'
    ]
    
    # Mots-clés à exclure (faux positifs)
    MOTS_EXCLUSION = [
        'logo', 'header', 'footer', 'banner', 'icon',
        'facebook', 'twitter', 'linkedin', 'youtube'
    ]


class DocumentScraper:
    """Scraper de documents pour les appels d'offres"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr,fr-FR;q=0.8,en;q=0.5',
        })
        self.session.verify = False
        self.docs_dir = Path(settings.MEDIA_ROOT) / 'tdr_scraped'
        self.docs_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_documents_from_page(self, page_url, max_docs=10):
        """
        Extrait tous les documents d'une page d'offre
        
        Args:
            page_url: URL de la page d'offre
            max_docs: Nombre maximum de documents à extraire
            
        Returns:
            List de dict avec les documents trouvés
        """
        documents = []
        
        if not page_url:
            return documents
        
        try:
            logger.info(f"📄 Extraction documents depuis: {page_url[:60]}...")
            
            response = self.session.get(page_url, timeout=DocumentScraperConfig.TIMEOUT)
            if response.status_code != 200:
                logger.warning(f"⚠️ Erreur {response.status_code} pour {page_url}")
                return documents
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 1. Rechercher les liens directs vers des documents
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                text = link.get_text(strip=True).lower()
                classe = ' '.join(link.get('class', [])).lower()
                
                # Vérifier les extensions de fichiers
                is_doc = False
                doc_type = None
                
                # Vérifier les extensions
                for ext in DocumentScraperConfig.EXTENSIONS_DOCS:
                    if href.lower().endswith(ext):
                        is_doc = True
                        doc_type = ext[1:].upper()
                        break
                
                # Vérifier les mots-clés
                if not is_doc:
                    for mot in DocumentScraperConfig.MOTS_CLES_DOCS:
                        if mot in text or mot in href.lower():
                            is_doc = True
                            break
                
                # Vérifier les exclusions
                if is_doc:
                    for excl in DocumentScraperConfig.MOTS_EXCLUSION:
                        if excl in text or excl in href.lower():
                            is_doc = False
                            break
                
                if is_doc and href and not href.startswith('#'):
                    # Construire l'URL complète
                    doc_url = urljoin(page_url, href)
                    
                    # Générer un nom de fichier
                    doc_name = link.get_text(strip=True) or doc_url.split('/')[-1]
                    if not doc_name:
                        doc_name = f"document_{len(documents)+1}"
                    
                    # Nettoyer le nom
                    doc_name = re.sub(r'[^\w\s\-_.]', '_', doc_name)[:80]
                    
                    # Ajouter l'extension si manquante
                    if not re.search(r'\.\w+$', doc_name) and doc_type:
                        doc_name = f"{doc_name}.{doc_type.lower()}"
                    
                    # Télécharger le document
                    local_path = self._download_document(doc_url, doc_name)
                    
                    if local_path:
                        documents.append({
                            'nom': doc_name,
                            'url': doc_url,
                            'chemin_local': local_path,
                            'type': doc_type or 'unknown'
                        })
                        
                        if len(documents) >= max_docs:
                            break
            
            # 2. Si pas de documents trouvés, chercher dans les iframes
            if not documents:
                for iframe in soup.find_all('iframe'):
                    src = iframe.get('src', '')
                    if src and '.pdf' in src.lower():
                        doc_url = urljoin(page_url, src)
                        doc_name = src.split('/')[-1] or f"document_{len(documents)+1}.pdf"
                        local_path = self._download_document(doc_url, doc_name)
                        if local_path:
                            documents.append({
                                'nom': doc_name,
                                'url': doc_url,
                                'chemin_local': local_path,
                                'type': 'PDF'
                            })
            
            # 3. Chercher dans les objets/embeds
            if not documents:
                for obj in soup.find_all(['object', 'embed']):
                    data = obj.get('data') or obj.get('src')
                    if data and '.pdf' in data.lower():
                        doc_url = urljoin(page_url, data)
                        doc_name = data.split('/')[-1] or f"document_{len(documents)+1}.pdf"
                        local_path = self._download_document(doc_url, doc_name)
                        if local_path:
                            documents.append({
                                'nom': doc_name,
                                'url': doc_url,
                                'chemin_local': local_path,
                                'type': 'PDF'
                            })
            
            if documents:
                logger.info(f"✅ {len(documents)} document(s) trouvé(s)")
            
            return documents
            
        except Exception as e:
            logger.error(f"❌ Erreur extraction documents: {e}")
            return documents
    
    def _download_document(self, url, filename):
        """
        Télécharge un document
        
        Args:
            url: URL du document
            filename: Nom du fichier
            
        Returns:
            Chemin local du fichier téléchargé
        """
        try:
            # Nettoyer le nom de fichier
            filename = re.sub(r'[^\w\-_.]', '_', filename)
            
            # Créer le chemin complet
            filepath = self.docs_dir / filename
            
            # Éviter les doublons
            if filepath.exists():
                return str(filepath)
            
            logger.info(f"⬇️ Téléchargement: {filename[:50]}...")
            
            response = self.session.get(url, timeout=DocumentScraperConfig.TIMEOUT, stream=True)
            response.raise_for_status()
            
            # Vérifier le type de contenu
            content_type = response.headers.get('content-type', '')
            if 'text/html' in content_type and not url.lower().endswith('.pdf'):
                logger.warning(f"⚠️ Contenu HTML au lieu d'un document")
                return None
            
            # Télécharger
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"✅ Téléchargé: {filename}")
            return str(filepath)
            
        except Exception as e:
            logger.warning(f"❌ Erreur téléchargement {filename}: {str(e)[:50]}")
            return None
    
    def get_documents_for_offre(self, offre):
        """
        Récupère les documents pour une offre donnée
        
        Args:
            offre: Instance de AppelOffre
            
        Returns:
            List de documents téléchargés
        """
        documents = []
        
        # Utiliser l'URL source ou l'URL TDR
        urls_to_check = []
        if offre.url_source:
            urls_to_check.append(offre.url_source)
        if offre.url_tdr and offre.url_tdr != offre.url_source:
            urls_to_check.append(offre.url_tdr)
        
        for url in urls_to_check[:2]:  # Limiter à 2 URLs
            docs = self.extract_documents_from_page(
                url, 
                max_docs=DocumentScraperConfig.MAX_DOCS_PER_OFFRE
            )
            documents.extend(docs)
            
            # Arrêter si on a trouvé des documents
            if documents:
                break
        
        return documents