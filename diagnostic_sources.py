#!/usr/bin/env python3
"""
DIAGNOSTIC DES SOURCES DE SCRAPING
Teste chaque source et génère un rapport détaillé
"""

import os
import django
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_offres.settings')
django.setup()

from offres.models import SourceScraping
from offres.scraping.base import BaseScraper

# Configuration HTTP
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
}

def test_source(source):
    """Teste une source et retourne un diagnostic"""
    print(f"\n{'='*70}")
    print(f"🔍 TEST DE : {source.nom}")
    print(f"🌐 URL : {source.url_racine}")
    print(f"{'='*70}")
    
    result = {
        'nom': source.nom,
        'url': source.url_racine,
        'status': '❌ ÉCHEC',
        'details': [],
        'html_size': 0,
        'offers_found': 0,
    }
    
    # Test 1 : Connexion HTTP
    print("\n📡 Test 1 : Connexion HTTP...")
    try:
        response = requests.get(
            source.url_racine,
            headers=HEADERS,
            timeout=20,
            verify=False
        )
        
        if response.status_code == 200:
            print(f"   ✅ Status code : {response.status_code}")
            result['html_size'] = len(response.text)
            print(f"   📏 Taille HTML : {result['html_size']} caractères")
        else:
            print(f"   ❌ Status code : {response.status_code}")
            result['details'].append(f"HTTP {response.status_code}")
            return result
            
    except requests.exceptions.Timeout:
        print("   ❌ Timeout (20s)")
        result['details'].append("Timeout")
        return result
    except Exception as e:
        print(f"   ❌ Erreur : {e}")
        result['details'].append(str(e)[:50])
        return result
    
    # Test 2 : Parsing HTML
    print("\n🔧 Test 2 : Parsing HTML...")
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Compter les éléments
        links = soup.find_all('a', href=True)
        articles = soup.find_all(['article', 'div'])
        tables = soup.find_all('table')
        
        print(f"   📊 Liens trouvés : {len(links)}")
        print(f"   📊 Articles/Divs : {len(articles)}")
        print(f"   📊 Tableaux : {len(tables)}")
        
        # Chercher des mots-clés d'offres
        keywords = ['appel', 'offre', 'tender', 'procurement', 'tdr', 'marché']
        keywords_found = []
        
        for keyword in keywords:
            count = len(soup.find_all(string=lambda text: text and keyword.lower() in text.lower()))
            if count > 0:
                keywords_found.append(f"{keyword}({count})")
        
        if keywords_found:
            print(f"   ✅ Mots-clés trouvés : {', '.join(keywords_found)}")
        else:
            print(f"   ⚠️  Aucun mot-clé d'offre détecté")
            result['details'].append("Pas de mots-clés d'offres")
            
    except Exception as e:
        print(f"   ❌ Erreur parsing : {e}")
        result['details'].append(f"Parse error: {str(e)[:30]}")
        return result
    
    # Test 3 : Test du parser
    print("\n🕷️ Test 3 : Test du parser...")
    try:
        from offres.scraping.tasks import get_parser_for_source
        
        parser = get_parser_for_source(source)
        print(f"   📦 Parser utilisé : {parser.__class__.__name__}")
        
        # Exécuter le parser
        offres = parser.run()
        result['offers_found'] = len(offres)
        
        if offres:
            print(f"   ✅ {len(offres)} offres extraites")
            result['status'] = '✅ SUCCÈS'
            
            # Afficher les 3 premières offres
            for i, offre in enumerate(offres[:3], 1):
                titre = offre.get('titre', 'Sans titre')[:60]
                print(f"      {i}. {titre}...")
        else:
            print(f"   ⚠️  Aucune offre extraite")
            result['status'] = '⚠️ PARTIEL'
            result['details'].append("0 offres extraites")
            
    except Exception as e:
        print(f"   ❌ Erreur parser : {e}")
        result['details'].append(f"Parser error: {str(e)[:30]}")
    
    return result


def main():
    print("\n" + "="*70)
    print("🔍 DIAGNOSTIC COMPLET DES SOURCES DE SCRAPING")
    print("="*70)
    
    # Récupérer toutes les sources actives
    sources = SourceScraping.objects.filter(est_actif=True)
    
    if not sources.exists():
        print("\n⚠️ Aucune source active trouvée dans la base de données")
        print("💡 Ajoute des sources via l'interface admin Django")
        return
    
    print(f"\n📊 {sources.count()} sources actives à tester\n")
    
    results = []
    
    # Tester chaque source
    for source in sources:
        result = test_source(source)
        results.append(result)
        time.sleep(2)  # Délai de politesse
    
    # Rapport final
    print("\n" + "="*70)
    print("📊 RAPPORT FINAL")
    print("="*70)
    
    success = [r for r in results if r['status'] == '✅ SUCCÈS']
    partial = [r for r in results if r['status'] == '⚠️ PARTIEL']
    failed = [r for r in results if r['status'] == '❌ ÉCHEC']
    
    print(f"\n✅ Sources fonctionnelles : {len(success)}/{len(results)}")
    print(f"⚠️  Sources partielles : {len(partial)}/{len(results)}")
    print(f"❌ Sources en échec : {len(failed)}/{len(results)}")
    
    if success:
        print("\n✅ SOURCES FONCTIONNELLES :")
        for r in success:
            print(f"   • {r['nom']} ({r['offers_found']} offres)")
    
    if partial:
        print("\n⚠️  SOURCES PARTIELLES (à corriger) :")
        for r in partial:
            print(f"   • {r['nom']}")
            for detail in r['details']:
                print(f"      → {detail}")
    
    if failed:
        print("\n❌ SOURCES EN ÉCHEC :")
        for r in failed:
            print(f"   • {r['nom']}")
            for detail in r['details']:
                print(f"      → {detail}")
    
    # Sauvegarder le rapport
    with open('diagnostic_sources.txt', 'w', encoding='utf-8') as f:
        f.write("DIAGNOSTIC DES SOURCES DE SCRAPING\n")
        f.write("="*70 + "\n\n")
        for r in results:
            f.write(f"{r['status']} {r['nom']}\n")
            f.write(f"   URL : {r['url']}\n")
            f.write(f"   HTML : {r['html_size']} caractères\n")
            f.write(f"   Offres : {r['offers_found']}\n")
            if r['details']:
                f.write(f"   Détails : {', '.join(r['details'])}\n")
            f.write("\n")
    
    print(f"\n💾 Rapport sauvegardé dans : diagnostic_sources.txt")


if __name__ == "__main__":
    main()