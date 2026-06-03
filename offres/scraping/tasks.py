# offres/scraping/tasks.py - Version FINALE 100% RÉEL, SANS MOCK

from celery import shared_task
from django.utils import timezone
from urllib.parse import urlparse
from django.db import transaction
import logging
from bs4 import BeautifulSoup
import requests

from offres.models import SourceScraping, AppelOffre
from offres.scraping.utils import (
    archive_expired_offres, clean_text, parse_french_date, 
    normalize_url, extract_pdf_from_page, is_valid_pdf_url, 
    download_pdf_file, fetch_and_validate_pdf
)
from offres.services.notifications import check_and_notify_matches

# =============================================================================
# CONFIGURATION - 100% RÉEL, AUCUN MOCK
# =============================================================================
USE_MOCK_FALLBACK = False  # ← TOUJOURS FALSE pour production
REQUIRE_PDF = True         # ← Exiger un PDF valide pour chaque offre

# =============================================================================
# IMPORTS DES PARSERS (uniquement les fonctionnels)
# =============================================================================
from offres.scraping.parsers.unfpa_parser import UNFPAParser
from offres.scraping.parsers.undp_parser import UNDPParser
from offres.scraping.parsers.agetib_parser import AgetibParser
from offres.scraping.parsers.sonabel_parser import SONABELParser
from offres.scraping.parsers.uemoa_parser import UEMOAParser
from offres.scraping.parsers.joffres_parser import JoffresParser
from offres.scraping.parsers.smart_parser import SmartParser  # ✅ NOUVEAU: Parser universel

logger = logging.getLogger(__name__)

# =============================================================================
# REGISTRE DES PARSERS
# ✅ UNFPA, UNDP, etc. gardent leurs parsers spécifiques
# ✅ SmartParser pour tous les autres sites (ajoutables via l'admin)
# =============================================================================
PARSER_REGISTRY = {
    # Parsers spécifiques existants (NE RIEN CHANGER ICI)
    "burkinafaso.unfpa.org": UNFPAParser,
    "www.unfpa.org": UNFPAParser,
    "procurement-notices.undp.org": UNDPParser,  # UNDP utilise aussi UNFPAParser
    "www.agetib.net": AgetibParser,
    "www.sonabel.bf": SONABELParser,
    "www.uemoa.int": UEMOAParser,
    "www.joffres.net": JoffresParser,
    
    # ✅ NOUVEAU: SmartParser pour TOUS les autres sites
    # Cela permet d'ajouter n'importe quelle source via l'admin
    "default": SmartParser,
}


def get_parser_for_source(source):
    """
    Retourne le parser approprié pour une source
    - Priorité aux parsers spécifiques
    - Fallback sur SmartParser pour tout nouveau site
    """
    try:
        parsed = urlparse(source.url_racine)
        domain = parsed.netloc.lower()
        
        # 1. Chercher un parser spécifique pour ce domaine
        for key, parser_class in PARSER_REGISTRY.items():
            if key in domain:
                if parser_class is None:
                    return SmartParser(source.url_racine)
                logger.info(f"🔧 Parser spécifique pour {domain}: {parser_class.__name__}")
                return parser_class(source.url_racine)
        
        # 2. Fallback: SmartParser pour tout nouveau site
        logger.info(f"🔧 SmartParser utilisé pour {domain} (aucun parser spécifique)")
        return SmartParser(source.url_racine)
        
    except Exception as e:
        logger.error(f"❌ Erreur sélection parser: {e}")
        return SmartParser(source.url_racine)


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_scheduled_scraping_task(self, source_id=None):
    """
    Tâche Celery pour le scraping 100% RÉEL
    - Aucune donnée mock
    - PDF valide obligatoire
    - Supporte l'ajout de nouvelles sources via l'admin
    """
    if source_id:
        sources = SourceScraping.objects.filter(id=source_id, est_actif=True)
        logger.info(f"🔧 Scraping manuel pour source ID {source_id}")
    else:
        sources = SourceScraping.objects.filter(est_actif=True)
        logger.info("🔄 Scraping automatique : toutes les sources actives")
    
    if not sources.exists():
        logger.warning("⚠️ Aucune source active trouvée")
        return {"new": 0, "updated": 0, "skipped": 0, "sources": 0}
    
    total_new = 0
    total_updated = 0
    total_skipped = 0

    for source in sources:
        try:
            logger.info(f"🕷️ Scraping RÉEL: {source.nom} ({source.url_racine})")
            
            # ✅ get_parser_for_source fonctionne avec SmartParser par défaut
            scraper = get_parser_for_source(source)
            if not scraper:
                logger.warning(f"⚠️ Source ignorée (parser non disponible): {source.nom}")
                total_skipped += 1
                continue
            
            # Exécuter le scraping RÉEL
            raw_offres = scraper.run()
            
            if not raw_offres:
                logger.warning(f"⚠️ Aucune offre réelle extraite pour {source.nom}")
                continue
            
            logger.info(f"📦 {len(raw_offres)} offres brutes extraites")

            for data in raw_offres:
                titre_debug = data.get('titre', '')[:30]
                
                # Extraction du PDF depuis la page détail si nécessaire
                if not data.get('url_tdr') and data.get('url_source'):
                    try:
                        headers = {'User-Agent': 'Mozilla/5.0'}
                        detail_response = requests.get(data['url_source'], headers=headers, timeout=15)
                        if detail_response.status_code == 200:
                            extracted_pdf = extract_pdf_from_page(detail_response.text, source.url_racine)
                            if extracted_pdf:
                                data['url_tdr'] = extracted_pdf
                                logger.info(f"📎 PDF extrait: {data['url_tdr'][:80]}...")
                    except Exception as pdf_err:
                        logger.debug(f"⚠️ PDF non extrait: {pdf_err}")
                
                # Sauvegarde avec validation PDF stricte
                result = save_offre_real(data, source, require_pdf=REQUIRE_PDF)
                
                if result == 'created':
                    total_new += 1
                    logger.info(f"✅ +1 Nouvelle (avec PDF): '{titre_debug}...'")
                elif result == 'updated':
                    total_updated += 1
                    logger.debug(f"🔄 +1 MAJ: '{titre_debug}...'")
                else:
                    total_skipped += 1
                    logger.debug(f"❌ Rejetée (pas de PDF valide): '{titre_debug}...'")

            source.last_scraped = timezone.now()
            source.save(update_fields=["last_scraped"])
            logger.info(f"✅ Source {source.nom} traitée")

        except Exception as e:
            logger.error(f"❌ Échec source {source.nom}: {e}")
            if self.request.retries < self.max_retries:
                raise self.retry(exc=e)
            else:
                logger.error(f"❌ Échec définitif pour {source.nom}")

    logger.info(f"🏁 Terminé | +{total_new} nouvelles | ~{total_updated} MAJ | {total_skipped} ignorées")
    return {"new": total_new, "updated": total_updated, "skipped": total_skipped, "sources": sources.count()}


@transaction.atomic
def save_offre_real(data: dict, source: SourceScraping, require_pdf: bool = True) -> str:
    """
    Sauvegarde une offre RÉELLE avec validation PDF stricte
    Retourne 'created', 'updated' ou 'skipped'
    """
    titre = clean_text(data.get('titre', '')).strip()
    organisme = clean_text(data.get('organisme', '')).strip()
    
    if not titre or not organisme:
        logger.debug(f"⚠️ Ignorée (titre/organisme vide): titre='{titre}', organisme='{organisme}'")
        return 'skipped'
    
    url_source = normalize_url(data.get('url_source'), source.url_racine)
    url_tdr = normalize_url(data.get('url_tdr'), source.url_racine)
    
    # ✅ VALIDATION STRICTE: PDF obligatoire
    if require_pdf and not url_tdr:
        logger.info(f"❌ Rejetée (pas d'URL TDR): {titre[:50]}...")
        return 'skipped'
    
    if url_tdr and require_pdf:
        if not is_valid_pdf_url(url_tdr):
            logger.info(f"❌ Rejetée (PDF invalide): {titre[:50]}...")
            return 'skipped'
    
    if not url_source and not url_tdr:
        logger.warning(f"⚠️ Ignorée (pas d'URL): {titre[:50]}...")
        return 'skipped'
    
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
        
        # Télécharger le PDF si manquant
        if url_tdr and not existing.fichier_pdf:
            pdf_content = fetch_and_validate_pdf(url_tdr, titre)
            if pdf_content:
                from django.core.files.base import ContentFile
                import time
                filename = f"tdr_{int(time.time())}_{titre[:20].replace(' ', '_')}.pdf"
                existing.fichier_pdf = ContentFile(pdf_content, name=filename)
                updated = True
                logger.info(f"✅ PDF téléchargé pour offre existante: {titre[:40]}...")
        
        if updated:
            existing.save(update_fields=['url_tdr', 'url_source', 'fichier_pdf', 'statut'])
            logger.info(f"🔄 MAJ: {titre[:40]}...")
            return 'updated'
        return 'skipped'
    
    # Création d'une nouvelle offre
    date_pub = parse_french_date(data.get('date_publication')) or timezone.now().date()
    date_clot = parse_french_date(data.get('date_cloture'))
    
    # Télécharger le PDF
    fichier_pdf = None
    if url_tdr and require_pdf:
        pdf_content = fetch_and_validate_pdf(url_tdr, titre)
        if pdf_content:
            from django.core.files.base import ContentFile
            import time
            filename = f"tdr_{int(time.time())}_{titre[:20].replace(' ', '_')}.pdf"
            fichier_pdf = ContentFile(pdf_content, name=filename)
            logger.info(f"✅ PDF téléchargé: {titre[:40]}...")
        else:
            logger.info(f"❌ Rejetée (échec téléchargement PDF): {titre[:40]}...")
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
            url_tdr=url_tdr if url_tdr != url_source else None,
            statut=data.get('statut', 'Ouvert'),
            mode_acquisition='AUTO',
            source_origine=source,
            fichier_pdf=fichier_pdf,
        )
        logger.info(f"✅ CRÉÉE: {titre[:40]}... | PDF: {'✓' if fichier_pdf else '✗'}")
        return 'created'
    except Exception as e:
        logger.error(f"❌ Erreur création: {e}")
        return 'skipped'


@shared_task
def daily_archive_task():
    """Archive les offres expirées"""
    logger.info("🗄️ Archivage automatique...")
    try:
        count = archive_expired_offres()
        logger.info(f"✅ {count} offres archivées")
        return {"archived": count}
    except Exception as e:
        logger.error(f"❌ Erreur archivage: {e}")
        return {"archived": 0}


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def daily_alert_matching_task(self):
    """Matching offres ↔ critères experts"""
    try:
        logger.info("🎯 Matching offres ↔ critères...")
        count = check_and_notify_matches()
        logger.info(f"✅ {count} experts notifiés")
        return {"notified": count}
    except Exception as e:
        logger.error(f"❌ Erreur matching: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        return {"notified": 0}