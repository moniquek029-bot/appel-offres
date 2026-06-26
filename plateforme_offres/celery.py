# plateforme_offres/celery.py
import os
from celery import Celery
from celery.schedules import crontab
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_offres.settings')

app = Celery('plateforme_offres')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

app.conf.beat_schedule = {
    # Alertes critères : tous les jours à 8h
    'send-matching-alerts-daily': {
        'task': 'offres.tasks.send_matching_alerts_task',
        'schedule': crontab(hour=8, minute=0),
    },
}