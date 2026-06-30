# scripts/fix_domaines.py
"""
Corrige les domaines incorrects
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

print("\n" + "=" * 80)
print("🔧 CORRECTION DES DOMAINES")
print("=" * 80)

# 1. Supprimer "420 Live Notices" (page d'index)
offres_index = AppelOffre.objects.filter(titre__icontains="420 Live Notices")
if offres_index.exists():
    count = offres_index.count()
    offres_index.delete()
    print(f"\n🗑️ Supprimé : {count} offre(s) '420 Live Notices'")

# 2. Corriger "SDP 01/2026" → IT & Digital
offres_it = AppelOffre.objects.filter(titre__icontains="SDP 01/2026")
for offre in offres_it:
    old = offre.domaine
    offre.domaine = 'IT & Digital'
    offre.save(update_fields=['domaine'])
    print(f"\n📊 IT & Digital : {offre.titre[:60]}")
    print(f"   {old} → IT & Digital")

# 3. Corriger "MEG3" → Environnement & Climat
offres_env = AppelOffre.objects.filter(titre__icontains="MEG3")
for offre in offres_env:
    old = offre.domaine
    offre.domaine = 'Environnement & Climat'
    offre.save(update_fields=['domaine'])
    print(f"\n🌍 Environnement : {offre.titre[:60]}")
    print(f"   {old} → Environnement & Climat")

# 4. Corriger "SDG2030BiH" → Management & Administration
offres_mgmt = AppelOffre.objects.filter(titre__icontains="SDG2030BiH")
for offre in offres_mgmt:
    old = offre.domaine
    offre.domaine = 'Management & Administration'
    offre.save(update_fields=['domaine'])
    print(f"\n📋 Management : {offre.titre[:60]}")
    print(f"   {old} → Management & Administration")

print("\n" + "=" * 80)
print("✅ CORRECTIONS TERMINÉES")
print("=" * 80 + "\n")