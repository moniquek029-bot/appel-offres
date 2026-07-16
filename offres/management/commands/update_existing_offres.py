# offres/management/commands/update_existing_offres.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from offres.models import AppelOffre
from offres.scraping.country_detector import detecter_pays_smart
from offres.scraping.extraction_helpers import (
    extract_publication_date_from_text,
    extract_deadline_from_text,
    parse_date_universelle,
)
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Met à jour les offres existantes avec pays et dates corrigés'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Nombre maximum d\'offres à traiter (0 = toutes)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simuler sans sauvegarder',
        )

    def handle(self, *args, **options):
        limit = options['limit']
        dry_run = options['dry_run']
        
        # Récupérer les offres avec URL source non vide
        offres = AppelOffre.objects.exclude(url_source__isnull=True).exclude(url_source__exact='')
        if limit > 0:
            offres = offres[:limit]
        
        total = offres.count()
        self.stdout.write(f"📊 {total} offres à traiter")
        
        updated_count = 0
        skipped_count = 0
        
        for offre in offres:
            self.stdout.write(f"\n🔍 Traitement offre #{offre.id}: {offre.titre[:50]}...")
            
            try:
                # Récupérer le contenu de la page source
                response = requests.get(offre.url_source, timeout=30, verify=False)
                if response.status_code != 200:
                    self.stdout.write(f"   ⚠️ Page inaccessible (HTTP {response.status_code})")
                    skipped_count += 1
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                texte_complet = soup.get_text(separator=' ')
                
                # 1. Re-détection du pays
                pays_old = offre.pays
                pays_new = detecter_pays_smart(
                    texte=texte_complet,
                    url=offre.url_source,
                    pays_defaut='BF'
                )
                
                # 2. Re-extraction des dates
                date_pub_old = offre.date_publication
                date_clot_old = offre.date_cloture
                
                # Date de publication
                date_pub_new = extract_publication_date_from_text(texte_complet)
                if date_pub_new and date_pub_new <= timezone.now().date():
                    pass
                else:
                    date_pub_new = None
                
                # Date de clôture
                date_clot_new = extract_deadline_from_text(texte_complet)
                
                # Si toujours pas de date, essayer de parse les dates existantes
                if not date_clot_new:
                    # Vérifier si la date existante est valide
                    if offre.date_cloture and offre.date_cloture >= timezone.now().date():
                        date_clot_new = offre.date_cloture
                    else:
                        # Fallback : prendre la date de publication + 30 jours
                        date_clot_new = (date_pub_new or timezone.now().date()) + timezone.timedelta(days=30)
                
                # 3. Vérifier les changements
                changes = []
                if pays_new != pays_old:
                    changes.append(f"pays: {pays_old} → {pays_new}")
                if date_pub_new and date_pub_new != date_pub_old:
                    changes.append(f"date_publication: {date_pub_old} → {date_pub_new}")
                if date_clot_new and date_clot_new != date_clot_old:
                    changes.append(f"date_cloture: {date_clot_old} → {date_clot_new}")
                
                if not changes:
                    self.stdout.write("   ✅ Aucun changement")
                    continue
                
                self.stdout.write(f"   📝 Changements: {', '.join(changes)}")
                
                if dry_run:
                    self.stdout.write("   🔄 [DRY RUN] Modifications non sauvegardées")
                    updated_count += 1
                    continue
                
                # Sauvegarder les modifications
                offre.pays = pays_new
                if date_pub_new:
                    offre.date_publication = date_pub_new
                if date_clot_new:
                    offre.date_cloture = date_clot_new
                offre.save()
                
                updated_count += 1
                self.stdout.write("   ✅ Sauvegardé")
                
            except Exception as e:
                self.stdout.write(f"   ❌ Erreur: {e}")
                skipped_count += 1
        
        self.stdout.write(f"\n🏁 Terminé | Mises à jour: {updated_count} | Ignorées: {skipped_count}")
        if dry_run:
            self.stdout.write("⚠️ Mode DRY RUN - aucune modification permanente")