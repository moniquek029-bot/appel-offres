# offres/management/commands/update_tdr_urls.py
from django.core.management.base import BaseCommand
from django.db import models  # ✅ AJOUT DE L'IMPORT
from offres.models import AppelOffre
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Met à jour les URL TDR des offres existantes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les modifications sans les appliquer',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force la mise à jour sans confirmation',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        force = options.get('force', False)
        
        self.stdout.write("🔍 Recherche des offres sans URL TDR valide...")
        
        # Récupérer les offres sans url_tdr ou avec url_tdr vide
        offres_a_mettre_a_jour = AppelOffre.objects.filter(
            models.Q(url_tdr__isnull=True) | models.Q(url_tdr='')
        )
        
        count = offres_a_mettre_a_jour.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS("✅ Toutes les offres ont déjà une URL TDR !"))
            return
        
        self.stdout.write(f"📊 {count} offres à mettre à jour")
        
        if dry_run:
            self.stdout.write("\n📋 Liste des offres qui seront mises à jour :")
            for offre in offres_a_mettre_a_jour[:20]:
                self.stdout.write(f"  - {offre.titre[:50]}...")
                self.stdout.write(f"    URL source: {offre.url_source}")
                self.stdout.write(f"    Actuel: {offre.url_tdr or 'Aucune'}")
                self.stdout.write()
            if count > 20:
                self.stdout.write(f"  ... et {count - 20} autres offres")
            return
        
        if not force:
            confirm = input(f"\n⚠️ Mettre à jour {count} offres avec leur URL source ? (oui/non) : ")
            if confirm.lower() != 'oui':
                self.stdout.write(self.style.WARNING("❌ Opération annulée."))
                return
        
        self.stdout.write("\n🔄 Mise à jour en cours...")
        
        updated_count = 0
        for offre in offres_a_mettre_a_jour:
            # Si l'URL source existe, l'utiliser comme URL TDR
            if offre.url_source:
                offre.url_tdr = offre.url_source
                offre.save(update_fields=['url_tdr'])
                updated_count += 1
                
                if updated_count % 10 == 0:
                    self.stdout.write(f"   {updated_count}/{count} mises à jour...")
        
        self.stdout.write(
            self.style.SUCCESS(f"\n✅ {updated_count} offres mises à jour avec succès !")
        )
        
        # Afficher le résultat
        self.stdout.write("\n📊 RÉSULTAT FINAL :")
        total_avec_tdr = AppelOffre.objects.exclude(url_tdr__isnull=True).exclude(url_tdr='').count()
        total_sans_tdr = AppelOffre.objects.filter(models.Q(url_tdr__isnull=True) | models.Q(url_tdr='')).count()
        self.stdout.write(f"  - Offres avec URL TDR: {total_avec_tdr}")
        self.stdout.write(f"  - Offres sans URL TDR: {total_sans_tdr}")