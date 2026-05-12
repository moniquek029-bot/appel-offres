# test_j360_real.py - Test du parser J360BurkinaParser avec accès réseau réel
import os, sys, django, requests
from bs4 import BeautifulSoup

sys.path.append(r"C:\Users\sebas\Downloads\plateforme_offres")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_offres.settings')
django.setup()

from offres.scraping.parsers.j360_burkina import J360BurkinaParser
from offres.models import AppelOffre

print(" Test du parser J360BurkinaParser avec accès réseau réel...")

TARGET_URL = "https://www.j360.info/appels-d-offres/afrique/burkina-faso/"

try:
    # 1. Tester l'accès HTTP direct
    print(f"\n Test de connexion à {TARGET_URL}...")
    response = requests.get(
        TARGET_URL, 
        timeout=15,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    print(f" Status HTTP : {response.status_code}")
    print(f" Longueur HTML : {len(response.text)} caractères")
    
    # 2. Chercher du JSON-LD dans la réponse
    soup = BeautifulSoup(response.text, "html.parser")
    json_scripts = soup.find_all("script", type="application/ld+json")
    print(f" Balises JSON-LD trouvées : {len(json_scripts)}")
    
    if json_scripts:
        print("\n Extrait du premier JSON-LD :")
        import json
        try:
            data = json.loads(json_scripts[0].string)
            # Afficher uniquement les champs pertinents
            if "item" in data:
                item = data["item"]
                print(f"   • Titre : {item.get('itemOffered', {}).get('name', data.get('name', 'N/A'))[:80]}...")
                print(f"   • Organisme : {item.get('seller', 'N/A')[:60]}...")
                print(f"   • Date clôture : {item.get('validThrough', 'N/A')}")
                print(f"   • URL : {data.get('identifier', 'N/A')[:70]}...")
        except json.JSONDecodeError:
            print("    JSON invalide ou non lisible")
    
    # 3. Exécuter le parser complet
    print(f"\n Exécution du parser J360BurkinaParser...")
    parser = J360BurkinaParser(TARGET_URL)
    resultats = parser.run()
    
    print(f"\n {len(resultats)} offre(s) extraite(s)")
    
    if resultats:
        print("\n Première offre extraite :")
        for key, value in resultats[0].items():
            print(f"   • {key}: {value}")
        
        # 4. Insérer en base pour vérification admin
        print(f"\n Insertion des {len(resultats)} offre(s) en base de données...")
        from offres.models import SourceScraping
        from django.utils import timezone
        
        source, _ = SourceScraping.objects.get_or_create(
            nom="j360.info Burkina Faso",
            url_racine=TARGET_URL,
            defaults={'frequence_maj': 'Toutes les 12h', 'est_actif': True}
        )
        
        for data in resultats[:5]:  # Limiter à 5 pour le test
            if data.get("url_tdr"):
                obj, created = AppelOffre.objects.update_or_create(
                    url_tdr=data["url_tdr"],
                    defaults={
                        "titre": data["titre"],
                        "organisme": data["organisme"],
                        "description": data["description"][:500],
                        "pays": "BF",
                        "date_publication": data["date_publication"] or timezone.now().date(),
                        "date_cloture": data["date_cloture"],
                        "mode_acquisition": "AUTO",
                        "source_origine": source,
                        "statut": "Ouvert"
                    }
                )
                status = "créée" if created else "mise à jour"
                print(f"   • {data['titre'][:50]}... [{status}]")
        
        total = AppelOffre.objects.filter(mode_acquisition='AUTO').count()
        print(f"\n Total offres scrapées en base : {total}")
        print(" Vérifiez dans l'admin : http://127.0.0.1:8000/admin/offres/appeloffre/")
    else:
        print("\n Aucune offre extraite. Causes possibles :")
        print("   • Le JSON-LD n'est pas présent sur la page liste (seulement pages détail)")
        print("   • Le site bloque le scraping (User-Agent, rate-limit, CAPTCHA)")
        print("   • La structure HTML a changé → ajuster les sélecteurs dans le parser")
        
except requests.exceptions.RequestException as e:
    print(f"\n Erreur réseau : {e}")
    print(" Le site est peut-être inaccessible depuis votre connexion (DNS/Firewall/VPN requis)")
    
except Exception as e:
    print(f"\n Erreur : {type(e).__name__} - {e}")
    import traceback
    traceback.print_exc()