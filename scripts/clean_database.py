# scripts/clean_database.py
"""
Nettoie la base de données en supprimant les offres invalides
"""
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_offres.settings')

import django
django.setup()

from offres.models import AppelOffre
from offres.utils.offer_validator import is_valid_offer_title
from offres.scraping.extraction_helpers import (
    is_offer_expired,
    is_date_unrealistic,
    is_offer_too_old
)
from datetime import date, timedelta

print("\n" + "=" * 80)
print("🧹 NETTOYAGE DE LA BASE DE DONNÉES")
print("=" * 80)

offres = AppelOffre.objects.all()
total = offres.count()
deleted = 0
kept = 0

print(f"\n📊 Total offres : {total}")
print("-" * 80)

for offre in offres:
    should_delete = False
    reason = ""
    
    # 1. Vérifier le titre
    if not is_valid_offer_title(offre.titre):
        should_delete = True
        reason = "Titre invalide"
    
    # 2. Vérifier si expirée
    elif is_offer_expired(offre.date_cloture):
        should_delete = True
        reason = f"Expirée ({offre.date_cloture})"
    
    # 3. Vérifier date irréaliste
    elif is_date_unrealistic(offre.date_cloture):
        should_delete = True
        reason = f"Date irréaliste ({offre.date_cloture})"
    
    # 4. Vérifier offre trop ancienne
    elif is_offer_too_old(offre.date_publication):
        should_delete = True
        reason = f"Trop ancienne ({offre.date_publication})"
    
    # 5. Vérifier pays invalide
    elif not offre.pays or len(offre.pays) > 10:
        should_delete = True
        reason = f"Pays invalide ({offre.pays})"
    
    if should_delete:
        print(f"\n❌ SUPPRIMÉ : {offre.titre[:60]}")
        print(f"   Raison : {reason}")
        offre.delete()
        deleted += 1
    else:
        kept += 1

print("\n" + "=" * 80)
print(f"✅ RÉSULTAT :")
print(f"   • Supprimées : {deleted}")
print(f"   • Conservées : {kept}")
print(f"   • Total initial : {total}")
print("=" * 80 + "\n")