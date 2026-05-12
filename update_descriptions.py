#!/usr/bin/env python
"""
update_descriptions.py
Script autonome pour mettre à jour les descriptions des offres avec le mock enrichi.
Exécution : python update_descriptions.py
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_offres.settings')
django.setup()

# Imports (après django.setup())
from offres.scraping.parsers.j360_mock import J360MockParser
from offres.models import AppelOffre, SourceScraping

def main():
    print("🔄 Démarrage de la mise à jour des descriptions...")
    
    # 1. Récupérer ou créer la source mock
    source, created = SourceScraping.objects.get_or_create(
        nom="J360 Mock Démo",
        defaults={
            "url_racine": "https://app.j360.info/#/my-monitoring",
            "frequence_maj": "Toutes les 12h",
            "est_actif": True
        }
    )
    if created:
        print(f"✅ Source 'J360 Mock Démo' créée")
    else:
        print(f"✅ Source 'J360 Mock Démo' trouvée")
    
    # 2. Parser les nouvelles données enrichies
    parser = J360MockParser(source.url_racine)
    nouvelles_offres = parser.run()
    print(f"📦 {len(nouvelles_offres)} offre(s) générées par le mock enrichi")
    
    # 3. Mettre à jour la base
    updated_count = 0
    for data in nouvelles_offres:
        obj, created = AppelOffre.objects.update_or_create(
            url_tdr=data["url_tdr"],
            defaults={
                "titre": data["titre"],
                "organisme": data["organisme"],
                "description": data["description"],  # ← Description longue !
                "date_publication": data["date_publication"],
                "date_cloture": data["date_cloture"],
                "mode_acquisition": "AUTO",
                "source_origine": source,
                "statut": "Ouvert",
                "pays": data["pays"]
            }
        )
        if created or obj.description != data["description"]:
            updated_count += 1
    
    print(f"✅ {updated_count} offre(s) mises à jour avec descriptions enrichies")
    
    # 4. Afficher un aperçu
    print(f"\n👀 Aperçu d'une offre mise à jour :")
    offre = AppelOffre.objects.filter(mode_acquisition='AUTO').first()
    if offre:
        print(f"   Titre : {offre.titre[:60]}...")
        print(f"   Description : {len(offre.description)} caractères")
        print(f"   Extrait : {offre.description[:200]}...")
    
    print(f"\n🎉 Mise à jour terminée !")
    print(f"💡 Pour vérifier : ouvrez email_preview.html dans votre navigateur")

if __name__ == "__main__":
    main()