# offres/tasks.py
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def test_task():
    """Tâche de test simple."""
    logger.info(" Tâche de test exécutée !")
    return " Test OK"


#  Pour importer les tâches de scraping, faites-le DANS une fonction, pas au niveau module :
def register_scraping_tasks():
    """Enregistre les tâches de scraping (appelé après chargement Django)."""
    try:
        from offres.scraping.tasks import (
            run_scheduled_scraping_task,
            daily_archive_task,
            daily_alert_matching_task,
        )
        return True
    except ImportError as e:
        logger.warning(f" Import scraping tasks : {e}")
        return False