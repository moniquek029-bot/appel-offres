# offres/scraping/tasks.py - Version CORRIGÉE (Fallback + TDR intelligent + Support JS global)

from celery import shared_task
from django.utils import timezone
from urllib.parse import urlparse
from django.db import transaction
from django.core.files.base import ContentFile  
import logging
import requests
import time  

from offres.models import SourceScraping, AppelOffre
from offres.scraping.parsers.Oxfam_parser import OxfamParser
from offres.scraping.utils import (
    archive_expired_offres, clean_text, parse_french_date, 
    normalize_url, extract_pdf_from_page, is_valid_pdf_url, 
    download_pdf_file, fetch_and_validate_pdf,
    archive_and_delete_old_offres
)
from offres.services.notifications import check_and_notify_matches

# =============================================================================
# CONFIGURATION
# =============================================================================
USE_MOCK_FALLBACK = False
REQUIRE_PDF = False

logger = logging.getLogger(__name__)

# =============================================================================
# IMPORTS DES PARSERS
# =============================================================================
from offres.scraping.parsers.unfpa_parser import UNFPAParser
from offres.scraping.parsers.undp_parser import UNDPParser
from offres.scraping.parsers.agetib_parser import AgetibParser
from offres.scraping.parsers.sonabel_parser import SONABELParser
from offres.scraping.parsers.uemoa_parser import UEMOAParser
from offres.scraping.parsers.joffres_parser import JoffresParser
from offres.scraping.parsers.abf_burkina_parser import ABFBurkinaScraper
from offres.scraping.parsers.smart_parser import SmartParser
from offres.scraping.parsers.afdb_parser import AfDBParser
from offres.scraping.parsers.reliefweb_parser import ReliefWebParser
from offres.scraping.parsers.uemoa_parser import UEMOAParser

# =============================================================================
# REGISTRE DES PARSERS
# =============================================================================
PARSER_REGISTRY = {
    # === SITES INTERNATIONAUX ===
    "burkinafaso.unfpa.org": UNFPAParser,
    "www.unfpa.org": UNFPAParser,
    "procurement-notices.undp.org": UNDPParser,
    "www.afdb.org": AfDBParser,
    "reliefweb.int": ReliefWebParser,
    
    
    # === SITES BURKINA FASO ===
    "www.agetib.net": AgetibParser,
    "www.sonabel.bf": SONABELParser,
    "www.abfburkina.org": ABFBurkinaScraper,
    "abfburkina.org": ABFBurkinaScraper,
    "burkinafaso.oxfam.org": OxfamParser,
    
    # === SITES RÉGIONAUX ===
    "www.uemoa.int": UEMOAParser,
    "uemoa.int": UEMOAParser,
    
    # === SITES D'OFFRES INTERNATIONALES ===
    "www.joffres.net": JoffresParser,
    
    # === PARSER PAR DÉFAUT ===
    "default": SmartParser,
}


def get_parser_for_source(source):
    """Retourne le parser approprié pour une source"""
    try:
        parsed = urlparse(source.url_racine)
        domain = parsed.netloc.lower()
        
        #  SITES QUI NÉCESSITENT JAVASCRIPT
        JS_REQUIRED_SITES = [
            'undp.org',
            'worldbank.org',
            'un.org',
            'who.int'
        ]
        
        use_js = any(site in domain for site in JS_REQUIRED_SITES)
        
        for key, parser_class in PARSER_REGISTRY.items():
            if key in domain:
                if parser_class is SmartParser or parser_class is None:
                    return SmartParser(source.url_racine, use_js=use_js)
                return parser_class(source.url_racine)
        
        return SmartParser(source.url_racine, use_js=use_js)
        
    except Exception as e:
        logger.error(f"❌ Erreur sélection parser: {e}")
        return SmartParser(source.url_racine)


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_scheduled_scraping_task(self, source_id=None):
    """Tâche Celery pour le scraping (PDF optionnel + Fallback intelligent)"""
    if source_id:
        sources = SourceScraping.objects.filter(id=source_id, est_actif=True)
        logger.info(f" Scraping manuel pour source ID {source_id}")
    else:
        sources = SourceScraping.objects.filter(est_actif=True)
        logger.info(" Scraping automatique : toutes les sources actives")
    
    if not sources.exists():
        logger.warning(" Aucune source active trouvée")
        return {"new": 0, "updated": 0, "skipped": 0, "sources": 0}
    
    total_new = 0
    total_updated = 0
    total_skipped = 0

    for source in sources:
        try:
            logger.info(f" Scraping RÉEL: {source.nom} ({source.url_racine})")
            
            scraper = get_parser_for_source(source)
            if not scraper:
                logger.warning(f"⚠️ Source ignorée: {source.nom}")
                total_skipped += 1
                continue
            
            raw_offres = scraper.run()
            
            if not raw_offres:
                logger.warning(f" Aucune offre extraite pour {source.nom}")
                continue
            
            logger.info(f" {len(raw_offres)} offres brutes extraites")

            # Détection si le domaine requiert du JS
            parsed_domain = urlparse(source.url_racine).netloc.lower()
            is_js_site = any(site in parsed_domain for site in ['undp.org', 'worldbank.org', 'un.org', 'who.int'])

            for data in raw_offres:
                titre_debug = data.get('titre', '')[:30]
                
                # ÉTAPE 1 : Extraction du PDF si absent
                if not data.get('url_tdr') and data.get('url_source'):
                    try:
                        #  Sécurité JS : Si le site nécessite JavaScript
                        if is_js_site and hasattr(scraper, 'fetch_page'):
                            detail_soup = scraper.fetch_page(data['url_source'], use_js=True)
                            if detail_soup:
                                extracted_pdf = scraper._trouver_pdf_dans_page(detail_soup, data['url_source'])
                                if extracted_pdf:
                                    data['url_tdr'] = extracted_pdf
                                    logger.info(f" PDF extrait via DOM JS: {data['url_tdr'][:80]}...")
                        else:
                            # Fallback HTTP standard pour les sites sans JS complexe
                            headers = {'User-Agent': 'Mozilla/5.0'}
                            detail_response = requests.get(data['url_source'], headers=headers, timeout=15)
                            if detail_response.status_code == 200:
                                extracted_pdf = extract_pdf_from_page(detail_response.text, source.url_racine)
                                if extracted_pdf:
                                    data['url_tdr'] = extracted_pdf
                                    logger.info(f" PDF extrait via HTTP: {data['url_tdr'][:80]}...")
                    except Exception as pdf_err:
                        logger.debug(f" PDF non extrait pour '{titre_debug}': {pdf_err}")
                
                # ÉTAPE 2 : FALLBACK - Si toujours pas de TDR, utiliser url_source
                if not data.get('url_tdr') and data.get('url_source'):
                    data['url_tdr'] = data['url_source']
                    logger.info(f" FALLBACK: url_tdr = url_source pour '{titre_debug}...'")
                
                # Sauvegarde
                result = save_offre_real(data, source, require_pdf=REQUIRE_PDF)
                
                if result == 'created':
                    total_new += 1
                    logger.info(f" +1 Nouvelle: '{titre_debug}...'")
                elif result == 'updated':
                    total_updated += 1
                    logger.debug(f" +1 MAJ: '{titre_debug}...'")
                else:
                    total_skipped += 1
                    logger.debug(f"⏭ Ignorée: '{titre_debug}...'")

            source.last_scraped = timezone.now()
            source.save(update_fields=["last_scraped"])
            logger.info(f" Source {source.nom} traitée avec succès")

        except Exception as e:
            logger.error(f" Échec de la tâche pour la source {source.nom}: {e}")
            if self.request.retries < self.max_retries:
                raise self.retry(exc=e)
            else:
                logger.error(f" Échec définitif pour {source.nom}")

    logger.info(f" Terminé | +{total_new} nouvelles | ~{total_updated} MAJ | {total_skipped} ignorées")
    return {"new": total_new, "updated": total_updated, "skipped": total_skipped, "sources": sources.count()}


@transaction.atomic
def save_offre_real(data: dict, source: SourceScraping, require_pdf: bool = False) -> str:
    """
    Sauvegarde une offre avec logique intelligente :
    - Si url_tdr est un vrai PDF → téléchargement local
    - Si url_tdr = url_source (fallback) → pas de téléchargement, juste redirection
    """
    titre = clean_text(data.get('titre', '')).strip()
    organisme = clean_text(data.get('organisme', '')).strip()
    
    if not titre or not organisme:
        logger.debug(f"Ignorée (titre/organisme vide)")
        return 'skipped'
    
    url_source = normalize_url(data.get('url_source'), source.url_racine)
    url_tdr = normalize_url(data.get('url_tdr'), source.url_racine)
    
    if not url_source and not url_tdr:
        logger.warning(f"Ignorée (pas d'URL): {titre[:50]}...")
        return 'skipped'
    
    # DÉTECTER si url_tdr est un vrai PDF ou juste une redirection
    is_real_pdf = False
    if url_tdr and url_tdr != url_source:
        is_real_pdf = True
    
    # Éviter les doublons
    existing = None
    if url_source:
        existing = AppelOffre.objects.filter(url_source=url_source).first()
    
    if existing:
        updated = False
        
        if url_tdr and existing.url_tdr != url_tdr:
            existing.url_tdr = url_tdr
            updated = True
        
        if url_source and existing.url_source != url_source:
            existing.url_source = url_source
            updated = True
        
        if is_real_pdf and not existing.fichier_pdf:
            pdf_content = fetch_and_validate_pdf(url_tdr, titre)
            if pdf_content:
                filename = f"tdr_{int(time.time())}_{titre[:20].replace(' ', '_')}.pdf"
                existing.fichier_pdf = ContentFile(pdf_content, name=filename)
                updated = True
                logger.info(f" PDF téléchargé en mise à jour: {titre[:40]}...")
        
        if updated:
            existing.save(update_fields=['url_tdr', 'url_source', 'fichier_pdf', 'statut'])
            logger.info(f" MAJ Réussie: {titre[:40]}...")
            return 'updated'
        return 'skipped'
    
    # Extraction des dates
    date_pub = parse_french_date(data.get('date_publication')) or timezone.now().date()
    date_clot = parse_french_date(data.get('date_cloture'))
    
    if not date_clot:
        date_clot = date_pub + timezone.timedelta(days=30)
        logger.warning(f" Date clôture manquante pour '{titre[:30]}'. Fixée à J+30.")
    
    # Téléchargement du PDF à la création
    fichier_pdf = None
    if is_real_pdf:
        pdf_content = fetch_and_validate_pdf(url_tdr, titre)
        if pdf_content:
            filename = f"tdr_{int(time.time())}_{titre[:20].replace(' ', '_')}.pdf"
            fichier_pdf = ContentFile(pdf_content, name=filename)
            logger.info(f" PDF téléchargé à la création: {titre[:40]}...")
        elif require_pdf:
            logger.warning(f" Offre ignorée car PDF obligatoire introuvable: {titre[:40]}")
            return 'skipped'
    
    try:
        offre = AppelOffre.objects.create(
            titre=titre[:300],
            organisme=organisme[:200],
            description=clean_text(data.get('description', ''))[:2000],
            pays=data.get('pays', getattr(source, 'pays', 'BF')),
            date_publication=date_pub,
            date_cloture=date_clot,
            url_source=url_source,
            url_tdr=url_tdr,
            statut=data.get('statut', 'Ouvert'),
            mode_acquisition='AUTO',
            source_origine=source,
            fichier_pdf=fichier_pdf,
        )
        
        if fichier_pdf:
            logger.info(f"CRÉÉE avec PDF local: {titre[:40]}...")
        elif is_real_pdf:
            logger.info(f"CRÉÉE avec TDR externe: {titre[:40]}... | url_tdr={url_tdr}")
        elif url_tdr == url_source:
            logger.info(f" CRÉÉE avec redirection: {titre[:40]}... | url_tdr=url_source")
        else:
            logger.info(f" CRÉÉE sans document: {titre[:40]}...")
        
        return 'created'
    except Exception as e:
        logger.error(f" Erreur création BDD: {e}")
        return 'skipped'


@shared_task
def daily_archive_task():
    """Tâche quotidienne unifiée : Archive et purge les offres expirées"""
    logger.info(" Lancement du cycle de vie des offres (Archivage + Purge)...")
    try:
        archived, deleted = archive_and_delete_old_offres(days_to_keep=30)
        return {
            "status": "success",
            "archived_count": archived,
            "deleted_count": deleted
        }
    except Exception as e:
        logger.error(f" Erreur dans le cycle de vie : {e}")
        return {"status": "error", "archived_count": 0, "deleted_count": 0}


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def daily_alert_matching_task(self):
    """Matching offres ↔ critères experts"""
    try:
        logger.info(" Matching offres ↔ critères...")
        count = check_and_notify_matches()
        logger.info(f" {count} experts notifiés")
        return {"notified": count}
    except Exception as e:
        logger.error(f" Erreur matching: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        return {"notified": 0}
    


