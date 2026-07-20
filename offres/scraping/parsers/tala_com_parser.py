import re
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from django.utils import timezone
from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text
from offres.scraping.extraction_helpers import extract_publication_date_from_text, extract_deadline_from_text

logger = logging.getLogger(__name__)

class TalaComParser(BaseScraper):
    def __init__(self, source_url: str, **kwargs):
        super().__init__(source_url, **kwargs)
        self.base_domain = "https://www.tala-com.com"

    def parse(self, soup: BeautifulSoup) -> list:
        offres = []
        if not soup:
            return offres

        headings = soup.find_all(['h2', 'h3', 'h4'])
        
        for heading in headings:
            link = heading.find('a', href=True)
            if not link:
                link = heading.find_parent('a', href=True)
            
            if not link:
                continue
                
            href = link.get('href', '')
            
            if '/appels-offres/' not in href:
                continue
                
            url_source = href if href.startswith('http') else f"https://www.tala-com.com{href}"
            
            if any(o['url_source'] == url_source for o in offres):
                continue
            
            detail_soup = self.fetch_page(url_source)
            if not detail_soup:
                continue
            
            # 1. Extraire le titre
            h1_tag = detail_soup.find('h1')
            titre = h1_tag.get_text(strip=True) if h1_tag else heading.get_text(strip=True)
            titre = re.sub(r'\s*-\s*Tala Com\s*$', '', titre, flags=re.IGNORECASE).strip()
            
            if len(titre) < 10:
                continue

            # 2. Extraire le VRAI contenu de l'article (ignorer le menu)
            # On cherche les classes CSS standards des articles WordPress
            content_div = detail_soup.find('div', class_=re.compile(r'entry-content|post-content|article-body|td-post-content', re.I))
            
            if content_div:
                description_brute = content_div.get_text(separator=' ', strip=True)
            else:
                # Fallback : on prend tout le texte, mais on essaie de couper après le premier paragraphe utile
                description_brute = detail_soup.get_text(separator=' ', strip=True)

            # 3. FILTRE DE QUALITÉ : Si la description est juste le menu du site, on rejette
            if "A propos FAQ Espace client" in description_brute or "Chargement" in description_brute[:50]:
                logger.warning(f"⏭️ REJETÉ (Qualité faible / Menu uniquement) : {titre[:40]}")
                continue

            description = clean_text(description_brute)[:1000]
            
            # 4. Extraction des dates
            date_pub = extract_publication_date_from_text(description_brute)
            date_cloture = extract_deadline_from_text(description_brute)
            
            if not date_pub:
                date_pub = timezone.now().date()

            # 5. FILTRE CRUCIAL : REJETER LES OFFRES EXPIRÉES
            today = timezone.now().date()
            if date_cloture and date_cloture < today:
                logger.warning(f"⏭️ REJETÉ (Offre expirée le {date_cloture}) : {titre[:40]}")
                continue
            
            # Si pas de date de clôture trouvée, on ne prend pas le risque
            if not date_cloture:
                logger.warning(f"⏭️ REJETÉ (Pas de date de clôture trouvée) : {titre[:40]}")
                continue

            # Enrichissement du titre pour la validation globale
            mots_cles = ['appel', 'avis', 'consultation', 'recrutement', 'manifestation', 'offre', 'marché', 'tender']
            if not any(mot in titre.lower() for mot in mots_cles):
                titre = f"Appel d'offres / Consultation : {titre}"

            # 6. Chercher le PDF
            pdf_url = None
            for d_link in detail_soup.find_all('a', href=True):
                d_href = d_link.get('href', '').lower()
                d_text = d_link.get_text().lower()
                if d_href.endswith('.pdf') or 'pdf' in d_text or 'télécharger' in d_text:
                    pdf_url = d_link['href'] if d_link['href'].startswith('http') else urljoin(url_source, d_link['href'])
                    break

            offres.append({
                'titre': titre[:300],
                'organisme': 'Tala Com',
                'description': description,
                'date_publication': date_pub,
                'date_cloture': date_cloture,
                'url_source': url_source,
                'url_tdr': pdf_url or url_source,
                'pays': 'CD',
                'domaine': 'Autres',
                'statut': 'Ouvert',
                'type_offre': 'APPEL_D_OFFRES',
                'mode_acquisition': 'AUTO'
            })
            
            if len(offres) >= 10:
                break
                
        logger.info(f"🎯 TalaComParser: {len(offres)} offres VALIDES extraites.")
        return offres

    def run(self) -> list:
        logger.info(f"🕷️ TalaComParser: {self.source_url}")
        try:
            soup = self.fetch_and_parse(use_js=False)
            if not soup:
                return []
            return self.parse(soup)
        except Exception as e:
            logger.error(f"❌ Erreur TalaComParser: {e}")
            return []