import re
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text
from offres.scraping.extraction_helpers import extract_publication_date_from_text, extract_deadline_from_text

logger = logging.getLogger(__name__)

class AfDBParser(BaseScraper):
    def __init__(self, source_url: str, **kwargs):
        super().__init__(source_url, **kwargs)
        self.base_domain = "https://www.afdb.org"

    def parse(self, soup: BeautifulSoup) -> list:
        offres = []
        if not soup:
            return offres

        liens_cibles = soup.find_all('a', href=re.compile(r'/fr/documents/', re.I))
        
        for lien in liens_cibles[:20]:
            titre_brut = lien.get_text(strip=True)
            if len(titre_brut) < 20 or not any(mot in titre_brut.lower() for mot in ['appel', 'avis', 'consultation', 'procurement']):
                continue

            href = lien['href']
            url_source = href if href.startswith('http') else urljoin(self.base_domain, href)

            if any(o['url_source'] == url_source for o in offres):
                continue

            detail_soup = self.fetch_page(url_source)
            if not detail_soup:
                continue

            texte_complet = detail_soup.get_text(separator=' ', strip=True)
            date_pub = extract_publication_date_from_text(texte_complet)
            date_cloture = extract_deadline_from_text(texte_complet)

            pays = 'Multiple'
            if 'burkina' in texte_complet.lower(): pays = 'BF'
            elif 'sénégal' in texte_complet.lower(): pays = 'SN'
            elif 'ivoire' in texte_complet.lower(): pays = 'CI'
            elif 'mali' in texte_complet.lower(): pays = 'ML'

            pdf_url = None
            for link in detail_soup.find_all('a', href=True):
                if '.pdf' in link['href'].lower() or 'télécharger' in link.get_text().lower():
                    pdf_url = link['href'] if link['href'].startswith('http') else urljoin(url_source, link['href'])
                    break

            offres.append({
                'titre': clean_text(titre_brut)[:300],
                'organisme': 'Banque Africaine de Développement (BAD)',
                'description': clean_text(texte_complet[:1000]),
                'date_publication': date_pub,
                'date_cloture': date_cloture,
                'url_source': url_source,
                'url_tdr': pdf_url or url_source,
                'pays': pays,
                'domaine': 'Finance, Audit & Conseil',
                'statut': 'Ouvert',
                'type_offre': 'APPEL_D_OFFRES',
                'mode_acquisition': 'AUTO'
            })
        return offres

    def run(self) -> list:
        logger.info(f"🕷️ AfDBParser: {self.source_url}")
        try:
            # La BAD bloque parfois les requêtes simples, on force JS
            soup = self.fetch_and_parse(use_js=True) 
            if not soup:
                return []
            return self.parse(soup)
        except Exception as e:
            logger.error(f"❌ Erreur AfDBParser: {e}")
            return []