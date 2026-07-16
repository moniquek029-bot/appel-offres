from django.core.management.base import BaseCommand
from django.db.models import Q
from offres.models import AppelOffre
from offres.utils.search_keywords import detecter_domaine

class Command(BaseCommand):
    help = 'Corrige les domaines des offres mal classifiées'

    def handle(self, *args, **options):
        total_corrige = 0
        
        self.stdout.write("🔍 Correction de tous les domaines...")
        
        # Correction intelligente de TOUTES les offres
        for offre in AppelOffre.objects.all():
            nouveau_domaine = detecter_domaine(offre.titre, offre.description or '')
            
            if nouveau_domaine and nouveau_domaine != offre.domaine:
                ancien = offre.domaine
                offre.domaine = nouveau_domaine
                offre.save(update_fields=['domaine'])
                total_corrige += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ {offre.titre[:50]}...")
                )
                self.stdout.write(f"     {ancien} → {nouveau_domaine}")
        
        self.stdout.write(
            self.style.SUCCESS(f"\n✅ {total_corrige} offres corrigées !")
        )
        
        # Afficher le nouveau bilan
        from django.db.models import Count
        repartition = AppelOffre.objects.values('domaine').annotate(
            total=Count('id')
        ).order_by('-total')
        
        self.stdout.write("\n📊 NOUVELLE RÉPARTITION PAR DOMAINE :")
        for d in repartition:
            domaine = d['domaine'] or 'Non défini'
            self.stdout.write(f"  - {domaine}: {d['total']} offres")