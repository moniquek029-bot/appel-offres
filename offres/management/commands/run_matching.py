# offres/management/commands/run_matching.py
from django.core.management.base import BaseCommand
from offres.services.offre_matching import run_matching

class Command(BaseCommand):
    help = 'Exécute le matching des offres avec les critères des experts'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Lancement du matching...")
        result = run_matching()
        self.stdout.write(self.style.SUCCESS(f"✅ Terminé: {result}"))