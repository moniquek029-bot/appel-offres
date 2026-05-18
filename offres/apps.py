from django.apps import AppConfig
import offres.tasks  # Import explicite pour enregistrer les tâches Celery de l'app 'offres'


class OffresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'offres'

    def ready(self):
        import offres.signals  # Import des signaux
        pass
