# test_j360_selenium.py
import os, sys, django
sys.path.append(r"C:\Users\sebas\Downloads\plateforme_offres")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_offres.settings')
django.setup()

from offres.scraping.parsers.j360_selenium import J360SeleniumParser
print("🚀 Premier lancement : connectez-vous dans le navigateur, puis appuyez sur ENTRÉE...")
parser = J360SeleniumParser("https://app.j360.info/#/my-monitoring")
resultats = parser.run()
print(f"\n✅ {len(resultats)} offre(s) extraite(s)")
if resultats: print("📋", resultats[0])