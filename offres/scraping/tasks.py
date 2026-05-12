#IMPORTS STANDARD & DJANGO
from celery import shared_task
from django.utils import timezone
from urllib.parse import urlparse

#IMPORTS DES MODELES & UTILITAIRES
from offres.models import SourceScraping, AppelOffre
from offres.scraping.utils import archive_expired_offres
from offres.services.notifications import check_and_notify_matches

# IMPORTS DES PARSERS (un par site source)
# =============================================================================
from offres.scraping.parsers.template import TemplateSiteParser
from offres.scraping.parsers.j360_burkina import J360BurkinaParser
from offres.scraping.parsers.j360_mock import J360MockParser
from offres.scraping.parsers.joffres_parser import JoffresParser  # ✅ Nom corrigé
from offres.scraping.parsers.agetib_parser import AgetibParser
from offres.scraping.parsers.cci_bf_parser import CCIBFParser  # ✅ Commentaire complété

import logging
logger = logging.getLogger(__name__)


# =============================================================================
# REGISTRE DES PARSERS : URL normalisée -> Classe Parser
# =============================================================================
PARSER_REGISTRY = {
    # J360
    "https://www.j360.info/appels-d-offres/afrique/burkina-faso": J360BurkinaParser,
    "https://app.j360.info": J360MockParser,
    
    # Joffres
    "https://www.joffres.net/les_appeloffre/filtre": JoffresParser,
    
    # Agetib
    "https://www.agetib.net/appels-offres": AgetibParser,
    "https://www.agetib.net/appels-d-offres": AgetibParser,
    
    # CCI-BF
    "https://www.cci-bf.net/appels-offres": CCIBFParser,
    "https://www.cci-bf.net/appels-d-offres": CCIBFParser,
    
    # Fallback
    "default": TemplateSiteParser,
}


# =============================================================================
# TÂCHE 1 : SCRAPPING PLANIFIÉ DES SOURCES ACTIVES
# =============================================================================
@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def run_scheduled_scraping_task(self, source_id=None):
    """
     CDC Module 2 : Lance le scraping sur les sources actives.
    
    Paramètre optionnel :
    - source_id : Si fourni, scrape uniquement cette source (pour l'admin manuel)
    - Si None, scrape TOUTES les sources actives (pour Celery Beat automatique)
    """
    
    #  Si un source_id est passé, on ne scrape que cette source
    if source_id:
        sources = SourceScraping.objects.filter(id=source_id, est_actif=True)
        logger.info(f" Scraping manuel demandé pour source ID {source_id}")
    else:
        # 🔹 Sinon, on scrape toutes les sources actives (mode automatique)
        sources = SourceScraping.objects.filter(est_actif=True)
        logger.info(" Scraping automatique : toutes les sources actives")
    
    total_new = 0
    total_updated = 0

    for source in sources:
        try:
            logger.info(f"🕷️ Scraping source : {source.nom} ({source.url_racine})")
            
            # =================================================================
            # ÉTAPE 1 : Sélection du parser via le registre (avec normalisation d'URL)
            # =================================================================
            #  Normaliser l'URL : retirer les paramètres (?q=...) pour la comparaison
            # Ex: "https://site.com/page/?q=test" → "https://site.com/page/"
            parsed = urlparse(source.url_racine)
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
            
            #  Chercher le parser avec l'URL normalisée
            parser_class = PARSER_REGISTRY.get(base_url)
            
            #  Fallback vers le parser par défaut si non trouvé
            if not parser_class:
                logger.warning(f" Aucun parser pour {base_url} (URL source: {source.url_racine})")
                parser_class = PARSER_REGISTRY.get("default")
            
            #  Si toujours rien, passer à la source suivante
            if not parser_class:
                logger.warning(f" Aucun parser configuré ni par défaut pour {source.url_racine}")
                continue
            
            # =================================================================
            # ÉTAPE 2 : Exécution du scraping via le parser sélectionné
            # =================================================================
            scraper = parser_class(source.url_racine)
            raw_offres = scraper.run()

            # =================================================================
            # ÉTAPE 3 : Insertion/Mise à jour en base (anti-doublons)
            # =================================================================
            for data in raw_offres:
                #  CDC Section 3 : On ignore les offres sans lien source officiel
                if not data.get("url_tdr"):
                    continue

                #  update_or_create = "upsert" Django (anti-doublons par url_tdr)
                obj, created = AppelOffre.objects.update_or_create(
                    url_tdr=data["url_tdr"],
                    defaults={
                        "titre": data["titre"],
                        "organisme": data["organisme"],
                        "description": data["description"][:500],  # CDC: résumé court
                        "pays": "BF",
                        "date_publication": data["date_publication"] or timezone.now().date(),
                        "date_cloture": data["date_cloture"],
                        "mode_acquisition": "AUTO",  # Marque l'origine automatique
                        "source_origine": source,    # Lien vers la config de la source
                        "statut": "Ouvert"
                    }
                )
                
                # Mise à jour des compteurs
                if created:
                    total_new += 1
                    logger.debug(f" Nouvelle offre créée : {data['titre']}")
                else:
                    total_updated += 1
                    logger.debug(f" Offre mise à jour : {data['titre']}")

            # =================================================================
            # ÉTAPE 4 : Mise à jour du timestamp de dernier scraping
            # =================================================================
            source.last_scraped = timezone.now()
            source.save(update_fields=["last_scraped"])  # Optimisation : ne sauve que ce champ
            logger.info(f" Source {source.nom} traitée avec succès")

        except Exception as e:
            #  Gestion d'erreur : log + retry automatique via Celery
            logger.error(f" Échec scraping source {source.nom} : {type(e).__name__} - {e}")
            # self.retry() relance la tâche après delay, jusqu'à max_retries
            raise self.retry(exc=e)

    #  Rapport final de l'exécution
    logger.info(f" Scraping terminé | Nouvelles: {total_new} | Mises à jour: {total_updated}")
    
    # La valeur de retour est stockée dans le backend de résultats (django-db)
    return {"new": total_new, "updated": total_updated, "sources_processed": len(sources)}


# =============================================================================
# TÂCHE 2 : ARCHIVAGE AUTOMATIQUE DES OFFRES CLÔTURÉES
# =============================================================================
@shared_task
def daily_archive_task():
    """
     CDC Module 2 - Cycle de vie des offres
    
    Exécutée quotidiennement par Celery Beat.
    Détecte les offres dont date_cloture < aujourd'hui et change leur statut à "Clôturé".
    
    Retourne : nombre d'offres archivées
    """
    logger.info(" Démarrage de l'archivage automatique des offres clôturées...")
    
    # Délègue à la fonction utilitaire (déjà testée et isolée)
    count = archive_expired_offres()
    
    logger.info(f" Archivage terminé : {count} offres mises à jour")
    return {"archived": count}


# =============================================================================
# TÂCHE 3 : MATCHING OFFRES ↔ CRITÈRES EXPERTS + NOTIFICATIONS EMAIL
# =============================================================================
@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def daily_alert_matching_task(self):
    """
     CDC Module 4 - Notifications personnalisées
    
    Exécutée quotidiennement. Pour chaque expert avec alerte_active=True :
    1. Récupère ses mots-clés de recherche
    2. Scanne les offres publiées < 24h
    3. Si correspondance → envoie un email + enregistre dans Notification
    
    Paramètres :
    - bind=True + retry → Gestion robuste des échecs SMTP temporaires
    """
    try:
        logger.info(" Démarrage du matching offres ↔ critères experts...")
        
        # Délègue au service de notifications (logique métier isolée)
        count = check_and_notify_matches()
        
        logger.info(f" Matching terminé : {count} experts notifiés par email")
        return {"notified_experts": count}
        
    except Exception as e:
        # En cas d'échec (ex: SMTP indisponible), on réessaie après 60s
        logger.error(f" Erreur lors du matching : {type(e).__name__} - {e}")
        raise self.retry(exc=e)