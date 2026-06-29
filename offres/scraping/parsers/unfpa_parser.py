# offres/scraping/parsers/unfpa_parser.py
from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url, parse_french_date
from offres.scraping.country_detector import detecter_pays_smart
from offres.scraping.site_validator import is_valid_offer_title, is_rejected_content
import logging
from urllib.parse import urljoin
from datetime import date

logger = logging.getLogger(__name__)


class UNFPAParser(BaseScraper):
    """Parser pour UNFPA Burkina Faso"""
    
    # Mots-clés pour identifier les appels d'offres UNFPA
    MOTS_CLES_OFFRES = [
        'recrutement', 'cotation', 'appel', 'achat', 'demande',
        'consultant', 'manifestation', 'intérêt', 'interet',
        'avis', 'tender', 'bureau d\'études', 'bureau d\'etudes',
        'fourniture', 'acquisition', 'consultation',
    ]
    
    def __init__(self, source_url, **kwargs):
        super().__init__(source_url, **kwargs)
        self.offers = []
    
    def run(self) -> list[dict]:
        """Exécute le scraping UNFPA avec validation"""
        logger.info(f"🌍 Scraping UNFPA: {self.source_url}")
        
        try:
            soup = self.fetch_and_parse()
            if not soup:
                logger.error("❌ Page non récupérée")
                return []
            
            # ✅ DEBUG : Titre de la page
            title = soup.title.string if soup.title else 'Sans titre'
            logger.info(f"📄 Titre: {title}")
            
            # ✅ DEBUG : Compter les liens
            links = soup.find_all('a', href=True)
            logger.info(f"🔗 Nombre de liens: {len(links)}")
            
            # Extraire les offres
            self.offers = []
            
            for link in links:
                titre = link.get_text(strip=True)
                
                # Filtrer les liens pertinents
                if not titre or len(titre) < 25:
                    continue
                
                if not any(mot in titre.lower() for mot in self.MOTS_CLES_OFFRES):
                    continue
                
                offre_url = urljoin(self.source_url, link['href'])
                
                # ✅ VALIDATION : Vérifier que c'est bien un appel d'offres
                if not is_valid_offer_title(titre):
                    logger.debug(f"⏭️ Offre rejetée (titre non-valide): {titre[:50]}...")
                    continue
                
                # Visiter la page de détail pour extraire les documents
                documents = self._extract_documents(offre_url)
                
                # ✅ DÉTECTION INTELLIGENTE DU PAYS
                # Récupérer le texte de la page de détail pour une meilleure détection
                texte_complet = titre
                if documents:
                    # Ajouter les noms des documents au texte pour la détection
                    texte_complet += ' ' + ' '.join(d.get('nom', '') for d in documents)
                
                pays = detecter_pays_smart(
                    texte_complet,
                    url=offre_url,
                    pays_defaut=self.pays_defaut
                )
                
                offer = {
                    'titre': clean_text(titre)[:300],
                    'url_source': offre_url,
                    'organisme': 'UNFPA Burkina Faso',
                    'pays': pays,  # ✅ CORRIGÉ : variable au lieu de chaîne
                    'description': clean_text(titre)[:1000],
                    'date_publication': date.today(),
                    'date_cloture': parse_french_date(titre),  # Tente d'extraire une date du titre
                    'url_tdr': documents[0]['url'] if documents else None,
                    'statut': 'Ouvert',
                    'mode_acquisition': 'AUTO',
                }
                
                self.offers.append(offer)
                logger.info(f"  ✅ Offre trouvée: {titre[:60]}...")
                logger.info(f"     🌍 Pays: {pays}")
                if documents:
                    logger.info(f"     📄 Documents: {len(documents)}")
            
            logger.info(f"✅ UNFPA: {len(self.offers)} offres extraites")
            return self.offers
            
        except Exception as e:
            logger.error(f"❌ Erreur UNFPA: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
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
                is_doc = is_doc or any(word in text for word in [
                    'telecharger', 'télécharger', 'tdr', 'dossier', 'dao',
                    'terms of reference', 'termes de référence'
                ])
                
                # Exclure les faux positifs
                if is_doc and not any(excl in href for excl in ['logo', 'favicon', 'icon', 'home']):
                    doc_url = urljoin(page_url, link['href'])
                    documents.append({
                        'nom': link.get_text(strip=True) or doc_url.split('/')[-1],
                        'url': doc_url
                    })
            
            return documents
        except Exception as e:
            logger.error(f"⚠️ Erreur extraction documents: {e}")
            return documents