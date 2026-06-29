# debug_unfpa.py
"""
Diagnostic du scraping UNFPA
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_offres.settings')
django.setup()

from offres.scraping.parsers.unfpa_parser import UNFPAParser
from offres.models import AppelOffre
import requests

URL = "https://burkinafaso.unfpa.org/fr/call-for-submissions"

print("=" * 80)
print("🔍 DIAGNOSTIC SCRAPING UNFPA")
print("=" * 80)

# =========================================================================
# ÉTAPE 1 : Vérifier que le site est accessible
# =========================================================================
print("\n📡 ÉTAPE 1 : Vérification de l'accessibilité du site...")
try:
    response = requests.get(URL, timeout=15, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    print(f"   Status: {response.status_code}")
    print(f"   Taille HTML: {len(response.text)} caractères")
    
    if response.status_code != 200:
        print(f"   ❌ Site inaccessible !")
        exit()
    
    # Chercher des mots-clés d'offres dans le HTML
    html_lower = response.text.lower()
    mots_cles = ['appel', 'offre', 'tender', 'procurement', 'call', 'submission']
    for mot in mots_cles:
        count = html_lower.count(mot)
        if count > 0:
            print(f"   ✅ Mot '{mot}' trouvé {count} fois")
    
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    exit()

# =========================================================================
# ÉTAPE 2 : Tester le parser
# =========================================================================
print("\n🕷️ ÉTAPE 2 : Test du parser UNFPA...")
try:
    parser = UNFPAParser(URL)
    
    # Récupérer la page
    print("   Récupération de la page...")
    soup = parser.fetch_and_parse(use_js=False)
    
    if not soup:
        print("   ❌ Page non récupérée !")
        exit()
    
    print(f"   ✅ Page récupérée ({len(str(soup))} caractères)")
    
    # Afficher le titre
    title = soup.title.string if soup.title else 'Sans titre'
    print(f"   📄 Titre: {title}")
    
    # Compter les liens
    links = soup.find_all('a', href=True)
    print(f"   🔗 Nombre de liens: {len(links)}")
    
    # Afficher les 10 premiers liens
    print("\n   📋 10 premiers liens :")
    for i, link in enumerate(links[:10], 1):
        href = link.get('href', '')
        text = link.get_text(strip=True)[:60]
        print(f"   {i}. {text} → {href[:60]}")
    
    # Essayer de parser
    print("\n🔍 ÉTAPE 3 : Parsing des offres...")
    offres = parser.parse(soup)
    print(f"   📊 Offres trouvées par parse(): {len(offres)}")
    
    if offres:
        print("\n   📝 Détails des offres :")
        for i, offre in enumerate(offres[:5], 1):
            print(f"   {i}. {offre.get('titre', '')[:70]}")
            print(f"      Pays: {offre.get('pays', '?')}")
            print(f"      URL: {offre.get('url_source', '')[:70]}")
    else:
        print("   ❌ Aucune offre trouvée par parse()")
        print("   → Le parser ne trouve pas les conteneurs d'offres")
    
    # Tester run() complet
    print("\n🚀 ÉTAPE 4 : Test de run() complet...")
    offres_run = parser.run()
    print(f"   📊 Offres retournées par run(): {len(offres_run)}")
    
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

# =========================================================================
# ÉTAPE 5 : Vérifier les offres existantes
# =========================================================================
print("\n💾 ÉTAPE 5 : Offres UNFPA déjà en base...")
offres_unfpa = AppelOffre.objects.filter(source_origine__nom__icontains='UNFPA')
print(f"   📊 Total offres UNFPA en base: {offres_unfpa.count()}")

if offres_unfpa.exists():
    print("\n   📝 5 dernières offres UNFPA :")
    for offre in offres_unfpa.order_by('-date_publication')[:5]:
        print(f"   - {offre.titre[:60]}")
        print(f"     URL: {offre.url_source}")

print("\n" + "=" * 80)