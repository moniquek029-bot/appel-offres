# scripts/check_stats.py
"""
Vérifie les statistiques de la base de données
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
from django.db.models import Count

print("\n" + "=" * 80)
print("📊 STATISTIQUES DE LA BASE DE DONNÉES")
print("=" * 80)

# Total
total = AppelOffre.objects.count()
print(f"\n📦 Total offres : {total}")

# Par organisme
print("\n🏢 Par organisme :")
for o in AppelOffre.objects.values('organisme').annotate(total=Count('id')).order_by('-total'):
    print(f"   • {o['organisme']}: {o['total']}")

# Par pays
print("\n🌍 Par pays :")
for p in AppelOffre.objects.values('pays').annotate(total=Count('id')).order_by('-total')[:15]:
    print(f"   • {p['pays']}: {p['total']}")

# Par domaine
print("\n📂 Par domaine :")
for d in AppelOffre.objects.values('domaine').annotate(total=Count('id')).order_by('-total'):
    print(f"   • {d['domaine']}: {d['total']}")

# Par statut
print("\n📋 Par statut :")
for s in AppelOffre.objects.values('statut').annotate(total=Count('id')).order_by('-total'):
    print(f"   • {s['statut']}: {s['total']}")

print("\n" + "=" * 80)