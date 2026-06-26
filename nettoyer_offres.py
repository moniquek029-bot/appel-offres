# nettoyer_offres.py
"""
Script de nettoyage des offres non-valides
Exécutez avec: python manage.py shell < nettoyer_offres.py
Ou directement: python nettoyer_offres.py
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_offres.settings')
django.setup()

from offres.models import AppelOffre
from offres.scraping.site_validator import is_valid_offer_title, is_rejected_content

def nettoyer_offres_invalides(dry_run=True):
    """
    Supprime les offres qui ne sont pas de vrais appels d'offres
    
    Args:
        dry_run (bool): Si True, affiche seulement ce qui serait supprimé sans supprimer
    """
    print("=" * 80)
    print("🧹 NETTOYAGE DES OFFRES NON-VALIDES")
    print("=" * 80)
    
    # Récupérer toutes les offres
    toutes_les_offres = AppelOffre.objects.all()
    total_offres = toutes_les_offres.count()
    
    print(f"\n📊 Total des offres en base: {total_offres}")
    
    offres_a_supprimer = []
    offres_valides = []
    
    print("\n🔍 Analyse des offres en cours...\n")
    
    for offre in toutes_les_offres:
        titre = offre.titre or ''
        description = offre.description or ''
        texte_complet = titre + ' ' + description
        
        # Vérifier si c'est un appel d'offres valide
        titre_valide = is_valid_offer_title(titre)
        contenu_rejete = is_rejected_content(texte_complet)
        
        if not titre_valide or contenu_rejete:
            raison = []
            if not titre_valide:
                raison.append("titre non-valide")
            if contenu_rejete:
                raison.append("contenu non-offre")
            
            offres_a_supprimer.append({
                'id': offre.id,
                'titre': titre[:60],
                'organisme': offre.organisme,
                'raison': ', '.join(raison)
            })
        else:
            offres_valides.append(offre.id)
    
    # Afficher les résultats
    print("=" * 80)
    print("📊 RÉSULTATS DE L'ANALYSE")
    print("=" * 80)
    print(f"✅ Offres valides: {len(offres_valides)}")
    print(f"❌ Offres à supprimer: {len(offres_a_supprimer)}")
    print(f"📈 Pourcentage valide: {(len(offres_valides) / total_offres * 100):.1f}%")
    
    if offres_a_supprimer:
        print("\n" + "=" * 80)
        print("❌ OFFRES À SUPPRIMER")
        print("=" * 80)
        
        for i, offre in enumerate(offres_a_supprimer, 1):
            print(f"\n{i}. ID: {offre['id']}")
            print(f"   Titre: {offre['titre']}...")
            print(f"   Organisme: {offre['organisme']}")
            print(f"   Raison: {offre['raison']}")
        
        # Suppression effective
        if not dry_run:
            print("\n" + "=" * 80)
            print("🗑️  SUPPRESSION EN COURS...")
            print("=" * 80)
            
            ids_a_supprimer = [o['id'] for o in offres_a_supprimer]
            
            try:
                # Supprimer les fichiers PDF associés
                offres_obj = AppelOffre.objects.filter(id__in=ids_a_supprimer)
                
                for offre in offres_obj:
                    if offre.fichier_pdf:
                        try:
                            offre.fichier_pdf.delete(save=False)
                            print(f"   📄 PDF supprimé: ID {offre.id}")
                        except Exception as e:
                            print(f"   ⚠️  Erreur suppression PDF ID {offre.id}: {e}")
                
                # Supprimer les offres
                count, _ = offres_obj.delete()
                
                print(f"\n✅ {count} offre(s) supprimée(s) avec succès!")
                print(f"✅ {len(offres_valides)} offre(s) valide(s) conservée(s)")
                
            except Exception as e:
                print(f"\n❌ Erreur lors de la suppression: {e}")
                import traceback
                traceback.print_exc()
        
        else:
            print("\n" + "=" * 80)
            print("🔍 MODE DRY-RUN ACTIVÉ")
            print("=" * 80)
            print("Aucune suppression effectuée.")
            print("\nPour effectuer la suppression réelle, exécutez:")
            print("  python nettoyer_offres.py --execute")
    
    else:
        print("\n✅ Toutes les offres sont valides! Aucune suppression nécessaire.")
    
    print("\n" + "=" * 80)
    
    return len(offres_a_supprimer)


if __name__ == '__main__':
    # Vérifier les arguments
    dry_run = '--execute' not in sys.argv
    
    if dry_run:
        print("\n⚠️  MODE SIMULATION (dry-run)")
        print("Aucune suppression ne sera effectuée.\n")
    else:
        print("\n⚠️  MODE EXÉCUTION RÉELLE")
        print("Les offres invalides vont être SUPPRIMÉES définitivement!\n")
        
        # Confirmation
        confirmation = input("Tapez 'OUI' pour confirmer: ")
        if confirmation != 'OUI':
            print("❌ Opération annulée.")
            sys.exit(0)
    
    # Exécuter le nettoyage
    nombre_supprime = nettoyer_offres_invalides(dry_run=dry_run)
    
    if nombre_supprime > 0 and not dry_run:
        print(f"\n🎉 Nettoyage terminé! {nombre_supprime} offre(s) supprimée(s).")
    elif dry_run:
        print(f"\n🔍 Simulation terminée. {nombre_supprime} offre(s) seraient supprimées.")