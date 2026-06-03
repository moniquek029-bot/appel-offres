# offres/management/commands/retry_download_pdfs.py
"""
Commande Django personnalisée pour retélécharger les PDF manquants
Utilisation: python manage.py retry_download_pdfs
"""

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from offres.models import AppelOffre
from offres.scraping.utils import download_pdf_file
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Retente le téléchargement des PDF manquants pour les offres qui ont une URL TDR mais pas de PDF local'

    def add_arguments(self, parser):
        """Ajoute des arguments optionnels à la commande"""
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limite le nombre d\'offres à traiter (ex: --limit=10)'
        )
        parser.add_argument(
            '--offre-id',
            type=int,
            default=None,
            help='Traite une seule offre spécifique (ex: --offre-id=123)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force le retéléchargement même si un PDF existe déjà'
        )

    def handle(self, *args, **options):
        # Construction de la requête
        if options['force']:
            # Forcer le retéléchargement même si PDF existe
            offres = AppelOffre.objects.filter(url_tdr__isnull=False)
            self.stdout.write(self.style.WARNING("⚠️ Mode FORCE: retéléchargement de TOUS les PDF (même ceux existants)"))
        else:
            # Uniquement les offres sans PDF local
            offres = AppelOffre.objects.filter(
                url_tdr__isnull=False,
                fichier_pdf__isnull=True
            )
        
        # Filtrer par ID spécifique
        if options['offre_id']:
            offres = offres.filter(id=options['offre_id'])
            if not offres.exists():
                self.stdout.write(self.style.ERROR(f"❌ Offre ID {options['offre_id']} non trouvée"))
                return
        
        # Appliquer la limite
        if options['limit']:
            offres = offres[:options['limit']]
        
        total = offres.count()
        
        if total == 0:
            self.stdout.write(self.style.SUCCESS("✅ Aucune offre à traiter"))
            return
        
        self.stdout.write(f"📊 {total} offre(s) à traiter")
        self.stdout.write("=" * 50)
        
        success_count = 0
        fail_count = 0
        skip_count = 0
        
        for idx, offre in enumerate(offres, 1):
            self.stdout.write(f"\n[{idx}/{total}] 📥 Traitement: {offre.titre[:60]}...")
            
            # Vérifier si le PDF existe déjà
            if offre.fichier_pdf and not options['force']:
                self.stdout.write(self.style.WARNING(f"  ⏭️ PDF déjà existant (ignore --force pour forcer)"))
                skip_count += 1
                continue
            
            self.stdout.write(f"  🔗 URL TDR: {offre.url_tdr[:80]}...")
            
            # Tenter le téléchargement
            pdf_file = download_pdf_file(offre.url_tdr, offre.titre)
            
            if pdf_file:
                offre.fichier_pdf = pdf_file
                offre.save(update_fields=['fichier_pdf'])
                success_count += 1
                self.stdout.write(self.style.SUCCESS(f"  ✅ PDF téléchargé avec succès"))
            else:
                fail_count += 1
                self.stdout.write(self.style.ERROR(f"  ❌ Échec du téléchargement"))
        
        # Résumé final
        self.stdout.write("")
        self.stdout.write("=" * 50)
        self.stdout.write(self.style.SUCCESS(
            f"\n📊 RÉSULTAT FINAL:\n"
            f"   ✅ Succès: {success_count}\n"
            f"   ❌ Échecs: {fail_count}\n"
            f"   ⏭️ Ignorés: {skip_count}\n"
            f"   📦 Total: {total}"
        ))
        
        # Retourner un code d'erreur si des échecs
        if fail_count > 0:
            return 1
        return 0