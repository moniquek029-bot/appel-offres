# offres/management/commands/delete_non_tenders.py
from django.core.management.base import BaseCommand
from django.db.models import Q
from offres.models import AppelOffre
from offres.utils.search_keywords import est_appel_offres

class Command(BaseCommand):
    help = 'Supprime toutes les offres qui ne sont pas des appels d\'offres'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les offres qui seraient supprimées sans les supprimer',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Supprime sans demander confirmation',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        force = options.get('force', False)
        
        self.stdout.write("🔍 Recherche des offres qui ne sont pas des appels d'offres...")
        
        # Récupérer toutes les offres
        toutes_offres = AppelOffre.objects.all()
        
        # Identifier les offres qui ne sont PAS des appels d'offres
        offres_a_supprimer = []
        offres_conservees = []
        
        for offre in toutes_offres:
            # Vérifier par le type_offre
            est_tender = False
            if hasattr(offre, 'type_offre') and offre.type_offre:
                est_tender = offre.type_offre == 'APPEL_D_OFFRES'
            
            # Si pas de type_offre, utiliser la détection
            if not est_tender:
                est_tender = est_appel_offres(offre.titre, offre.description or "")
            
            if est_tender:
                offres_conservees.append(offre)
            else:
                offres_a_supprimer.append(offre)
        
        total_a_supprimer = len(offres_a_supprimer)
        total_conservees = len(offres_conservees)
        
        self.stdout.write(f"\n📊 Résultat de l'analyse :")
        self.stdout.write(f"   - Offres à conserver (appels d'offres) : {total_conservees}")
        self.stdout.write(f"   - Offres à supprimer : {total_a_supprimer}")
        
        if total_a_supprimer == 0:
            self.stdout.write(self.style.SUCCESS("\n✅ Aucune offre à supprimer ! Toutes sont des appels d'offres."))
            return
        
        # Afficher les offres à supprimer
        self.stdout.write("\n📋 Liste des offres à supprimer :")
        for i, offre in enumerate(offres_a_supprimer[:20], 1):
            type_offre = getattr(offre, 'type_offre', 'Non défini')
            domaine = offre.domaine or 'Non défini'
            self.stdout.write(
                f"   {i}. {offre.titre[:60]}..."
                f"\n      Type: {type_offre} | Domaine: {domaine} | Organisme: {offre.organisme[:30]}"
            )
        
        if len(offres_a_supprimer) > 20:
            self.stdout.write(f"   ... et {len(offres_a_supprimer) - 20} autres offres")
        
        # Si dry-run, on s'arrête ici
        if dry_run:
            self.stdout.write(self.style.WARNING(f"\n⚠️ DRY RUN : {total_a_supprimer} offres seraient supprimées."))
            self.stdout.write("   Lancez avec --force pour supprimer définitivement.")
            return
        
        # Demander confirmation
        if not force:
            confirm = input(f"\n⚠️ Voulez-vous vraiment supprimer {total_a_supprimer} offres ? (oui/non) : ")
            if confirm.lower() != 'oui':
                self.stdout.write(self.style.WARNING("❌ Suppression annulée."))
                return
        
        # Supprimer les offres
        self.stdout.write("\n🗑️ Suppression en cours...")
        
        deleted_count = 0
        for offre in offres_a_supprimer:
            try:
                # Supprimer le fichier PDF si présent
                if offre.fichier_pdf and offre.fichier_pdf.name:
                    try:
                        offre.fichier_pdf.delete(save=False)
                    except Exception as e:
                        self.stdout.write(f"   ⚠️ Erreur suppression PDF: {e}")
                
                # Supprimer l'offre
                offre.delete()
                deleted_count += 1
                
                if deleted_count % 10 == 0:
                    self.stdout.write(f"   {deleted_count}/{total_a_supprimer} supprimées...")
                    
            except Exception as e:
                self.stdout.write(f"   ❌ Erreur suppression de l'offre {offre.id}: {e}")
        
        self.stdout.write(
            self.style.SUCCESS(f"\n✅ {deleted_count} offres supprimées avec succès !")
        )
        self.stdout.write(
            self.style.SUCCESS(f"✅ {total_conservees} appels d'offres conservés.")
        )
        
        # Afficher la nouvelle répartition
        from django.db.models import Count
        if hasattr(AppelOffre, 'type_offre'):
            repartition = AppelOffre.objects.values('type_offre').annotate(
                total=Count('id')
            ).order_by('-total')
            
            self.stdout.write("\n📊 NOUVELLE RÉPARTITION PAR TYPE :")
            for d in repartition:
                type_choices = dict(AppelOffre.TYPE_OFFRE_CHOICES)
                type_nom = type_choices.get(d['type_offre'], d['type_offre'])
                self.stdout.write(f"  - {type_nom}: {d['total']} offres")
        
        # Afficher la répartition par domaine
        repartition_domaine = AppelOffre.objects.values('domaine').annotate(
            total=Count('id')
        ).order_by('-total')
        
        self.stdout.write("\n📊 RÉPARTITION PAR DOMAINE :")
        for d in repartition_domaine:
            domaine = d['domaine'] or 'Non défini'
            self.stdout.write(f"  - {domaine}: {d['total']} offres")