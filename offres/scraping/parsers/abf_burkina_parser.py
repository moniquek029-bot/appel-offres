# offres/scraping/abf_burkina.py
# Scraper spécialisé pour ABF Burkina Faso

import re
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import date, timedelta

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, parse_french_date

logger = logging.getLogger(__name__)


class ABFBurkinaScraper(BaseScraper):
    """
    Scraper spécialisé pour https://www.abfburkina.org/
    Extrait les appels à projets avec métadonnées structurées sur le modèle UNDP.
    """
    
    def __init__(self, source_url: str = "https://www.abfburkina.org/appels-a-projets/", **kwargs):
        base_url = "https://www.abfburkina.org"
        super().__init__(source_url, delay_seconds=2, base_url=base_url, **kwargs)
        self.pays_defaut = 'BF'

    def run(self) -> list[dict]:
        """Méthode d'entrée principale requise par Celery."""
        logger.info(f"🕷️ ABF Burkina scraping: {self.source_url}")
        try:
            soup = self.fetch_and_parse(use_js=False)
            if not soup:
                return []
            return self.parse(soup)
        except Exception as e:
            logger.error(f"❌ Erreur ABF Burkina lors du run: {e}")
            return []
    
    def extract_pdf_from_detail(self, detail_url: str) -> str | None:
        """Visite la page de détail interne de l'ABF pour en extraire le TDR/PDF."""
        try:
            soup = self.fetch_page(detail_url)
            if not soup:
                return None
                
            for link in soup.find_all('a', href=True):
                href = link['href'].strip()
                texte = link.get_text(strip=True).lower()
                
                # Si lien direct vers un PDF
                if href.lower().endswith('.pdf') and not any(x in href.lower() for x in ['logo', 'header', 'footer']):
                    return urljoin(self.base_url, href)
                    
                # Si le texte du bouton indique explicitement un téléchargement
                if any(w in texte for w in ['tdr', 'télécharger', 'document', 'pièce', 'dossier']):
                    if not href.startswith('#') and not href.startswith('javascript:'):
                        return urljoin(self.base_url, href)
            return None
        except Exception as e:
            logger.warning(f"  ⚠️ Erreur extraction PDF interne ABF: {e}")
            return None
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        """Parse la page principale et visite les détails de chaque offre."""
        offres = []
        
        # Structure WordPress courante
        articles = soup.find_all(['article', 'div'], class_=re.compile(r'post|entry|item|article|type-page', re.I))
        
        if not articles:
            titres = soup.find_all(['h2', 'h3', 'h4'])
            for titre in titres:
                parent = titre.find_parent(['article', 'div', 'section'])
                if parent and parent not in articles:
                    articles.append(parent)
        
        logger.info(f"🔍 ABF Burkina: {len(articles)} blocs potentiels trouvés")
        
        for i, article in enumerate(articles[:20], 1):  # Limite à 20 pour calquer l'UNDP et éviter les timeouts
            try:
                # Extraction des bases de l'article de la liste
                offre_base = self._parser_article_base(article)
                if not offre_base:
                    continue
                
                logger.info(f"  [{i}/{len(articles)}] Extraction détails: {offre_base['titre'][:50]}...")
                
                # 🎯 Visite immédiate et dynamique de la page de détail pour récupérer le TDR (Comme l'UNDP)
                url_tdr = self.extract_pdf_from_detail(offre_base['url_source'])
                offre_base['url_tdr'] = url_tdr
                
                # Éviter les doublons
                if not any(o['url_source'] == offre_base['url_source'] for o in offres):
                    offres.append(offre_base)
                    
            except Exception as e:
                logger.debug(f"⚠️ Erreur parsing bloc ABF: {e}")
                continue
        
        logger.info(f"✅ ABF Burkina: {len(offres)} offre(s) extraite(s) au total")
        return offres
    
    def _parser_article_base(self, article) -> dict | None:
        """Parse les données de surface d'un article."""
        titre_elem = article.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'title|entry', re.I)) or article.find(['h2', 'h3', 'h4'])
        if not titre_elem:
            return None
        
        titre = clean_text(titre_elem.get_text(strip=True))
        if len(titre) < 12 or any(w in titre.lower() for w in ['navigation', 'recherche', 'partenaires', 'contact']):
            return None
        
        description = ""
        contenu = article.find(['div', 'section', 'p'], class_=re.compile(r'content|entry|text|excerpt', re.I))
        if contenu:
            paragraphes = contenu.find_all('p') if hasattr(contenu, 'find_all') else [contenu]
            if paragraphes:
                description = clean_text(' '.join(p.get_text(strip=True) for p in paragraphes[:2]))
        if not description:
            description = titre

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
        if not date_cloture or date_cloture <= date_pub:
            date_cloture = date_pub + timedelta(days=30)
        
        organisme = self._extraire_donueur(texte_complet) or 'ABF Burkina Faso'
        montant = self._extraire_montant(texte_complet)
        categorie = self._extraire_categorie(texte_complet)
        
        offre = {
            'titre': titre[:300],
            'organisme': organisme[:200],
            'description': description[:500],
            'date_publication': date_pub,
            'date_cloture': date_cloture,
            'url_source': url_source,
            'url_tdr': None,  # Injecté dynamiquement juste après
            'pays': self.pays_defaut,
            'statut': 'Ouvert',
            'mode_acquisition': 'AUTO',
        }
        
        meta_champs = []
        if montant: meta_champs.append(f"Montant : {montant}")
        if categorie: meta_champs.append(f"Catégorie : {categorie}")
        if meta_champs:
            offre['description'] = f"{offre['description']}\n\n{' | '.join(meta_champs)}"
        
        return offre
    
    def _extraire_date_limite(self, texte: str) -> date | None:
        patterns = [
            r'Date limite\s*:\s*([0-9]{1,2}\s+\w+\s+[0-9]{4})',
            r'Deadline\s*:\s*([0-9]{1,2}\s+\w+\s+[0-9]{4})',
            r'Date limite\s*:\s*([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})',
            r'clôture\s*:\s*([0-9]{1,2}\s+\w+\s+[0-9]{4})',
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
    
    def _extraire_montant(self, texte: str) -> str | None:
        match = re.search(r'(?:subvention|montant|financement)\s*:\s*([^\n\.]+)', texte, re.IGNORECASE)
        return clean_text(match.group(1)) if match else None
    
    def _extraire_categorie(self, texte: str) -> str | None:
        match = re.search(r'(?:catégorie|secteur|type)\s*:\s*([^\n\.]+)', texte, re.IGNORECASE)
        return clean_text(match.group(1)) if match else None
    
    def _extraire_lien_detail(self, article) -> str | None:
        for lien in article.find_all('a', href=True):
            href = lien['href'].strip()
            texte = lien.get_text(strip=True).lower()
            if any(m in texte for m in ['lire', 'suite', 'plus', 'voir', 'detail']):
                return urljoin(self.base_url, href)
        for lien in article.find_all('a', href=True):
            href = lien['href'].strip()
            if href and not href.startswith('#') and not any(ext in href.lower() for ext in ['.pdf', '.png', '.jpg']):
                return urljoin(self.base_url, href)
        return None