# offres/management/commands/fix_domains.py
from django.core.management.base import BaseCommand
from django.db.models import Q
from offres.models import AppelOffre
from offres.utils.search_keywords import detecter_domaine

class Command(BaseCommand):
    help = 'Corrige les domaines des offres mal classifiées'

    def handle(self, *args, **options):
        total_corrige = 0
        
        # 1. CORRECTION MANUELLE DES OFFRES MAL CLASSIFIÉES
        corrections = {
            'motocyclette': 'Transport & Logistique',
            'bureau d\'etudes': 'Services & Conseil',
            'bureau d\'études': 'Services & Conseil',
            'recrutement': 'Services & Conseil',
            'verifications': 'Finance & Comptabilité',
            'vérifications': 'Finance & Comptabilité',
            'spot checks': 'Finance & Comptabilité',
            'rehabilitation': 'Ingénierie & Construction',
            'réhabilitation': 'Ingénierie & Construction',
            'construction': 'Ingénierie & Construction',
        }
        
        self.stdout.write("🔍 Correction des offres mal classifiées...")
        
        # Parcourir toutes les offres
        for offre in AppelOffre.objects.all():
            titre_lower = offre.titre.lower()
            nouveau_domaine = None
            
            # Vérifier si le titre contient un mot-clé de correction
            for mot_cle, domaine in corrections.items():
                if mot_cle in titre_lower:
                    nouveau_domaine = domaine
                    break
            
            if nouveau_domaine and nouveau_domaine != offre.domaine:
                ancien = offre.domaine
                offre.domaine = nouveau_domaine
                offre.save(update_fields=['domaine'])
                total_corrige += 1
                self.stdout.write(
                    self.style.WARNING(f"  ✏️ {offre.titre[:50]}...")
                )
                self.stdout.write(f"     {ancien} → {nouveau_domaine}")
        
        # 2. CORRECTION INTELLIGENTE DES OFFRES IT & Digital
        self.stdout.write("\n🔄 Correction intelligente des offres IT & Digital...")
        
        # Mots-clés qui indiquent que l'offre est vraiment IT
        mots_cles_it = [
            'informatique', 'digital', 'ordinateur', 'logiciel', 'plateforme',
            'data', 'système', 'it', 'software', 'hardware', 'réseau',
            'internet', 'cloud', 'cyber', 'sécurité informatique'
        ]
        
        # Récupérer les offres IT & Digital
        offres_it = AppelOffre.objects.filter(domaine='IT & Digital')
        
        for offre in offres_it:
            titre_lower = offre.titre.lower()
            description_lower = (offre.description or '').lower()
            texte_complet = titre_lower + ' ' + description_lower
            
            # Vérifier si c'est vraiment une offre IT
            est_vraiment_it = any(mot in texte_complet for mot in mots_cles_it)
            
            if not est_vraiment_it:
                # Re-détecter le domaine
                nouveau_domaine = detecter_domaine(offre.titre, offre.description or '')
                
                if nouveau_domaine and nouveau_domaine != 'IT & Digital':
                    ancien = offre.domaine
                    offre.domaine = nouveau_domaine
                    offre.save(update_fields=['domaine'])
                    total_corrige += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"  ✅ {offre.titre[:50]}...")
                    )
                    self.stdout.write(f"     {ancien} → {nouveau_domaine}")
        
        # 3. VÉRIFICATION DES OFFRES "Autres"
        self.stdout.write("\n🔄 Vérification des offres 'Autres'...")
        
        offres_autres = AppelOffre.objects.filter(domaine='Autres')
        
        for offre in offres_autres:
            # Re-détecter le domaine
            nouveau_domaine = detecter_domaine(offre.titre, offre.description or '')
            
            if nouveau_domaine and nouveau_domaine != 'Autres':
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