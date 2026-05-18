# offres/scraping/tasks.py
from celery import shared_task
from django.utils import timezone
from urllib.parse import urlparse
from django.db import transaction, models
import logging

from offres.models import SourceScraping, AppelOffre
from offres.scraping.utils import archive_expired_offres, clean_text, parse_french_date, normalize_url
from offres.services.notifications import check_and_notify_matches

# IMPORTS DES PARSERS
from offres.scraping.parsers.template import TemplateSiteParser
from offres.scraping.parsers.j360_burkina import J360BurkinaParser
from offres.scraping.parsers.j360_mock import J360MockParser
from offres.scraping.parsers.joffres_parser import JoffresParser  
from offres.scraping.parsers.agetib_parser import AgetibParser
from offres.scraping.parsers.globaltenders_parser import GlobalTendersParser  

logger = logging.getLogger(__name__)


# =============================================================================
# REGISTRE DES PARSERS
# =============================================================================
PARSER_REGISTRY = {
    "https://www.j360.info/appels-d-offres/afrique/burkina-faso": J360BurkinaParser,
    "https://app.j360.info": J360MockParser,
    "https://www.joffres.net/les_appeloffre/filtre": JoffresParser,
    "https://www.agetib.net/appels-offres": AgetibParser,
    "https://www.agetib.net/appels-d-offres": AgetibParser,
    "https://www.globaltenders.com": GlobalTendersParser,
    "https://www.globaltenders.com/appels-d-offres": GlobalTendersParser,
    "default": TemplateSiteParser,
}


# =============================================================================
# TÂCHE 1 : SCRAPPING PLANIFIÉ
# =============================================================================
@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def run_scheduled_scraping_task(self, source_id=None):
    """Lance le scraping sur les sources actives"""
    
    if source_id:
        sources = SourceScraping.objects.filter(id=source_id, est_actif=True)
        logger.info(f"🔧 Scraping manuel pour source ID {source_id}")
    else:
        sources = SourceScraping.objects.filter(est_actif=True)
        logger.info("🔄 Scraping automatique : toutes les sources actives")
    
    total_new = 0
    total_updated = 0
    total_skipped = 0

    for source in sources:
        try:
            logger.info(f"🕷️ Scraping : {source.nom} ({source.url_racine})")
            
            # Sélection du parser via registre
            parsed = urlparse(source.url_racine)
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
            parser_class = PARSER_REGISTRY.get(base_url) or PARSER_REGISTRY.get("default")
            
            if not parser_class:
                logger.warning(f"⚠️ Aucun parser pour {source.url_racine}")
                continue
            
            # Exécution du scraping
            scraper = parser_class(source.url_racine)
            raw_offres = scraper.run()
            logger.info(f"📦 {len(raw_offres)} offres brutes extraites")

            # Insertion/Mise à jour en base
            for data in raw_offres:
                result = save_offre_with_fallback(data, source)
                if result == 'created':
                    total_new += 1
                elif result == 'updated':
                    total_updated += 1
                else:
                    total_skipped += 1

            # Mise à jour timestamp
            source.last_scraped = timezone.now()
            source.save(update_fields=["last_scraped"])
            logger.info(f"✅ Source {source.nom} traitée")

        except Exception as e:
            logger.error(f"❌ Échec source {source.nom}: {type(e).__name__} - {e}")
            raise self.retry(exc=e)

    logger.info(f"🏁 Terminé | +{total_new} nouvelles | ~{total_updated} MAJ | {total_skipped} ignorées")
    return {"new": total_new, "updated": total_updated, "skipped": total_skipped, "sources": len(sources)}


# =============================================================================
# FONCTION DE SAUVEGARDE ROBUSTE
# =============================================================================
@transaction.atomic
def save_offre_with_fallback(data: dict, source: SourceScraping) -> str:
    """
    Sauvegarde une offre avec gestion des deux URLs : source et TDR.
    Retourne: 'created' | 'updated' | 'skipped'
    """
    # Nettoyage des champs
    titre = clean_text(data.get('titre', '')).strip()
    organisme = clean_text(data.get('organisme', '')).strip()
    
    if not titre or not organisme:
        logger.debug(f"⚠️ Ignorée (titre/organisme vide)")
        return 'skipped'
    
    # ✅ Extraction des DEUX URLs
    url_source = normalize_url(data.get('url_source') or data.get('url_page'), source.url_racine)
    url_tdr = normalize_url(data.get('url_tdr') or data.get('url_document'), source.url_racine)
    
    # Validation : au moins une URL doit être présente
    if not url_source and not url_tdr:
        logger.warning(f"⚠️ Ignorée (pas d'URL): {titre[:50]}...")
        return 'skipped'
    
    # ✅ Détection de doublon : prioriser url_tdr si présent, sinon url_source
    unique_url = url_tdr or url_source
    existing = AppelOffre.objects.filter(
        models.Q(url_tdr=unique_url) | models.Q(url_source=unique_url)
    ).first()
    
    if existing:
        # Mise à jour si changements
        updated = False
        if url_tdr and existing.url_tdr != url_tdr:
            existing.url_tdr = url_tdr
            updated = True
        if url_source and existing.url_source != url_source:
            existing.url_source = url_source
            updated = True
        
        new_statut = data.get("statut", "Ouvert")
        if existing.statut != new_statut:
            existing.statut = new_statut
            updated = True
        
        if updated:
            existing.save(update_fields=['url_tdr', 'url_source', 'statut'])
            logger.debug(f"🔄 MAJ: {titre[:50]}...")
            return 'updated'
        return 'skipped'
    
    # ✅ Création nouvelle offre
    date_pub = parse_french_date(data.get('date_publication')) or timezone.now().date()
    date_clot = parse_french_date(data.get('date_cloture'))
    
    AppelOffre.objects.create(
        titre=titre,
        organisme=organisme,
        description=clean_text(data.get('description', ''))[:2000],
        pays=data.get('pays', 'BF'),
        date_publication=date_pub,
        date_cloture=date_clot,
        url_source=url_source,
        url_tdr=url_tdr if url_tdr != url_source else None,
        statut=data.get('statut', 'Ouvert'),
        mode_acquisition=data.get('mode_acquisition', 'AUTO'),
        source_origine=source,
    )
    logger.info(f"✅ Nouvelle: {titre[:50]}... | TDR: {'✓' if url_tdr else '✗'}")
    return 'created'


# =============================================================================
# TÂCHE 2 : ARCHIVAGE AUTOMATIQUE
# =============================================================================
@shared_task
def daily_archive_task():
    """Archive les offres dont la date de clôture est dépassée"""
    logger.info("🗄️ Archivage automatique...")
    count = archive_expired_offres()
    logger.info(f"✅ {count} offres archivées")
    return {"archived": count}


# =============================================================================
# TÂCHE 3 : MATCHING & NOTIFICATIONS
# =============================================================================
@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def daily_alert_matching_task(self):
    """Envoie des alertes aux experts selon leurs critères"""
    try:
        logger.info("🎯 Matching offres ↔ critères...")
        count = check_and_notify_matches()
        logger.info(f"✅ {count} experts notifiés")
        return {"notified": count}
    except Exception as e:
        logger.error(f"❌ Erreur matching: {e}")
        raise self.retry(exc=e)