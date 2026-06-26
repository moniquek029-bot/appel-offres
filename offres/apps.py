from django.apps import AppConfig


class OffresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'offres'

    def ready(self):
        # ✅ Import des tâches Celery (après chargement des apps)
        try:
            import offres.tasks  # noqa: F401
        except ImportError as e:
            print(f"⚠️ Erreur import tasks: {e}")
        
        # ✅ Import des signaux
        try:
            import offres.signals  # noqa: F401
        except ImportError as e:
            print(f"️ Erreur import signals: {e}")