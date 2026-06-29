# offres/management/commands/scraper.py
from django.core.management.base import BaseCommand
from offres.scraping.orchestrator import ScrapingOrchestrator


class Command(BaseCommand):
    help = 'Lance le scraping de toutes les sources actives'
    
    def add_arguments(self, parser):
        parser.add_argument('--source', type=str, help='Nom de la source à scraper')
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🕷️  LANCEMENT DU SCRAPING\n'))
        
        orchestrator = ScrapingOrchestrator()
        source_filter = options.get('source')
        
        results = orchestrator.run_all_sources(source_name=source_filter)
        
        self.stdout.write(self.style.SUCCESS('\n📊 RÉSUMÉ FINAL'))
        total = 0
        for source_name, result in results.items():
            saved = result.get('saved', 0)
            expired = result.get('expired_rejected', 0)
            total += saved
            self.stdout.write(f"✅ {source_name}: {saved} offres ({expired} expirées)")
        
        self.stdout.write(self.style.SUCCESS(f'\n📈 Total : {total} offres sauvegardées\n'))