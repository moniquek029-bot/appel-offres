# scripts/update_domaines.py
"""Script pour mettre à jour le domaine des offres existantes"""
import os
import sys
import django

# ✅ AJOUTER LE CHEMIN DU PROJET AU PYTHONPATH
# __file__ = C:\Users\sebas\Downloads\plateforme_offres\scripts\update_domaines.py
# dirname(__file__) = C:\Users\sebas\Downloads\plateforme_offres\scripts
# dirname(dirname(__file__)) = C:\Users\sebas\Downloads\plateforme_offres
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"✅ Chemin ajouté au PYTHONPATH : {project_root}")

# ✅ NOM EXACT DU PROJET
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_offres.settings')
django.setup()

from offres.models import AppelOffre
from offres.scraping.constantes import detecter_domaine

def update_domaines():
    offres = AppelOffre.objects.all()
    total = offres.count()
    updated = 0
    
    print(f"\n🔄 Mise à jour de {total} offres...")
    print("=" * 60)
    
    for offre in offres:
        texte = f"{offre.titre} {offre.description or ''} {offre.organisme or ''}"
        domaine = detecter_domaine(texte)
        
        if offre.domaine != domaine:
            offre.domaine = domaine
            offre.save(update_fields=['domaine'])
            updated += 1
            print(f"  ✅ [{updated}] {offre.titre[:50]}... → {domaine}")
    
    print("=" * 60)
    print(f"✅ Terminé : {updated}/{total} offres mises à jour\n")

if __name__ == '__main__':
    update_domaines()