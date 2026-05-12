# test_scraping.py - À la racine du projet (même niveau que manage.py)
import os
import sys
import django

from offres.scraping.parsers.j360_burkina import J360BurkinaParser

from offres.scraping.parsers.j360_burkina import J360BurkinaParser

# 1. Ajouter le projet au PYTHONPATH
sys.path.append(r"C:\Users\sebas\Downloads\plateforme_offres")

# 2. Définir le module de settings Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_offres.settings')

# 3.  INITIALISER DJANGO - OBLIGATOIRE avant tout import de modèles
django.setup()

# Maintenant on peut importer nos modules Django
from offres.models import AppelOffre

print(" Démarrage du test de scraping...")

# Tester le parser sur une URL cible (à adapter)
parser = J360BurkinaParser("https://www.armp.bf")
offres_extraites = parser.run()

print(f" {len(offres_extraites)} offres extraites")

# Afficher un exemple
if offres_extraites:
    print("\n Exemple d'offre :")
    for key, value in offres_extraites[0].items():
        print(f"   {key}: {value}")

# Compter les offres en base
total = AppelOffre.objects.count()
print(f"\n Total offres en base de données : {total}")