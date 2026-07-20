import re
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text
from offres.scraping.extraction_helpers import extract_publication_date_from_text, extract_deadline_from_text

logger = logging.getLogger(__name__)

class UNGMParser(BaseScraper):
    def __init__(self, source_url: str, **kwargs):
        super().__init__(source_url, **kwargs)
        self.base_domain = "https://www.ungm.org"

    def parse(self, soup: BeautifulSoup) -> list:
        print("🚨 DEBUG UNGM: Début de la fonction parse")
        offres = []
        if not soup:
            print("🚨 DEBUG UNGM: L'objet soup est vide ou None")
            return offres

        all_links = soup.find_all('a', href=True)
        msg = f"🚨 DEBUG UNGM: La page contient {len(all_links)} liens au total."
        print(msg)
        logger.warning(msg)
        
        for link in all_links:
            href = link.get('href', '')
            texte = link.get_text(strip=True)
            
            # On affiche tout lien qui contient "notice" ou "opportunity" dans l'URL
            if 'notice' in href.lower() or 'opportunity' in href.lower():
                cand_msg = f"🚨 DEBUG UNGM CANDIDAT: '{texte[:60]}...' -> {href}"
                print(cand_msg)
                logger.warning(cand_msg)
                
                if len(texte) < 20:
                    continue
                    
                url_source = href if href.startswith('http') else f"https://www.ungm.org{href}"
                
                if any(o['url_source'] == url_source for o in offres):
                    continue

                detail_soup = self.fetch_page(url_source)
                if not detail_soup:
                    continue

                texte_complet = detail_soup.get_text(separator=' ', strip=True)
                date_pub = extract_publication_date_from_text(texte_complet)
                date_cloture = extract_deadline_from_text(texte_complet)

                pays = 'International'
                if 'burkina faso' in texte_complet.lower(): pays = 'BF'
                elif 'senegal' in texte_complet.lower(): pays = 'SN'
                elif 'mali' in texte_complet.lower(): pays = 'ML'
                elif "côte d'ivoire" in texte_complet.lower(): pays = 'CI'

                pdf_url = url_source
                for d_link in detail_soup.find_all('a', href=True):
                    if '.pdf' in d_link['href'].lower() or 'document' in d_link.get_text().lower():
                        pdf_url = d_link['href'] if d_link['href'].startswith('http') else urljoin(url_source, d_link['href'])
                        break

                offres.append({
                    'titre': clean_text(texte)[:300],
                    'organisme': 'Nations Unies (UNGM)',
                    'description': clean_text(texte_complet[:1000]),
                    'date_publication': date_pub,
                    'date_cloture': date_cloture,
                    'url_source': url_source,
                    'url_tdr': pdf_url,
                    'pays': pays,
                    'domaine': 'Autres',
                    'statut': 'Ouvert',
                    'type_offre': 'APPEL_D_OFFRES',
                    'mode_acquisition': 'AUTO'
                })
                
                if len(offres) >= 10:
                    break
                    
        return offres

    def run(self) -> list:
        print("🚨 DEBUG UNGM: Début de la fonction run")
        logger.info(f"🕷️ UNGMParser: {self.source_url} (Mode JS requis)")
        try:
            soup = self.fetch_and_parse(use_js=True)
            if not soup:
                print("🚨 DEBUG UNGM: Échec du chargement JS, soup est None")
                logger.warning("⚠️ UNGM: Échec du chargement JS")
                return []
            return self.parse(soup)
        except Exception as e:
            print(f"🚨 DEBUG UNGM: Exception attrapée : {e}")
            logger.error(f"❌ Erreur UNGMParser: {e}")
            return []