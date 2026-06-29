# scripts/reset_scraping.py
"""
Supprime TOUTES les offres et relance le scraping proprement
"""
import os
import sys

# Ajouter le chemin du projet
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_offres.settings')

import django
django.setup()

from offres.models import AppelOffre, SourceScraping
from django.utils import timezone


def reset_all():
    print("\n" + "=" * 70)
    print("🗑️  RÉINITIALISATION COMPLÈTE DU SCRAPING")
    print("=" * 70)
    
    # 1. Supprimer toutes les offres
    total_offres = AppelOffre.objects.count()
    print(f"\n📊 Offres en base : {total_offres}")
    
    if total_offres > 0:
        confirm = input(f"\n⚠️  Voulez-vous vraiment supprimer {total_offres} offres ? (oui/non) : ")
        if confirm.lower() != 'oui':
            print("❌ Annulé")
            return
        
        AppelOffre.objects.all().delete()
        print(f"✅ {total_offres} offres supprimées")
    else:
        print("✅ Aucune offre à supprimer")
    
    # 2. Réinitialiser last_scraped des sources
    sources = SourceScraping.objects.all()
    for source in sources:
        source.last_scraped = None
        source.save(update_fields=['last_scraped'])
    print(f"✅ {sources.count()} sources réinitialisées")
    
    print("\n" + "=" * 70)
    print("✅ NETTOYAGE TERMINÉ")
    print("=" * 70)
    print("\n🚀 Vous pouvez maintenant lancer : python manage.py scraper\n")


if __name__ == '__main__':
    reset_all()