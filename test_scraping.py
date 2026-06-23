#!/usr/bin/env python
"""
test_scraping.py - Test rapide du scraping GlobalTenders
Exécution : python test_scraping.py
"""
import os# test_scraper.py
import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_offres.settings')
django.setup()

from offres.scraping.parsers.unfpa_parser import UNFPAParser

# Test UNFPA
url_test = "https://burkinafaso.unfpa.org/fr/node/add/procurement_notice"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print(f"🔍 Test de : {url_test}")
response = requests.get(url_test, headers=headers, timeout=15)
print(f"📊 Status code : {response.status_code}")
print(f"📏 Taille HTML : {len(response.text)} caractères")

# Sauvegarder le HTML pour analyse
with open('debug_unfpa.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("💾 HTML sauvegardé dans debug_unfpa.html")

# Tester le parser
parser = UNFPAParser(url_test)
offres = parser.run()
print(f"📦 Nombre d'offres trouvées : {len(offres)}")
if offres:
    print(f"✅ Première offre : {offres[0]}")
else:
    print("❌ Aucune offre extraite - Vérifier les sélecteurs CSS")
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_offres.settings')
django.setup()

from offres.scraping.parsers.globaltenders_parser import GlobalTendersParser
from offres.models import AppelOffre, SourceScraping
from django.db.models import Count

print(" Test du parser GlobalTenders...")

# 1. Tester le parser en isolation
parser = GlobalTendersParser("https://www.globaltenders.com?mock=true")
data = parser.run()

print(f" Parser retourne : {len(data)} offre(s)")
if data:
    print(f" Premier titre : {data[0].get('titre', 'N/A')[:60]}...")
    print(f" Premier URL : {data[0].get('url_tdr', 'N/A')}")

# 2. Vérifier ce qui est en base
total = AppelOffre.objects.count()
print(f"\n Total en base : {total} offre(s)")

# 3. Compter par source
stats = AppelOffre.objects.values('source_origine__nom').annotate(
    count=Count('id')
).order_by('-count')

print(f"\n Offres par source :")
for s in stats:
    nom = s['source_origine__nom'] or 'Sans source'
    print(f"   • {nom} : {s['count']}")

# 4. Tester l'insertion manuelle (si total == 11)
if total == 11 and data:
    print(f"\n Test d'insertion d'une nouvelle offre...")
    source = SourceScraping.objects.filter(nom="GlobalTenders").first()
    if not source:
        source = SourceScraping.objects.create(
            nom="GlobalTenders",
            url_racine="https://www.globaltenders.com?mock=true",
            frequence_maj="Toutes les 24h",
            est_actif=True
        )
    
    # Insérer la première offre du parser
    offre_data = data[0]
    obj, created = AppelOffre.objects.update_or_create(
        url_tdr=offre_data["url_tdr"],
        defaults={
            "titre": offre_data["titre"],
            "organisme": offre_data["organisme"],
            "description": offre_data["description"][:500],
            "pays": "BF",
            "date_publication": offre_data["date_publication"],
            "date_cloture": offre_data["date_cloture"],
            "mode_acquisition": "AUTO",
            "source_origine": source,
            "statut": "Ouvert"
        }
    )
    
    nouveau_total = AppelOffre.objects.count()
    print(f" Insertion : {'Nouvelle offre créée' if created else 'Offre mise à jour'}")
    print(f" Nouveau total en base : {nouveau_total}")
    
    if nouveau_total > total:
        print(" SUCCÈS : Les nouvelles offres sont bien ajoutées !")
    else:
        print("  Attention : Le total n'a pas changé (doublon d'URL ?)")

print("\n Test terminé !")