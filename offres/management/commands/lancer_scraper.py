from django.core.management.base import BaseCommand
from offres.scraping.tasks import votre_fonction_de_scrapping  # ⚠️ Remplacez par le vrai nom de votre fonction

class Command(BaseCommand):
    help = 'Lance le scraping manuellement'

    def handle(self, *args, **kwargs):
        self.stdout.write('🚀 Démarrage du scraping...')
        try:
            # Appelez votre fonction de scraping directement (sans .delay())
            resultat = votre_fonction_de_scrapping() 
            self.stdout.write(self.style.SUCCESS(f'✅ Scraping terminé ! {resultat} offres trouvées.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur lors du scraping : {e}'))