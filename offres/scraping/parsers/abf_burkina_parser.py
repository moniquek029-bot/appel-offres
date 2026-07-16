# offres/scraping/abf_burkina.py
import re
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import date, timedelta

from offres.scraping.base import BaseScraper 
from offres.scraping.utils import clean_text, parse_french_date
from offres.scraping.extraction_helpers import extract_pdf_url
from offres.utils.search_keywords import detecter_domaine, est_appel_offres

logger = logging.getLogger(__name__)

class ABFBurkinaScraper(BaseScraper):
    """Scraper ABF Burkina - Correction de l'extraction des titres et descriptions"""
    
    def __init__(self, source_url: str = "https://www.abfburkina.org/appels-a-projets/", **kwargs):
        base_url = "https://www.abfburkina.org"
        super().__init__(source_url, delay_seconds=2, base_url=base_url, **kwargs)
        self.pays_defaut = 'BF'

    def detecter_domaine(self, titre, description=""):
        return detecter_domaine(titre, description)

    def run(self) -> list[dict]:
        logger.info(f"🕷️ ABF Burkina scraping: {self.source_url}")
        try:
            soup = self.fetch_and_parse(use_js=False)
            if not soup:
                return []
            return self.parse(soup)
        except Exception as e:
            logger.error(f"❌ Erreur ABF Burkina: {e}")
            return []
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        offres = []
        # Cibler les articles de blog/offres de manière plus robuste
        articles = soup.find_all(['article', 'div'], class_=re.compile(r'post|entry|item|article|type-page|call-for-proposal', re.I))
        
        if not articles:
            # Fallback: chercher les conteneurs de titres
            titres = soup.find_all(['h2', 'h3', 'h4'])
            for titre in titres:
                parent = titre.find_parent(['article', 'div', 'section'])
                if parent and parent not in articles:
                    articles.append(parent)
        
        logger.info(f"🔍 ABF Burkina: {len(articles)} blocs potentiels trouvés")
        
        for i, article in enumerate(articles[:30], 1):
            try:
                offre_base = self._parser_article_base(article)
                if not offre_base:
                    continue
                
                # ✅ CORRECTION : Passer titre ET description à la validation
                titre_valid = offre_base.get('titre', '')
                desc_valid = offre_base.get('description', '')
                
                if not est_appel_offres(titre_valid, desc_valid):
                    logger.info(f"   ⏭️ REJETÉ (pas un appel d'offres): {titre_valid[:50]}...")
                    continue
                
                if offre_base['date_cloture'] and offre_base['date_cloture'] < date.today():
                    logger.info(f"  ⏭️ Offre expirée ignorée : {titre_valid[:40]}")
                    continue
                
                logger.info(f"  [{i}/{len(articles)}] Extraction détails: {titre_valid[:50]}...")
                
                url_tdr = offre_base.get('url_source')
                if url_tdr and url_tdr != self.source_url:
                    detail_soup = self.fetch_page(url_tdr)
                    if detail_soup:
                        pdf_url = extract_pdf_url(detail_soup, self.base_url)
                        if pdf_url:
                            url_tdr = pdf_url
                
                offre_base['url_tdr'] = url_tdr
                offre_base['type_offre'] = 'APPEL_D_OFFRES'
                
                if not any(o['url_source'] == offre_base['url_source'] for o in offres):
                    offres.append(offre_base)
                    logger.info(f"  ✅ Appel d'offres extrait (domaine: {offre_base.get('domaine', 'Autres')})")
                    
            except Exception as e:
                logger.debug(f"⚠️ Erreur parsing bloc ABF: {e}")
                continue
        
        logger.info(f"✅ ABF Burkina: {len(offres)} appel(s) d'offres extrait(s)")
        return offres
    
    def _parser_article_base(self, article) -> dict | None:
        # ✅ CORRECTION : Ignorer les éléments de navigation
        titre_elem = article.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'title|entry', re.I)) 
        if not titre_elem:
            titre_elem = article.find(['h2', 'h3', 'h4'])
            
        if not titre_elem:
            return None
        
        titre = clean_text(titre_elem.get_text(strip=True))
        
        # ✅ CORRECTION : Filtre agressif des faux titres
        if len(titre) < 15 or any(w in titre.lower() for w in ['navigation', 'recherche', 'partenaires', 'contact', 'en savoir plus']):
            return None
        
        description = ""
        contenu = article.find(['div', 'section'], class_=re.compile(r'content|entry|text|excerpt|field', re.I))
        if contenu:
            paragraphes = contenu.find_all('p') if hasattr(contenu, 'find_all') else [contenu]
            if paragraphes:
                description = clean_text(' '.join(p.get_text(strip=True) for p in paragraphes[:3]))
        
        if not description or len(description) < 20:
            description = titre # Fallback

        url_source = None
        link_inside_title = titre_elem.find('a', href=True) if hasattr(titre_elem, 'find') else None
        if link_inside_title:
            url_source = urljoin(self.base_url, link_inside_title['href'])
        else:
            url_source = self._extraire_lien_detail(article)
            
        if not url_source:
            return None
            
        texte_complet = article.get_text()
        
        date_pub = date.today()
        date_cloture = self._extraire_date_limite(texte_complet)
        if not date_cloture:
            date_cloture = date_pub + timedelta(days=30)
        
        organisme = self._extraire_donueur(texte_complet) or 'ABF Burkina Faso'
        categorie = self._extraire_categorie(texte_complet)
        
        domaine = self.detecter_domaine(titre, description)
        if categorie:
            domaine_par_categorie = self.detecter_domaine(categorie)
            if domaine_par_categorie and domaine_par_categorie != 'Autres':
                domaine = domaine_par_categorie
        
        if categorie:
            description = f"Catégorie : {categorie}. {description}"

        return {
            'titre': titre[:300],
            'organisme': organisme[:200],
            'description': description[:500],
            'date_publication': date_pub,
            'date_cloture': date_cloture,
            'url_source': url_source,
            'url_tdr': url_source,
            'pays': self.pays_defaut,
            'domaine': domaine,
            'statut': 'Ouvert',
            'mode_acquisition': 'AUTO',
        }
    
    def _extraire_date_limite(self, texte: str) -> date | None:
        patterns = [
            r'Date limite\s*:\s*([0-9]{1,2}\s+\w+\s+[0-9]{4})',
            r'Deadline\s*:\s*([0-9]{1,2}\s+\w+\s+[0-9]{4})',
            r'Date limite\s*:\s*([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})',
            r'clôture\s*:\s*([0-9]{1,2}\s+\w+\s+[0-9]{4})',
            r'jusqu\'au\s+([0-9]{1,2}\s+\w+\s+[0-9]{4})',
        ]
        for pattern in patterns:
            match = re.search(pattern, texte, re.IGNORECASE)
            if match:
                try: return parse_french_date(match.group(1))
                except: continue
        return None
    
    def _extraire_donueur(self, texte: str) -> str | None:
        match = re.search(r'(?:donneur|organisme|bailleur)\s*:\s*([^\n\.]+)', texte, re.IGNORECASE)
        return clean_text(match.group(1)) if match else None
    
    def _extraire_categorie(self, texte: str) -> str | None:
        match = re.search(r'(?:catégorie|secteur|type|thématique)\s*:\s*([^\n\.]+)', texte, re.IGNORECASE)
        return clean_text(match.group(1)) if match else None
    
    def _extraire_lien_detail(self, article) -> str | None:
        for lien in article.find_all('a', href=True):
            href = lien['href'].strip()
            texte = lien.get_text(strip=True).lower()
            # ✅ CORRECTION : Exclure explicitement les boutons "lire la suite"
            if any(m in texte for m in ['lire', 'suite', 'plus', 'voir', 'detail']) and len(texte) < 30:
                # Vérifier si ce n'est pas juste un bouton générique
                if 'en savoir plus' in texte or 'lire la suite' in texte:
                    continue
                return urljoin(self.base_url, href)
        return None