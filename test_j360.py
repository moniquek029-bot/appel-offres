# =============================================================================
# test_j360.py - Test du parser j360.info Burkina Faso
#  CE CODE DOIT ÊTRE EXÉCUTÉ AVEC : python test_j360.py
# =============================================================================

# -----------------------------------------------------------------------------
#  BLOC D'INITIALISATION DJANGO - OBLIGATOIRE EN TÊTE DE FICHIER
# -----------------------------------------------------------------------------
import os
import sys
import django

# 1. Ajouter la racine du projet au PYTHONPATH
PROJECT_ROOT = r"C:\Users\sebas\Downloads\plateforme_offres"
sys.path.append(PROJECT_ROOT)

# 2. Définir le module de settings Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_offres.settings')

# 3. INITIALISER DJANGO - Cette ligne est CRITIQUE
#    Elle charge la configuration AVANT tout import de modèles Django
django.setup()
# -----------------------------------------------------------------------------
#  MAINTENANT on peut importer nos modules Django
# -----------------------------------------------------------------------------

from offres.scraping.parsers.j360_burkina import J360BurkinaParser
from offres.models import AppelOffre

print(" Test du parser j360.info Burkina Faso...")
print(f" Projet : {PROJECT_ROOT}")

# URL cible (avec paramètre de recherche optionnel)
TARGET_URL = "https://www.j360.info/appels-d-offres/afrique/burkina-faso/?q=gestion"

try:
    parser = J360BurkinaParser(TARGET_URL)
    resultats = parser.run()
    
    print(f"\n {len(resultats)} offre(s) extraite(s)")
    
    if resultats:
        print("\n Exemple de la première offre :")
        for key, value in resultats[0].items():
            print(f"   • {key}: {value}")
    else:
        print("\n Aucune offre extraite. Causes possibles :")
        print("   1. Site inaccessible (VPN/Firewall/DNS)")
        print("   2. Sélecteurs CSS à ajuster (voir F12 → Inspecter)")
        print("   3. robots.txt bloque le scraping")
        print("   4. Site dynamique nécessitant Selenium")
        
except ImportError as e:
    print(f"\n Erreur d'import : {e}")
    print(" Vérifiez que le fichier 'j360_burkina.py' existe dans offres/scraping/parsers/")
    
except Exception as e:
    print(f"\n Erreur lors du scraping : {type(e).__name__} - {e}")

# Compter les offres en base
try:
    total = AppelOffre.objects.count()
    print(f"\n Total offres en base de données : {total}")
except Exception as e:
    print(f"\n Impossible de compter les offres : {e}")


    # Ajoutez ce test alternatif à la fin de test_j360.py

print("\n Test avec HTML mocké (sans réseau)...")

from bs4 import BeautifulSoup

# HTML de test simulé (structure générique)
TEST_HTML = """
<html><body>
  <article class="post">
    <h2 class="entry-title"><a href="/offre/123">Fourniture de matériel informatique</a></h2>
    <span class="author">Ministère du Numérique</span>
    <p class="excerpt">Appel d'offres pour la fourniture d'ordinateurs...</p>
    <time datetime="2026-05-01">01/05/2026</time>
    <span class="deadline">30/06/2026</span>
  </article>
</body></html>
"""

parser_mock = J360BurkinaParser("https://test.local")
soup = BeautifulSoup(TEST_HTML, "html.parser")
resultats_mock = parser_mock.parse(soup)  # Note: parse() et non run()

print(f" {len(resultats_mock)} offre(s) extraite(s) en local")
for off in resultats_mock:
    print(f"   • {off['titre']} | {off['organisme']}")