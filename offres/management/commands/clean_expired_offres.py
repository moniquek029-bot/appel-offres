# offres/management/commands/clean_expired_offres.py
"""
Supprime les offres expirées
Usage: python manage.py clean_expired_offres
"""

from django.core.management.base import BaseCommand
from offres.models import AppelOffre
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Supprime les offres expirées depuis plus de X jours'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Nombre de jours après expiration pour supprimer (défaut: 7)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les offres qui seraient supprimées sans les supprimer'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Supprime sans confirmation'
        )

    def handle(self, *args, **options):
        days = options.get('days', 7)
        dry_run = options.get('dry_run', False)
        force = options.get('force', False)
        
        cutoff_date = date.today() - timedelta(days=days)
        
        offres_a_supprimer = AppelOffre.objects.filter(
            statut='Expiré',
            date_cloture__lt=cutoff_date
        )
        
        count = offres_a_supprimer.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS("✅ Aucune offre expirée à supprimer"))
            return
        
        self.stdout.write(f"📊 {count} offres expirées depuis plus de {days} jours")
        
        if dry_run:
            self.stdout.write("\n📋 Offres qui seraient supprimées:")
            for offre in offres_a_supprimer[:10]:
                self.stdout.write(f"   - {offre.titre[:50]}... (clôture: {offre.date_cloture})")
            if count > 10:
                self.stdout.write(f"   ... et {count - 10} autres")
            return
        
        if not force:
            confirm = input(f"\n🗑️ Supprimer {count} offres ? (oui/non) : ")
            if confirm.lower() != 'oui':
                self.stdout.write("❌ Annulé")
                return
        
        deleted = 0
        for offre in offres_a_supprimer:
            if offre.fichier_pdf:
                try:
                    offre.fichier_pdf.delete(save=False)
                except:
                    pass
            offre.delete()
            deleted += 1
            
            if deleted % 10 == 0:
                self.stdout.write(f"   {deleted}/{count} supprimées...")
        
        self.stdout.write(self.style.SUCCESS(f"\n✅ {deleted} offres supprimées définitivement"))