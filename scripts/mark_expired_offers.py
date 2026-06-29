# scripts/mark_expired_offers.py
"""Script pour marquer automatiquement les offres expirées"""
import os
import sys
import django
from datetime import date

# ✅ AJOUTER LE CHEMIN DU PROJET AU PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"✅ Chemin ajouté au PYTHONPATH : {project_root}")

# ✅ NOM EXACT DU PROJET
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_offres.settings')
django.setup()

from offres.models import AppelOffre

def mark_expired_offers():
    today = date.today()
    offres_expirees = AppelOffre.objects.filter(
        statut='Ouvert',
        date_cloture__lt=today
    )
    
    total = offres_expirees.count()
    if total == 0:
        print(f"\n✅ Aucune offre expirée trouvée (date: {today})\n")
        return
        
    print(f"\n🔄 Mise à jour de {total} offres expirées...")
    print("=" * 60)
    
    updated = 0
    for offre in offres_expirees:
        offre.statut = 'Clôturé'
        offre.est_expire = True
        offre.save(update_fields=['statut', 'est_expire'])
        updated += 1
        print(f"  ✅ [{updated}] {offre.titre[:50]}... (clôturée le {offre.date_cloture})")
        
    print("=" * 60)
    print(f"✅ Terminé : {updated}/{total} offres marquées comme clôturées\n")

if __name__ == '__main__':
    mark_expired_offers()