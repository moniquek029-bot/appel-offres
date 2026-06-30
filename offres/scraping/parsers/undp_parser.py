# offres/scraping/parsers/undp_parser.py
import re
import logging
from datetime import date, timedelta
from bs4 import BeautifulSoup

from offres.scraping.base import BaseScraper
from offres.scraping.utils import clean_text, normalize_url
from offres.scraping.extraction_helpers import extract_all_details, extract_pdf_url
from offres.utils.search_keywords import detecter_domaine, est_appel_offres

logger = logging.getLogger(__name__)


class UNDPParser(BaseScraper):
    """Parser UNDP - UNIQUEMENT les appels d'offres (RFQ/RFP)"""
    
    def __init__(self, source_url: str, base_url: str = "https://procurement-notices.undp.org", 
                 pays_defaut: str = 'BF', **kwargs):
        delay = kwargs.pop('delay_seconds', 2)
        super().__init__(
            source_url, 
            delay_seconds=delay,
            base_url=base_url, 
            pays_defaut=pays_defaut, 
            **kwargs
        )
    
    def detecter_domaine(self, titre, description=""):
        texte = (titre + " " + (description or "")).lower()
        
        mapping = {
            'IT & Digital': ['informatique', 'digital', 'ordinateur', 'logiciel', 'plateforme', 'data', 'système', 'it', 'technology', 'software', 'hardware', 'réseau', 'internet', 'cloud', 'cyber'],
            'Ingénierie & Construction': ['construction', 'réhabilitation', 'bâtiment', 'génie', 'infrastructure', 'travaux', 'rénovation', 'génie civil', 'architecte', 'chantier'],
            'Santé & Médical': ['santé', 'médical', 'hôpital', 'clinique', 'pharmaceutique', 'laboratoire', 'soins', 'médecine', 'health', 'medical'],
            'Transport & Logistique': ['transport', 'logistique', 'véhicule', 'motocyclette', 'livraison', 'camion', 'bus', 'car', 'fret', 'logistics', 'delivery', 'vehicle'],
            'Éducation & Formation': ['éducation', 'formation', 'enseignement', 'apprentissage', 'training', 'cours', 'études', 'pédagogie', 'education', 'learning'],
            'Environnement & Climat': ['environnement', 'climat', 'énergie', 'renouvelable', 'durable', 'écologie', 'développement durable', 'environment', 'climate', 'energy'],
            'Finance & Comptabilité': ['finance', 'comptabilité', 'audit', 'budget', 'compte', 'financier', 'fiscal', 'financial', 'accounting', 'budget', 'audit'],
            'Communication & Médias': ['communication', 'média', 'vidéo', 'documentaire', 'publicité', 'journal', 'radio', 'tv', 'media', 'video'],
            'Agriculture & Alimentation': ['agriculture', 'alimentation', 'agro', 'élevage', 'cultures', 'récolte', 'nourriture', 'agriculture', 'farming', 'food'],
            'Juridique & Droit': ['juridique', 'droit', 'loi', 'réglementation', 'légal', 'contrat', 'legal', 'law'],
            'Ressources Humaines': ['ressources humaines', 'rh', 'recrutement', 'embauche', 'personnel', 'staff', 'human resources', 'hr', 'recruitment'],
            'Sécurité & Protection': ['sécurité', 'protection', 'défense', 'armée', 'militaire', 'garde', 'sûreté', 'security', 'protection', 'safety'],
            'Social & Égalité': ['social', 'égalité', 'femme', 'jeune', 'égalité des genres', 'pauvreté', 'humanitaire', 'social', 'gender', 'women', 'youth', 'humanitarian'],
            'Biens & Équipements': ['bien', 'équipement', 'matériel', 'fourniture', 'achat', 'acquisition', 'equipment', 'supplies', 'procurement', 'purchase'],
            'Services & Conseil': ['service', 'conseil', 'consulting', 'consultant', 'étude', 'expertise', 'services', 'consulting', 'consultancy', 'advisory'],
        }
        
        for domaine, mots in mapping.items():
            for mot in mots:
                if mot in texte:
                    return domaine
        
        if any(mot in texte for mot in ['achat', 'fourniture', 'purchase', 'supply']):
            return 'Biens & Équipements'
        if any(mot in texte for mot in ['étude', 'consultant', 'consultancy', 'advisory']):
            return 'Services & Conseil'
        return 'Autres'
    
    def parse(self, soup: BeautifulSoup) -> list[dict]:
        offres = []
        
        notice_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'view_notice' not in href:
                continue
            
            titre = clean_text(link.get_text(strip=True))
            if titre.lower().startswith('title'):
                titre = titre[5:].strip()
            
            if len(titre) < 10:
                continue
            
            url_source = normalize_url(href, self.base_url)
            notice_links.append({'titre': titre, 'url_source': url_source})
        
        logger.info(f"🔍 {len(notice_links)} notices trouvées")
        
        for i, notice in enumerate(notice_links[:15], 1):
            logger.info(f"  [{i}/{len(notice_links)}] {notice['titre'][:50]}...")
            
            try:
                detail_soup = self.fetch_page(notice['url_source'])
                if not detail_soup:
                    continue
                
                # ✅ Extraire le PDF
                pdf_url = extract_pdf_url(detail_soup, self.base_url)
                
                details = extract_all_details(
                    detail_soup,
                    url=notice['url_source'],
                    pays_defaut=self.pays_defaut,
                    titre=notice['titre'],
                    description=notice['titre']
                )
                
                date_cloture = details.get('date_cloture')
                if date_cloture and date_cloture < date.today():
                    logger.info(f"     ⏭️ EXPIRÉE ({date_cloture})")
                    continue
                
                titre = notice['titre']
                description = notice['titre']
                domaine = self.detecter_domaine(titre, description)
                
                if details.get('domaine') and details.get('domaine') != 'Autres':
                    domaine = details.get('domaine')
                
                # ✅ REJET STRICT
                if not est_appel_offres(titre, description):
                    logger.info(f"     ⏭️ REJETÉ (pas un appel d'offres)")
                    continue
                
                # ✅ Fallback URL source
                url_tdr = pdf_url or details.get('url_tdr') or notice['url_source']
                
                offre = {
                    'titre': titre[:300],
                    'organisme': "UNDP",
                    'description': description[:1000],
                    'date_publication': details.get('date_publication', date.today()),
                    'date_cloture': date_cloture or (date.today() + timedelta(days=30)),
                    'url_source': notice['url_source'],
                    'url_tdr': url_tdr,
                    'pays': details.get('pays', self.pays_defaut),
                    'domaine': domaine,
                    'statut': 'Ouvert',
                    'type_offre': 'APPEL_D_OFFRES',
                    'mode_acquisition': 'AUTO',
                }
                
                if not any(o['url_source'] == offre['url_source'] for o in offres):
                    offres.append(offre)
                    logger.info(f"     ✅ AJOUTÉE (domaine: {domaine}, PDF: {bool(pdf_url)})")
                
            except Exception as e:
                logger.warning(f"     ⚠️ Erreur: {e}")
                continue
        
        logger.info(f"✅ UNDP: {len(offres)} appel(s) d'offres extrait(s)")
        return offres
    
    def run(self) -> list[dict]:
        logger.info(f"🕷️ UNDP scraping: {self.source_url}")
        try:
            soup = self.fetch_and_parse(use_js=False)
            if not soup:
                return []
            return self.parse(soup)
        except Exception as e:
            logger.error(f"❌ Erreur UNDP: {e}")
            return []