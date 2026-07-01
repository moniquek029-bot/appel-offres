# offres/management/commands/correct_existing_dates.py
"""
Correction des dates des offres existantes
Usage: python manage.py correct_existing_dates
"""

from django.core.management.base import BaseCommand
from offres.models import AppelOffre
from offres.scraping.extraction_helpers import extract_publication_date_from_text, extract_deadline_from_text
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Corrige les dates des offres existantes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--offre-id',
            type=int,
            help='Corriger une offre spécifique'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les modifications sans les appliquer'
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        offre_id = options.get('offre_id')

        queryset = AppelOffre.objects.all()
        if offre_id:
            queryset = queryset.filter(id=offre_id)

        total = queryset.count()
        self.stdout.write(f"📊 {total} offres à vérifier")

        corrected = 0
        for offre in queryset:
            try:
                # Récupérer la page source
                response = requests.get(offre.url_source, timeout=30)
                if response.status_code != 200:
                    self.stdout.write(f"   ⚠️ {offre.titre[:30]}... - HTTP {response.status_code}")
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')
                texte = soup.get_text()[:5000]

                # Extraire les dates
                pub_date = extract_publication_date_from_text(texte)
                deadline = extract_deadline_from_text(texte)

                corrections = []
                if pub_date and pub_date != offre.date_publication:
                    corrections.append(f"publication {offre.date_publication} → {pub_date}")
                    if not dry_run:
                        offre.date_publication = pub_date

                if deadline and deadline != offre.date_cloture:
                    corrections.append(f"clôture {offre.date_cloture} → {deadline}")
                    if not dry_run:
                        offre.date_cloture = deadline

                if corrections:
                    self.stdout.write(f"   ✏️ {offre.titre[:30]}...")
                    for corr in corrections:
                        self.stdout.write(f"      - {corr}")
                    if not dry_run:
                        offre.save(update_fields=['date_publication', 'date_cloture'])
                        corrected += 1

            except Exception as e:
                self.stdout.write(f"   ❌ {offre.titre[:30]}... - {str(e)[:50]}")

        self.stdout.write(f"\n✅ {corrected} offres corrigées")