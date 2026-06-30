# offres/management/commands/update_existing_pdfs.py
"""
Commande pour mettre à jour les PDF des offres existantes
Utilisation: python manage.py update_existing_pdfs
"""

from django.core.management.base import BaseCommand
from offres.models import AppelOffre
from offres.scraping.utils import fetch_and_validate_pdf, download_pdf_file
from offres.scraping.extraction_helpers import extract_pdf_url
import requests
from bs4 import BeautifulSoup
import logging
import time
from django.core.files.base import ContentFile
import os

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Met à jour les PDF des offres existantes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Limite le nombre d\'offres à traiter (ex: --limit=10)'
        )
        parser.add_argument(
            '--offre-id',
            type=int,
            help='Traite une seule offre spécifique (ex: --offre-id=123)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force le retéléchargement même si un PDF existe déjà'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les offres qui seraient traitées sans les modifier'
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        force = options.get('force', False)
        limit = options.get('limit', 0)
        offre_id = options.get('offre_id')

        self.stdout.write("=" * 60)
        self.stdout.write("📄 MISE À JOUR DES PDF DES OFFRES EXISTANTES")
        self.stdout.write("=" * 60)

        # Construire la requête
        queryset = AppelOffre.objects.all()

        # Si force=False, ne traiter que les offres sans PDF
        if not force:
            queryset = queryset.filter(
                fichier_pdf__isnull=True,
                url_source__isnull=False
            )
        else:
            self.stdout.write(self.style.WARNING("⚠️ Mode FORCE: retéléchargement de TOUS les PDF"))

        if offre_id:
            queryset = queryset.filter(id=offre_id)
            if not queryset.exists():
                self.stdout.write(self.style.ERROR(f"❌ Offre ID {offre_id} non trouvée"))
                return

        if limit > 0:
            queryset = queryset[:limit]

        total = queryset.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS("✅ Aucune offre à traiter"))
            return

        self.stdout.write(f"📊 {total} offre(s) à traiter")
        self.stdout.write("")

        success_count = 0
        fail_count = 0
        skip_count = 0

        for i, offre in enumerate(queryset, 1):
            self.stdout.write(f"[{i}/{total}] 📄 Traitement: {offre.titre[:60]}...")

            if dry_run:
                self.stdout.write(f"   🔍 URL source: {offre.url_source}")
                self.stdout.write(f"   📎 URL TDR actuel: {offre.url_tdr or 'Aucun'}")
                self.stdout.write(f"   💾 PDF local: {'Oui' if offre.fichier_pdf else 'Non'}")
                self.stdout.write("   ⏭️ DRY RUN - Aucune modification")
                self.stdout.write("")
                continue

            # Vérifier si le PDF existe déjà
            if offre.fichier_pdf and not force:
                self.stdout.write(self.style.WARNING(f"   ⏭️ PDF déjà existant (utiliser --force pour forcer)"))
                skip_count += 1
                self.stdout.write("")
                continue

            # Récupérer la page de détail
            try:
                self.stdout.write(f"   🌐 Récupération de: {offre.url_source[:60]}...")

                response = requests.get(offre.url_source, timeout=30, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })

                if response.status_code != 200:
                    self.stdout.write(self.style.ERROR(f"   ❌ Erreur HTTP {response.status_code}"))
                    fail_count += 1
                    self.stdout.write("")
                    continue

                soup = BeautifulSoup(response.content, 'html.parser')

                # ✅ Extraire le PDF de la page
                pdf_url = extract_pdf_url(soup, offre.url_source)

                if pdf_url:
                    self.stdout.write(f"   📎 PDF trouvé: {pdf_url[:80]}...")

                    # Télécharger le PDF
                    pdf_content = fetch_and_validate_pdf(pdf_url, offre.titre)

                    if pdf_content:
                        # Générer un nom de fichier
                        import uuid
                        import re
                        safe_title = re.sub(r'[^a-zA-Z0-9]', '_', offre.titre[:50]) if offre.titre else 'document'
                        filename = f"tdr_{offre.id}_{safe_title}_{uuid.uuid4().hex[:8]}.pdf"

                        # Sauvegarder le PDF
                        offre.fichier_pdf.save(filename, ContentFile(pdf_content), save=True)

                        # Mettre à jour l'URL TDR si différente
                        if offre.url_tdr != pdf_url:
                            offre.url_tdr = pdf_url
                            offre.save(update_fields=['url_tdr'])

                        success_count += 1
                        self.stdout.write(self.style.SUCCESS(f"   ✅ PDF téléchargé avec succès"))
                    else:
                        # Fallback: utiliser l'URL source
                        self.stdout.write(self.style.WARNING(f"   ⚠️ PDF non valide, utilisation de l'URL source"))
                        if not offre.url_tdr or offre.url_tdr == offre.url_source:
                            offre.url_tdr = offre.url_source
                            offre.save(update_fields=['url_tdr'])
                        fail_count += 1
                else:
                    # ✅ Fallback: URL source
                    self.stdout.write(self.style.WARNING(f"   📄 Aucun PDF trouvé, utilisation de l'URL source"))
                    if not offre.url_tdr or offre.url_tdr == offre.url_source:
                        offre.url_tdr = offre.url_source
                        offre.save(update_fields=['url_tdr'])
                    fail_count += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Erreur: {str(e)[:80]}"))
                fail_count += 1

            self.stdout.write("")
            time.sleep(1)

        # Résumé final
        self.stdout.write("=" * 60)
        self.stdout.write("📊 RÉSULTAT FINAL")
        self.stdout.write("=" * 60)
        self.stdout.write(f"   ✅ Succès: {success_count}")
        self.stdout.write(f"   ❌ Échecs: {fail_count}")
        self.stdout.write(f"   ⏭️ Ignorés: {skip_count}")
        self.stdout.write(f"   📦 Total: {total}")

        if not dry_run:
            # Afficher le nouveau total de PDF
            total_pdf = AppelOffre.objects.exclude(fichier_pdf__isnull=True).count()
            self.stdout.write("")
            self.stdout.write(f" Offres avec PDF local: {total_pdf}")
            self.stdout.write(f" Offres sans PDF: {AppelOffre.objects.filter(fichier_pdf__isnull=True).count()}")