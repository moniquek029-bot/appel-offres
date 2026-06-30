# offres/management/commands/fix_offres.py
"""
Correction complète des offres existantes
- Supprime les offres qui ne sont pas des appels d'offres
- Corrige les dates des offres
- Met à jour les types
"""

from django.core.management.base import BaseCommand
from offres.models import AppelOffre
from offres.utils.search_keywords import est_appel_offres, detecter_type_offre
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Corrige les offres existantes (suppression des non-AO, correction des dates)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les modifications sans les appliquer'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force la suppression sans confirmation'
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        force = options.get('force', False)

        self.stdout.write("=" * 60)
        self.stdout.write("🔧 CORRECTION DES OFFRES EXISTANTES")
        self.stdout.write("=" * 60)

        # ============================================================
        # 1. IDENTIFIER LES OFFRES À SUPPRIMER (NON APPELS D'OFFRES)
        # ============================================================
        self.stdout.write("\n🔍 Identification des offres à supprimer...")

        offres_a_supprimer = []
        mots_cles_non_ao = [
            'javni poziv', 'call for proposal', 'appel à projets', 'appel à projet',
            'expression of interest', 'manifestation d\'intérêt',
            'car sale', 'vente de voiture', 'auction',
            'analysis of social protection', 'social protection gaps',
            'recrutement', 'recruitment', 'consultant', 'bureau d\'etudes',
            'opportunité', 'opportunity', 'emploi', 'job'
        ]

        for offre in AppelOffre.objects.all():
            titre_lower = offre.titre.lower()
            est_non_ao = False

            # Vérifier par mots-clés
            for mot in mots_cles_non_ao:
                if mot in titre_lower:
                    est_non_ao = True
                    break

            # Vérifier par type_offre
            if hasattr(offre, 'type_offre'):
                if offre.type_offre in ['APPEL_A_PROJETS', 'MANIFESTATION_INTERET', 
                                        'VENTE_AUX_ENCHERES', 'RECRUTEMENT', 'AUTRE']:
                    est_non_ao = True

            # Vérifier par est_appel_offres()
            if not est_non_ao:
                if not est_appel_offres(offre.titre, offre.description or ''):
                    est_non_ao = True

            if est_non_ao:
                offres_a_supprimer.append(offre)

        total_a_supprimer = len(offres_a_supprimer)

        if total_a_supprimer > 0:
            self.stdout.write(f"\n📊 {total_a_supprimer} offres à supprimer :")
            for offre in offres_a_supprimer[:20]:
                type_offre = getattr(offre, 'type_offre', 'Non défini')
                self.stdout.write(f"   - {offre.titre[:50]}... (Type: {type_offre})")
            if total_a_supprimer > 20:
                self.stdout.write(f"   ... et {total_a_supprimer - 20} autres")

        # ============================================================
        # 2. CORRIGER LES DATES DES OFFRES VALIDES
        # ============================================================
        self.stdout.write("\n🔍 Vérification des dates...")

        offres_corrigees = []
        offres_conservees = []

        for offre in AppelOffre.objects.all():
            if offre in offres_a_supprimer:
                continue

            # Vérifier si les dates sont cohérentes
            if offre.date_publication > offre.date_cloture:
                offres_corrigees.append({
                    'offre': offre,
                    'problème': 'date_publication > date_cloture',
                    'ancien': f"{offre.date_publication} → {offre.date_cloture}"
                })
                # Inverser les dates
                offre.date_publication, offre.date_cloture = offre.date_cloture, offre.date_publication
                offre.save(update_fields=['date_publication', 'date_cloture'])
                continue

            # Vérifier si date_publication est aujourd'hui (scraping) mais devrait être plus ancienne
            if offre.date_publication == offre.date_scraping.date():
                # Vérifier si l'offre a une date de publication dans le titre ou description
                import re
                from datetime import datetime

                texte = f"{offre.titre} {offre.description or ''}"
                # Chercher une date au format JJ/MM/AAAA ou JJ Mois AAAA
                patterns = [
                    r'(\d{2})[/\-](\d{2})[/\-](\d{4})',
                    r'(\d{2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})',
                    r'Posted\s*[:;]\s*(\d{2})[/\-](\d{2})[/\-](\d{4})',
                    r'Published\s*[:;]\s*(\d{2})[/\-](\d{2})[/\-](\d{4})',
                    r'Date\s+limite\s*[:;]\s*(\d{2})[/\-](\d{2})[/\-](\d{4})',
                ]

                mois_fr = {'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
                          'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12}

                nouvelle_date = None

                for pattern in patterns:
                    match = re.search(pattern, texte, re.IGNORECASE)
                    if match:
                        groups = match.groups()
                        if len(groups) == 3:
                            if groups[0].isdigit() and groups[1].isdigit() and groups[2].isdigit():
                                day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
                            else:
                                day = int(groups[0])
                                month = mois_fr.get(groups[1].lower(), 1)
                                year = int(groups[2])
                            try:
                                nouvelle_date = datetime(year, month, day).date()
                                break
                            except ValueError:
                                pass

                if nouvelle_date and nouvelle_date < offre.date_scraping.date():
                    offres_corrigees.append({
                        'offre': offre,
                        'problème': 'date_publication = date_scraping',
                        'ancien': f"{offre.date_publication} → {nouvelle_date}"
                    })
                    offre.date_publication = nouvelle_date
                    offre.save(update_fields=['date_publication'])

        # ============================================================
        # 3. SUPPRESSION DES OFFRES NON-AO
        # ============================================================
        if total_a_supprimer > 0:
            if not dry_run:
                if not force:
                    confirm = input(f"\n🗑️ Supprimer {total_a_supprimer} offres non-appels d'offres ? (oui/non) : ")
                    if confirm.lower() != 'oui':
                        self.stdout.write(self.style.WARNING("❌ Suppression annulée."))
                        return

                self.stdout.write("\n🗑️ Suppression en cours...")
                deleted_count = 0
                for offre in offres_a_supprimer:
                    if offre.fichier_pdf:
                        try:
                            offre.fichier_pdf.delete(save=False)
                        except:
                            pass
                    offre.delete()
                    deleted_count += 1
                    if deleted_count % 5 == 0:
                        self.stdout.write(f"   {deleted_count}/{total_a_supprimer} supprimées...")

                self.stdout.write(self.style.SUCCESS(f"\n✅ {deleted_count} offres supprimées"))

        # ============================================================
        # 4. RÉSULTAT FINAL
        # ============================================================
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("📊 RÉSULTAT FINAL")
        self.stdout.write("=" * 60)

        if dry_run:
            self.stdout.write(self.style.WARNING(f"\n⚠️ DRY RUN - Aucune modification appliquée"))
            self.stdout.write(f"   - Offres à supprimer: {total_a_supprimer}")
            self.stdout.write(f"   - Offres à corriger: {len(offres_corrigees)}")

        else:
            total_restant = AppelOffre.objects.count()
            self.stdout.write(f"\n📊 Total offres restantes: {total_restant}")

            if total_restant > 0:
                self.stdout.write("\n📋 Répartition des offres restantes:")
                from django.db.models import Count
                repartition = AppelOffre.objects.values('type_offre').annotate(
                    total=Count('id')
                ).order_by('-total')

                type_choices = dict(AppelOffre.TYPE_OFFRE_CHOICES)
                for d in repartition:
                    type_nom = type_choices.get(d['type_offre'], d['type_offre'])
                    self.stdout.write(f"   - {type_nom}: {d['total']}")

        self.stdout.write("\n✅ Terminé !")