# offres/management/commands/scraper.py
"""
Commande Django pour lancer le scraping de toutes les sources actives
Usage : python manage.py scraper [--source NOM] [--clean]
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date

from offres.scraping.orchestrator import ScrapingOrchestrator
from offres.models import AppelOffre


class Command(BaseCommand):
    help = 'Lance le scraping de toutes les sources actives'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            help='Nom de la source à scraper (ex: "UNDP", "AGETIB")',
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Nettoyer la base avant scraping (marquer offres expirées)',
        )
        parser.add_argument(
            '--update-domaines',
            action='store_true',
            help='Mettre à jour les domaines des offres existantes',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('🕷️  LANCEMENT DU SCRAPING'))
        self.stdout.write(self.style.SUCCESS('=' * 70 + '\n'))
        
        # Nettoyage optionnel
        if options['clean']:
            self._clean_expired_offers()
        
        # Mise à jour des domaines optionnelle
        if options['update_domaines']:
            self._update_domaines()
        
        # Lancer le scraping
        orchestrator = ScrapingOrchestrator()
        source_filter = options.get('source')
        
        try:
            results = orchestrator.run_all_sources(source_name=source_filter)
            
            # Résumé
            self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
            self.stdout.write(self.style.SUCCESS('📊 RÉSUMÉ FINAL'))
            self.stdout.write(self.style.SUCCESS('=' * 70))
            
            total_offres = 0
            total_expired = 0
            
            for source_name, result in results.items():
                offres = result.get('offres', [])
                expired = result.get('expired_rejected', 0)
                total_offres += len(offres)
                total_expired += expired
                
                status = self.style.SUCCESS('✅') if offres else self.style.WARNING('⚠️')
                self.stdout.write(f"{status} {source_name}: {len(offres)} offres ({expired} expirées rejetées)")
            
            self.stdout.write(self.style.SUCCESS(f'\n📈 Total : {total_offres} offres scrapées'))
            self.stdout.write(self.style.SUCCESS(f'⏰ Total offres expirées rejetées : {total_expired}'))
            self.stdout.write(self.style.SUCCESS('=' * 70 + '\n'))
            
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'\n❌ Erreur : {e}'))
            import traceback
            traceback.print_exc()
    
    def _clean_expired_offers(self):
        """Marque les offres expirées comme clôturées"""
        self.stdout.write('\n⏰ Nettoyage des offres expirées...')
        today = date.today()
        offres_expirees = AppelOffre.objects.filter(
            statut='Ouvert',
            date_cloture__lt=today
        )
        count = 0
        for offre in offres_expirees:
            offre.statut = 'Clôturé'
            offre.est_expire = True
            offre.save(update_fields=['statut', 'est_expire'])
            count += 1
        self.stdout.write(self.style.SUCCESS(f'✅ {count} offres marquées comme clôturées'))
    
    def _update_domaines(self):
        """Met à jour les domaines des offres existantes"""
        self.stdout.write('\n📊 Mise à jour des domaines...')
        from offres.scraping.constantes import detecter_domaine
        
        offres = AppelOffre.objects.all()
        count = 0
        for offre in offres:
            texte = f"{offre.titre} {offre.description or ''} {offre.organisme or ''}"
            domaine = detecter_domaine(texte)
            if offre.domaine != domaine:
                offre.domaine = domaine
                offre.save(update_fields=['domaine'])
                count += 1
        self.stdout.write(self.style.SUCCESS(f'✅ {count} domaines mis à jour'))