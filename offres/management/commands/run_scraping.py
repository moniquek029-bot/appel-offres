# offres/management/commands/run_scraping.py
"""
Commande personnalisée pour lancer le scraping
Usage: python manage.py run_scraping [--source-id ID] [--verbose]
"""

from django.core.management.base import BaseCommand
from offres.scraping.tasks import run_scheduled_scraping_task
from offres.models import SourceScraping
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Lance le scraping des appels d\'offres'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source-id',
            type=int,
            help='ID de la source à scraper (par défaut: toutes les sources actives)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Affiche plus de détails'
        )

    def handle(self, *args, **options):
        source_id = options.get('source-id')
        verbose = options.get('verbose', False)
        
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        self.stdout.write("=" * 60)
        self.stdout.write("🚀 LANCEMENT DU SCRAPING")
        self.stdout.write("=" * 60)
        
        if source_id:
            # Scraper une source spécifique
            source = SourceScraping.objects.filter(id=source_id, est_actif=True).first()
            if not source:
                self.stdout.write(self.style.ERROR(f"❌ Source ID {source_id} non trouvée ou inactive"))
                return
            
            self.stdout.write(f"\n📡 Source: {source.nom}")
            self.stdout.write(f"   URL: {source.url_racine}")
            
            try:
                result = run_scheduled_scraping_task(source_id=source.id)
                self.stdout.write(self.style.SUCCESS(f"✅ Scraping terminé !"))
                self.stdout.write(f"   - Nouvelles offres: {result.get('new', 0)}")
                self.stdout.write(f"   - Offres mises à jour: {result.get('updated', 0)}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Erreur: {e}"))
        else:
            # Scraper toutes les sources actives
            sources = SourceScraping.objects.filter(est_actif=True)
            if not sources.exists():
                self.stdout.write(self.style.WARNING("⚠️ Aucune source active trouvée"))
                return
            
            self.stdout.write(f"\n📡 {sources.count()} source(s) active(s)")
            
            total_new = 0
            total_updated = 0
            
            for source in sources:
                self.stdout.write(f"\n   - {source.nom}")
                try:
                    result = run_scheduled_scraping_task(source_id=source.id)
                    total_new += result.get('new', 0)
                    total_updated += result.get('updated', 0)
                    self.stdout.write(f"     ✅ {result.get('new', 0)} nouvelles, {result.get('updated', 0)} mises à jour")
                except Exception as e:
                    self.stdout.write(f"     ❌ Erreur: {e}")
            
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(self.style.SUCCESS("📊 RÉSULTAT FINAL"))
            self.stdout.write("=" * 60)
            self.stdout.write(f"   ✅ Nouvelles offres: {total_new}")
            self.stdout.write(f"   🔄 Offres mises à jour: {total_updated}")
        
        self.stdout.write("\n" + "=" * 60)