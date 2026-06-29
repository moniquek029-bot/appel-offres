# scripts/cleanup_offers.py
"""Nettoie la base : domaines + offres expirées"""
import os
import sys
from datetime import date

# Ajouter le chemin du projet
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_offres.settings')

import django
django.setup()

from offres.models import AppelOffre
from offres.scraping.constantes import detecter_domaine

def cleanup():
    print("\n" + "=" * 70)
    print("🧹 NETTOYAGE DE LA BASE DES OFFRES")
    print("=" * 70)
    
    # 1. Mettre à jour les domaines
    print("\n📊 ÉTAPE 1 : Mise à jour des domaines")
    print("-" * 70)
    offres = AppelOffre.objects.all()
    total = offres.count()
    updated_domaines = 0
    
    for offre in offres:
        texte = f"{offre.titre} {offre.description or ''} {offre.organisme or ''}"
        domaine = detecter_domaine(texte)
        if offre.domaine != domaine:
            offre.domaine = domaine
            offre.save(update_fields=['domaine'])
            updated_domaines += 1
    
    print(f"✅ {updated_domaines}/{total} domaines mis à jour")
    
    # 2. Marquer les offres expirées
    print("\n⏰ ÉTAPE 2 : Marquage des offres expirées")
    print("-" * 70)
    today = date.today()
    offres_expirees = AppelOffre.objects.filter(
        statut='Ouvert',
        date_cloture__lt=today
    )
    total_expirees = offres_expirees.count()
    updated_statut = 0
    
    for offre in offres_expirees:
        offre.statut = 'Clôturé'
        offre.est_expire = True
        offre.save(update_fields=['statut', 'est_expire'])
        updated_statut += 1
    
    print(f"✅ {updated_statut}/{total_expirees} offres marquées comme clôturées")
    
    # 3. Statistiques finales
    print("\n📈 STATISTIQUES FINALES")
    print("-" * 70)
    from django.db.models import Count
    
    print("\nPar domaine :")
    for d in AppelOffre.objects.values('domaine').annotate(total=Count('id')).order_by('-total'):
        print(f"  • {d['domaine'] or 'Non défini'}: {d['total']}")
    
    print("\nPar statut :")
    for s in AppelOffre.objects.values('statut').annotate(total=Count('id')).order_by('-total'):
        print(f"  • {s['statut']}: {s['total']}")
    
    print("\nPar pays (top 10) :")
    for p in AppelOffre.objects.values('pays').annotate(total=Count('id')).order_by('-total')[:10]:
        print(f"  • {p['pays']}: {p['total']}")
    
    print("\n" + "=" * 70)
    print("✅ NETTOYAGE TERMINÉ")
    print("=" * 70 + "\n")

if __name__ == '__main__':
    cleanup()