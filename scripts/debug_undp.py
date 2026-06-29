# scripts/debug_undp.py
"""
Diagnostic UNDP : pourquoi les offres sont rejetées
"""
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_offres.settings')

import django
django.setup()

import requests
from bs4 import BeautifulSoup
from offres.scraping.utils import clean_text, normalize_url
from offres.scraping.extraction_helpers import (
    extract_all_details,
    is_offer_expired,
    is_date_unrealistic,
    is_offer_too_old
)
from offres.utils.offer_validator import is_valid_offer_title

print("\n" + "=" * 80)
print("🔍 DIAGNOSTIC UNDP - Analyse des rejets")
print("=" * 80)

# Récupérer la page UNDP
url = "https://procurement-notices.undp.org/"
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(response.text, 'html.parser')

# Extraire les liens view_notice
notice_links = []
for link in soup.find_all('a', href=True):
    href = link['href']
    if 'view_notice' not in href:
        continue
    
    titre = clean_text(link.get_text(strip=True))
    if titre.lower().startswith('title'):
        titre = titre[5:].strip()
    
    if len(titre) < 15:
        continue
    
    url_source = normalize_url(href, url)
    notice_links.append({'titre': titre, 'url_source': url_source})

print(f"\n📊 {len(notice_links)} notices trouvées")
print("-" * 80)

# Analyser les 10 premières
for i, notice in enumerate(notice_links[:10], 1):
    print(f"\n{i}. {notice['titre'][:70]}")
    
    # Test 1 : Validation du titre
    titre_valide = is_valid_offer_title(notice['titre'])
    print(f"   📝 Titre valide: {'✅' if titre_valide else '❌'}")
    
    if not titre_valide:
        print(f"      → REJETÉ à l'étape 1 (titre invalide)")
        continue
    
    # Test 2 : Visiter la page de détail
    try:
        detail_response = requests.get(notice['url_source'], headers=headers, timeout=15)
        detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
        
        details = extract_all_details(
            detail_soup,
            url=notice['url_source'],
            pays_defaut='BF',
            titre=notice['titre'],
            description=notice['titre']
        )
        
        date_cloture = details.get('date_cloture')
        date_publication = details.get('date_publication')
        
        print(f"   📅 Date pub: {date_publication}")
        print(f"   📅 Date cloture: {date_cloture}")
        
        # Test 3 : Expirée ?
        if is_offer_expired(date_cloture):
            print(f"   ⏰ EXPIRÉE → REJETÉ")
            continue
        
        # Test 4 : Date irréaliste ?
        if is_date_unrealistic(date_cloture):
            print(f"   🚀 DATE IRRÉALISTE → REJETÉ")
            continue
        
        # Test 5 : Trop ancienne ?
        if is_offer_too_old(date_publication):
            print(f"   📜 TROP ANCIENNE → REJETÉ")
            continue
        
        print(f"   ✅ OFFRE VALIDÉE")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

print("\n" + "=" * 80)