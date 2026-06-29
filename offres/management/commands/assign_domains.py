# offres/management/commands/assign_domains.py
from django.core.management.base import BaseCommand
from django.db.models import Q
from offres.models import AppelOffre
import re

class Command(BaseCommand):
    help = 'Assigne automatiquement un domaine à toutes les offres qui n\'en ont pas'

    def detecter_domaine(self, titre, description=""):
        """Détecte automatiquement le domaine d'une offre"""
        texte = (titre + " " + (description or "")).lower()
        
        mapping = {
            'IT & Digital': [
                'informatique', 'digital', 'ordinateur', 'logiciel', 'plateforme', 
                'data', 'système', 'it', 'technology', 'software', 'hardware', 
                'réseau', 'internet', 'cloud', 'cyber', 'sécurité informatique'
            ],
            
            'Ingénierie & Construction': [
                'construction', 'réhabilitation', 'bâtiment', 'génie', 
                'infrastructure', 'travaux', 'rénovation', 'génie civil',
                'architecte', 'chantier', 'génie rural'
            ],
            
            'Santé & Médical': [
                'santé', 'médical', 'hôpital', 'clinique', 'pharmaceutique', 
                'laboratoire', 'soins', 'médecine', 'infirmier', 'urgence',
                'médicament', 'vaccin', 'matériel médical'
            ],
            
            'Transport & Logistique': [
                'transport', 'logistique', 'véhicule', 'motocyclette', 
                'livraison', 'camion', 'bus', 'car', 'fret', 'mobilité'
            ],
            
            'Éducation & Formation': [
                'éducation', 'formation', 'enseignement', 'apprentissage', 
                'training', 'cours', 'études', 'pédagogie', 'université'
            ],
            
            'Environnement & Climat': [
                'environnement', 'climat', 'énergie', 'renouvelable', 
                'durable', 'écologie', 'développement durable', 'écologique',
                'solaire', 'éolien', 'recyclage', 'vert'
            ],
            
            'Finance & Comptabilité': [
                'finance', 'comptabilité', 'audit', 'budget', 'compte', 
                'financier', 'fiscal', 'trésorerie', 'investissement', 'banque'
            ],
            
            'Communication & Médias': [
                'communication', 'média', 'vidéo', 'documentaire', 
                'publicité', 'journal', 'radio', 'tv', 'presse',
                'audiovisuel', 'marketing'
            ],
            
            'Agriculture & Alimentation': [
                'agriculture', 'alimentation', 'agro', 'élevage', 
                'cultures', 'récolte', 'nourriture', 'céréale', 'riz',
                'maraîcher', 'élevage', 'bétail', 'semences'
            ],
            
            'Juridique & Droit': [
                'juridique', 'droit', 'loi', 'réglementation', 'légal', 
                'contrat', 'avocat', 'justice', 'contentieux'
            ],
            
            'Ressources Humaines': [
                'ressources humaines', 'rh', 'recrutement', 'embauche', 
                'personnel', 'staff', 'employé', 'carrière', 'talent'
            ],
            
            'Sécurité & Protection': [
                'sécurité', 'protection', 'défense', 'armée', 'militaire',
                'garde', 'sûreté', 'cybersécurité', 'police'
            ],
            
            'Social & Égalité': [
                'social', 'égalité', 'femme', 'jeune', 'égalité des genres',
                'pauvreté', 'humanitaire', 'inclusion', 'solidarité'
            ],
            
            'Biens & Équipements': [
                'bien', 'équipement', 'matériel', 'fourniture', 'achat', 
                'acquisition', 'livraison', 'fournitures', 'consommables'
            ],
            
            'Services & Conseil': [
                'service', 'conseil', 'consulting', 'consultant', 'étude', 
                'expertise', 'évaluation', 'assistance', 'support'
            ],
        }
        
        for domaine, mots in mapping.items():
            for mot in mots:
                if mot in texte:
                    return domaine
        
        # Si aucune correspondance, vérifier les termes génériques
        if 'achat' in texte or 'fourniture' in texte:
            return 'Biens & Équipements'
        if 'étude' in texte or 'consultant' in texte:
            return 'Services & Conseil'
        if 'appel d\'offres' in texte or 'ao' in texte:
            return 'Services & Conseil'
        
        return 'Autres'

    def handle(self, *args, **options):
        # Récupérer les offres sans domaine
        offres_sans_domaine = AppelOffre.objects.filter(
            Q(domaine__isnull=True) | Q(domaine='')
        )
        
        count = offres_sans_domaine.count()
        self.stdout.write(f"📊 Traitement de {count} offres sans domaine...")
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS("✅ Toutes les offres ont déjà un domaine !"))
            return
        
        updated_count = 0
        for offre in offres_sans_domaine:
            ancien_domaine = offre.domaine
            nouveau_domaine = self.detecter_domaine(offre.titre, offre.description or "")
            offre.domaine = nouveau_domaine
            offre.save(update_fields=['domaine'])
            updated_count += 1
            
            if updated_count % 10 == 0:
                self.stdout.write(f"   ⏳ {updated_count}/{count} offres traitées...")
        
        self.stdout.write(
            self.style.SUCCESS(f"✅ {updated_count} offres mises à jour avec succès !")
        )
        
        # Afficher la répartition par domaine
        from django.db.models import Count
        repartition = AppelOffre.objects.values('domaine').annotate(count=Count('id')).order_by('-count')
        self.stdout.write("\n📈 Répartition par domaine :")
        for item in repartition:
            self.stdout.write(f"   - {item['domaine'] or 'Non défini'}: {item['count']} offres")