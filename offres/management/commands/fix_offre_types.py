# offres/management/commands/fix_offre_types.py
from django.core.management.base import BaseCommand
from offres.models import AppelOffre
from offres.utils.search_keywords import detecter_type_offre

class Command(BaseCommand):
    help = 'Détecte et corrige le type des offres'

    def handle(self, *args, **options):
        total_corrige = 0
        
        self.stdout.write("🔍 Détection des types d'offres...")
        
        for offre in AppelOffre.objects.all():
            type_detecte = detecter_type_offre(offre.titre, offre.description or '')
            
            if offre.type_offre != type_detecte:
                ancien = offre.type_offre
                offre.type_offre = type_detecte
                offre.save(update_fields=['type_offre'])
                total_corrige += 1
                
                # Afficher les noms lisibles
                nom_ancien = dict(AppelOffre.TYPE_OFFRE_CHOICES).get(ancien, ancien)
                nom_nouveau = dict(AppelOffre.TYPE_OFFRE_CHOICES).get(type_detecte, type_detecte)
                
                self.stdout.write(
                    self.style.WARNING(f"  ✏️ {offre.titre[:40]}...")
                )
                self.stdout.write(f"     {nom_ancien} → {nom_nouveau}")
        
        self.stdout.write(
            self.style.SUCCESS(f"\n✅ {total_corrige} offres corrigées !")
        )
        
        # Afficher la répartition
        from django.db.models import Count
        repartition = AppelOffre.objects.values('type_offre').annotate(
            total=Count('id')
        ).order_by('-total')
        
        self.stdout.write("\n📊 RÉPARTITION PAR TYPE :")
        for d in repartition:
            nom_type = dict(AppelOffre.TYPE_OFFRE_CHOICES).get(d['type_offre'], d['type_offre'])
            self.stdout.write(f"  - {nom_type}: {d['total']} offres")