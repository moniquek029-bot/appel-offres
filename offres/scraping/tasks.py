# offres/scraping/tasks.py - Version CORRIGÉE (Fallback + TDR intelligent + Support JS global + Dates corrigées)

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
from offres.scraping.site_validator import SiteValidator, is_valid_offer_title, is_rejected_content

# ✅ Ajout de l'import pour l'extraction des dates
from offres.scraping.extraction_helpers import extract_publication_date_from_text

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

# =============================================================================
# REGISTRE DES PARSERS
# =============================================================================
PARSER_REGISTRY = {
    # === SITES INTERNATIONAUX ===
    "burkinafaso.unfpa.org": UNFPAParser,
    "www.unfpa.org": UNFPAParser,
    "procurement-notices.undp.org": UNDPParser,
    "www.afdb.org": AfDBParser,
    
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

# =============================================================================
# ✅ LISTE BLANCHE : Sites de confiance (validation ignorée)
# =============================================================================
TRUSTED_SOURCES = [
    'unfpa.org',
    'uemoa.int',
    'agetib.net',
    'sonabel.bf',
    'abfburkina.org',
    'joffres.net',
    'oxfam.org',
]


def get_parser_for_source(source):
    """Retourne le parser approprié pour une source"""
    try:
        parsed = urlparse(source.url_racine)
        domain = parsed.netloc.lower()
        
        # SITES QUI NÉCESSITENT JAVASCRIPT
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


def is_trusted_source(url_racine: str) -> bool:
    """Vérifie si une source est dans la liste blanche"""
    parsed_domain = urlparse(url_racine).netloc.lower()
    return any(trusted in parsed_domain for trusted in TRUSTED_SOURCES)


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_scheduled_scraping_task(self, source_id=None):
    """Tâche Celery pour le scraping (PDF optionnel + Fallback intelligent + Validation des sites)"""
    
    if source_id:
        sources = SourceScraping.objects.filter(id=source_id, est_actif=True)
        logger.info(f"🕷️ Scraping manuel pour source ID {source_id}")
    else:
        sources = SourceScraping.objects.filter(est_actif=True)
        logger.info("🕷️ Scraping automatique : toutes les sources actives")
    
    if not sources.exists():
        logger.warning("⚠️ Aucune source active trouvée")
        return {"new": 0, "updated": 0, "skipped": 0, "sources": 0}
    
    total_new = 0
    total_updated = 0
    total_skipped = 0
    total_rejected = 0

    for source in sources:
        try:
            logger.info(f"🕷️ Scraping RÉEL: {source.nom} ({source.url_racine})")
            
            scraper = get_parser_for_source(source)
            if not scraper:
                logger.warning(f"⚠️ Source ignorée: {source.nom}")
                total_skipped += 1
                continue
            
            # =========================================================================
            # ✅ VALIDATION DU SITE (uniquement pour les sites NON-fiables)
            # =========================================================================
            if is_trusted_source(source.url_racine):
                logger.info(f"✅ Site de confiance, validation ignorée: {source.nom}")
            else:
                logger.info(f"🔍 Validation du site: {source.nom}")
                
                try:
                    validation_soup = scraper.fetch_and_parse(use_js=False)
                    
                    if validation_soup:
                        validator = SiteValidator(soup=validation_soup, url=source.url_racine)
                        validation = validator.validate()
                        
                        if not validation.get('is_valid', False):
                            logger.warning(f"❌ Site REJETÉ: {source.nom}")
                            logger.warning(f"   Score: {validation.get('score', 0)}")
                            logger.warning(f"   Raisons: {validation.get('rejection_reasons', [])}")
                            logger.warning(f"   → Ce site ne semble pas publier d'appels d'offres")
                            total_rejected += 1
                            continue
                        
                        logger.info(f"✅ Site VALIDÉ: {source.nom} (Score: {validation.get('score', 0)}, Confiance: {validation.get('confidence', 'low')})")
                    else:
                        logger.warning(f"⚠️ Impossible de récupérer la page pour validation: {source.nom}")
                
                except Exception as val_err:
                    logger.warning(f"⚠️ Erreur lors de la validation: {val_err}")
            
            # =========================================================================
            # SCRAPING DES OFFRES
            # =========================================================================
            raw_offres = scraper.run()
            
            if not raw_offres:
                logger.warning(f"⚠️ Aucune offre extraite pour {source.nom}")
                continue
            
            logger.info(f"📊 {len(raw_offres)} offres brutes extraites")

            # Détection si le domaine requiert du JS
            parsed_domain = urlparse(source.url_racine).netloc.lower()
            is_js_site = any(site in parsed_domain for site in ['undp.org', 'worldbank.org', 'un.org', 'who.int'])

            for data in raw_offres:
                titre_debug = data.get('titre', '')[:30]
                
                # =========================================================================
                # ✅ VALIDATION DE L'OFFRE INDIVIDUELLE
                # =========================================================================
                titre_offre = data.get('titre', '').strip()
                description_offre = data.get('description', '').strip()
                
                # Vérifier que c'est bien un appel d'offres
                if not is_valid_offer_title(titre_offre):
                    logger.info(f"⏭️ Offre REJETÉE (titre non-valide): '{titre_debug}...'")
                    total_rejected += 1
                    continue
                
                # Vérifier que ce n'est pas du contenu non-offre
                if is_rejected_content(titre_offre + ' ' + description_offre):
                    logger.info(f"⏭️ Offre REJETÉE (contenu non-offre): '{titre_debug}...'")
                    total_rejected += 1
                    continue
                
                # =========================================================================
                # EXTRACTION DU PDF SI ABSENT
                # =========================================================================
                if not data.get('url_tdr') and data.get('url_source'):
                    try:
                        if is_js_site and hasattr(scraper, 'fetch_page'):
                            detail_soup = scraper.fetch_page(data['url_source'], use_js=True)
                            if detail_soup:
                                extracted_pdf = scraper._trouver_pdf_dans_page(detail_soup, data['url_source'])
                                if extracted_pdf:
                                    data['url_tdr'] = extracted_pdf
                                    logger.info(f"📄 PDF extrait via DOM JS: {data['url_tdr'][:80]}...")
                        else:
                            headers = {'User-Agent': 'Mozilla/5.0'}
                            detail_response = requests.get(data['url_source'], headers=headers, timeout=15)
                            if detail_response.status_code == 200:
                                extracted_pdf = extract_pdf_from_page(detail_response.text, source.url_racine)
                                if extracted_pdf:
                                    data['url_tdr'] = extracted_pdf
                                    logger.info(f"📄 PDF extrait via HTTP: {data['url_tdr'][:80]}...")
                    except Exception as pdf_err:
                        logger.debug(f"⚠️ PDF non extrait pour '{titre_debug}': {pdf_err}")
                
                # FALLBACK - Si toujours pas de TDR, utiliser url_source
                if not data.get('url_tdr') and data.get('url_source'):
                    data['url_tdr'] = data['url_source']
                    logger.info(f"🔄 FALLBACK: url_tdr = url_source pour '{titre_debug}...'")
                
                # =========================================================================
                # SAUVEGARDE
                # =========================================================================
                result = save_offre_real(data, source, require_pdf=REQUIRE_PDF)
                
                if result == 'created':
                    total_new += 1
                    logger.info(f"✅ +1 Nouvelle: '{titre_debug}...'")
                elif result == 'updated':
                    total_updated += 1
                    logger.debug(f"🔄 +1 MAJ: '{titre_debug}...'")
                else:
                    total_skipped += 1
                    logger.debug(f"⏭️ Ignorée: '{titre_debug}...'")

            source.last_scraped = timezone.now()
            source.save(update_fields=["last_scraped"])
            logger.info(f"✅ Source {source.nom} traitée avec succès")

        except Exception as e:
            logger.error(f"❌ Échec de la tâche pour la source {source.nom}: {e}")
            if self.request.retries < self.max_retries:
                raise self.retry(exc=e)
            else:
                logger.error(f"❌ Échec définitif pour {source.nom}")

    logger.info(f"🏁 Terminé | +{total_new} nouvelles | ~{total_updated} MAJ | {total_skipped} ignorées | ❌ {total_rejected} rejetées")
    return {
        "new": total_new, 
        "updated": total_updated, 
        "skipped": total_skipped, 
        "rejected": total_rejected,
        "sources": sources.count()
    }


@transaction.atomic
def save_offre_real(data: dict, source: SourceScraping, require_pdf: bool = False) -> str:
    """
    Sauvegarde une offre avec validation stricte :
    - Vérifie que c'est bien un appel d'offres
    - Si url_tdr est un vrai PDF → téléchargement local
    - Si url_tdr = url_source (fallback) → pas de téléchargement
    - ✅ Dates corrigées : extraction de la date de publication du texte
    """
    titre = clean_text(data.get('titre', '')).strip()
    organisme = clean_text(data.get('organisme', '')).strip()
    
    # ✅ VALIDATION 1 : Titre et organisme obligatoires
    if not titre or not organisme:
        logger.debug(f"⏭️ Ignorée (titre/organisme vide)")
        return 'skipped'
    
    # ✅ VALIDATION 2 : Vérifier que c'est un appel d'offres
    if not is_valid_offer_title(titre):
        logger.info(f"⏭️ REJETÉE - Pas un appel d'offres: {titre[:50]}...")
        return 'skipped'
    
    # ✅ VALIDATION 3 : Vérifier que ce n'est pas du contenu non-offre
    description = clean_text(data.get('description', ''))
    if is_rejected_content(titre + ' ' + description):
        logger.info(f"⏭️ REJETÉE - Contenu non-offre: {titre[:50]}...")
        return 'skipped'
    
    url_source = normalize_url(data.get('url_source'), source.url_racine)
    url_tdr = normalize_url(data.get('url_tdr'), source.url_racine)
    
    if not url_source and not url_tdr:
        logger.warning(f"⏭️ Ignorée (pas d'URL): {titre[:50]}...")
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
                logger.info(f"📄 PDF téléchargé en mise à jour: {titre[:40]}...")
        
        if updated:
            existing.save(update_fields=['url_tdr', 'url_source', 'fichier_pdf', 'statut'])
            logger.info(f"✅ MAJ Réussie: {titre[:40]}...")
            return 'updated'
        return 'skipped'
    
    # =========================================================================
    # ✅ EXTRACTION DES DATES AMÉLIORÉE
    # =========================================================================
    
    # 1. Essayer la date extraite par le parser
    date_pub = parse_french_date(data.get('date_publication'))
    
    # 2. Si pas de date ou date = aujourd'hui (scraping), essayer d'extraire du texte
    if not date_pub or date_pub == timezone.now().date():
        texte_complet = titre + ' ' + description
        extracted_pub = extract_publication_date_from_text(texte_complet)
        if extracted_pub and extracted_pub <= timezone.now().date():
            date_pub = extracted_pub
            logger.info(f"📅 Date de publication extraite du texte: {date_pub}")
    
    # 3. Fallback: aujourd'hui
    if not date_pub:
        date_pub = timezone.now().date()
        logger.info(f"📅 Date de publication par défaut: {date_pub}")
    
    # 4. S'assurer que date_pub n'est pas dans le futur
    if date_pub > timezone.now().date():
        date_pub = timezone.now().date()
        logger.warning(f"⚠️ Date de publication corrigée (était dans le futur): {date_pub}")
    
    # 5. Date de clôture
    date_clot = parse_french_date(data.get('date_cloture'))
    if not date_clot:
        date_clot = date_pub + timezone.timedelta(days=30)
        logger.warning(f"⚠️ Date clôture manquante, fixée à J+30: {date_clot}")
    
    # 6. S'assurer que date_cloture > date_publication
    if date_clot < date_pub:
        date_clot = date_pub + timezone.timedelta(days=30)
        logger.warning(f"⚠️ Date clôture corrigée (était avant publication): {date_clot}")
    
    # =========================================================================
    # Téléchargement du PDF à la création
    # =========================================================================
    fichier_pdf = None
    if is_real_pdf:
        pdf_content = fetch_and_validate_pdf(url_tdr, titre)
        if pdf_content:
            filename = f"tdr_{int(time.time())}_{titre[:20].replace(' ', '_')}.pdf"
            fichier_pdf = ContentFile(pdf_content, name=filename)
            logger.info(f"📄 PDF téléchargé à la création: {titre[:40]}...")
        elif require_pdf:
            logger.warning(f"⏭️ Offre ignorée car PDF obligatoire introuvable: {titre[:40]}")
            return 'skipped'
    
    try:
        offre = AppelOffre.objects.create(
            titre=titre[:300],
            organisme=organisme[:200],
            description=description[:2000],
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
            logger.info(f"✅ CRÉÉE avec PDF local: {titre[:40]}...")
        elif is_real_pdf:
            logger.info(f"✅ CRÉÉE avec TDR externe: {titre[:40]}... | url_tdr={url_tdr}")
        elif url_tdr == url_source:
            logger.info(f"✅ CRÉÉE avec redirection: {titre[:40]}... | url_tdr=url_source")
        else:
            logger.info(f"✅ CRÉÉE sans document: {titre[:40]}...")
        
        return 'created'
    except Exception as e:
        logger.error(f"❌ Erreur création BDD: {e}")
        return 'skipped'


@shared_task
def daily_archive_task():
    """Tâche quotidienne unifiée : Archive et purge les offres expirées"""
    logger.info("🗑️ Lancement du cycle de vie des offres (Archivage + Purge)...")
    try:
        archived, deleted = archive_and_delete_old_offres(days_to_keep=30)
        return {
            "status": "success",
            "archived_count": archived,
            "deleted_count": deleted
        }
    except Exception as e:
        logger.error(f"❌ Erreur dans le cycle de vie : {e}")
        return {"status": "error", "archived_count": 0, "deleted_count": 0}


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def daily_alert_matching_task(self):
    """Matching offres ↔ critères experts"""
    try:
        logger.info("🔔 Matching offres ↔ critères...")
        count = check_and_notify_matches()
        logger.info(f"📧 {count} experts notifiés")
        return {"notified": count}
    except Exception as e:
        logger.error(f"❌ Erreur matching: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        return {"notified": 0}