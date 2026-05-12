# =============================================================================
# test_jsonld.py - Test du parser JSON-LD pour j360.info Burkina Faso
# =============================================================================
import os
import sys
import django
import json
from bs4 import BeautifulSoup

# -----------------------------------------------------------------------------
#  BLOC D'INITIALISATION DJANGO - OBLIGATOIRE EN TÊTE
# -----------------------------------------------------------------------------
PROJECT_ROOT = r"C:\Users\sebas\Downloads\plateforme_offres"
sys.path.append(PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_offres.settings')
django.setup()
# -----------------------------------------------------------------------------

from offres.scraping.parsers.j360_burkina import J360BurkinaParser

print(" Test du parser JSON-LD avec vos données réelles...")
print(f" Projet : {PROJECT_ROOT}")

# Votre JSON-LD copié depuis le site j360.info
JSONLD_SAMPLE = '''
{
  "@context": "https://schema.org",
  "@type": "DataFeedItem",
  "identifier": "https://www.j360.info/appels-d-offres/54845360-recrutement-de-consultant-pour-la-r%C3%A9alisation-d%C3%A9tude-davant-projet-d%C3%A9taill%C3%A9-de/",
  "dateCreated": "2026-05-08",
  "dateModified": "2026-05-08",
  "name": "Recrutement de Consultant pour la réalisation d'étude d'avant-projet détaillé de l'extension du périmètre irrigué de Bama dans la commune de Bama, province du Houet de la région du Guiriko",
  "item": {
    "@type": "Demand",
    "seller": "MINISTERE DE L'AGRICULTURE DE L'EAU DES RESSOURCES ANIMALES ET HALIEUTIQUES",
    "validThrough": "2026-05-25",
    "areaServed": ["Burkina Faso"],
    "itemOffered":{
      "@type": "Service",
      "category": "Marché en cours",
      "name": "Recrutement de Consultant pour la réalisation d'étude d'avant-projet détaillé de l'extension du périmètre irrigué de Bama dans la commune de Bama, province du Houet de la région du Guiriko"
    }
  }
}
'''

try:
    # Créer un HTML mocké contenant le JSON-LD
    mock_html = f'<html><body><script type="application/ld+json">{JSONLD_SAMPLE}</script></body></html>'
    
    # Initialiser le parser
    parser = J360BurkinaParser("https://www.j360.info")
    
    # Parser le HTML avec BeautifulSoup
    soup = BeautifulSoup(mock_html, "html.parser")
    
    # Exécuter le parsing
    resultats = parser.parse(soup)
    
    print(f"\n {len(resultats)} offre(s) extraite(s)")
    
    if resultats:
        offre = resultats[0]
        print("\n Offre extraite avec succès :")
        print("=" * 60)
        for key, value in offre.items():
            print(f"   • {key}: {value}")
        print("=" * 60)
        print("\n Le parser JSON-LD fonctionne correctement !")
    else:
        print("\n Aucune offre extraite. Vérifiez le code du parser.")
        
except ImportError as e:
    print(f"\n Erreur d'import : {e}")
    print(" Vérifiez que le fichier 'j360_burkina.py' existe dans offres/scraping/parsers/")
    
except Exception as e:
    print(f"\n Erreur lors du test : {type(e).__name__} - {e}")
    import traceback
    traceback.print_exc()