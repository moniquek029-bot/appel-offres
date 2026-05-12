# plateforme_offres/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_offres.settings')

app = Celery('plateforme_offres')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découverte automatique des tâches dans les apps Django
app.autodiscover_tasks()

