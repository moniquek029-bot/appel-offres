# offres/management/commands/update_offre_dates.py
"""
Mettre à jour les dates des offres existantes en utilisant la nouvelle extraction
Usage: python manage.py update_offre_dates
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from offres.models import AppelOffre
from offres.scraping.extraction_helpers import (
    extract_publication_date_from_text,
    extract_deadline_from_text
)
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Met à jour les dates des offres existantes (publication et clôture)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source-id',
            type=int,
            help='Mettre à jour uniquement les offres d\'une source spécifique'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Limiter le nombre d\'offres à traiter'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simuler sans modifier la base'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer la mise à jour même si les dates semblent correctes'
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        force = options.get('force', False)
        source_id = options.get('source-id')
        limit = options.get('limit', 0)

        # Construction du queryset
        queryset = AppelOffre.objects.all()
        if source_id:
            queryset = queryset.filter(source_origine_id=source_id)

        # Optionnellement, ne traiter que les offres sans URL source (au cas où)
        queryset = queryset.exclude(url_source__isnull=True).exclude(url_source='')

        total = queryset.count()
        if limit > 0:
            queryset = queryset[:limit]

        if total == 0:
            self.stdout.write(self.style.WARNING("⚠️ Aucune offre à traiter"))
            return

        self.stdout.write(f"📊 {total} offres à vérifier")
        self.stdout.write("=" * 60)

        updated = 0
        skipped = 0
        errors = 0

        for idx, offre in enumerate(queryset, 1):
            self.stdout.write(f"\n[{idx}/{total}] 📄 {offre.titre[:50]}...")

            # Récupérer la page de détail
            try:
                response = requests.get(offre.url_source, timeout=30, verify=False)
                if response.status_code != 200:
                    self.stdout.write(f"   ⚠️ HTTP {response.status_code} - ignorée")
                    skipped += 1
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')
                texte = soup.get_text()

                # Extraire les dates
                new_pub = extract_publication_date_from_text(texte)
                new_deadline = extract_deadline_from_text(texte)

                # Afficher les changements
                changes = []
                if new_pub and new_pub != offre.date_publication:
                    changes.append(f"publication {offre.date_publication} → {new_pub}")
                if new_deadline and new_deadline != offre.date_cloture:
                    changes.append(f"clôture {offre.date_cloture} → {new_deadline}")

                if not changes:
                    self.stdout.write("   ✅ Dates déjà correctes")
                    skipped += 1
                    continue

                if dry_run:
                    self.stdout.write(f"   🔄 (simulation) {', '.join(changes)}")
                    updated += 1
                    continue

                # Appliquer les modifications
                if new_pub:
                    offre.date_publication = new_pub
                if new_deadline:
                    offre.date_cloture = new_deadline

                # Marquer comme expirée si la clôture est passée
                if new_deadline and new_deadline < timezone.now().date():
                    if offre.statut != 'Expiré':
                        offre.statut = 'Expiré'
                        self.stdout.write(f"   ⏭️ Marquée comme expirée")

                offre.save(update_fields=['date_publication', 'date_cloture', 'statut'])
                updated += 1
                self.stdout.write(f"   ✅ Mise à jour: {', '.join(changes)}")

            except Exception as e:
                self.stdout.write(f"   ❌ Erreur: {str(e)[:60]}")
                errors += 1

        # Bilan
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("📊 RÉSULTAT FINAL")
        self.stdout.write("=" * 60)
        self.stdout.write(f"   ✅ Mises à jour: {updated}")
        self.stdout.write(f"   ⏭️ Ignorées: {skipped}")
        self.stdout.write(f"   ❌ Erreurs: {errors}")
        self.stdout.write(f"   📦 Total traitées: {updated + skipped + errors}")