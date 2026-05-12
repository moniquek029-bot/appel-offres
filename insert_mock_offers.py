# insert_mock_offers.py
"""
Script d'insertion d'offres mockées réalistes pour le Burkina Faso.
Permet de tester l'affichage admin et frontend sans accès réseau au site source.
"""
import os
import sys
import django
from datetime import date, timedelta

# =============================================================================
# INITIALISATION DJANGO (obligatoire en tête de script standalone)
# =============================================================================
sys.path.append(r"C:\Users\sebas\Downloads\plateforme_offres")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_offres.settings')
django.setup()
# =============================================================================

from offres.models import AppelOffre, SourceScraping
from django.utils import timezone

print(" Insertion d'offres de test réalistes - Burkina Faso...")
print("=" * 70)

# Créer la source si elle n'existe pas
#  CORRECTION : Ne pas inclure 'description' car ce champ n'existe pas dans SourceScraping
source, created = SourceScraping.objects.get_or_create(
    nom="j360.info Burkina Faso",
    url_racine="https://www.j360.info/appels-d-offres/afrique/burkina-faso/",
    defaults={
        'frequence_maj': 'Toutes les 12 heures',
        'est_actif': True,
    }
)
print(f" Source configurée : {source.nom} {'(créée)' if created else '(existante)'}")

# =============================================================================
# DONNÉES DE TEST RÉALISTES (inspirées de vraies offres BF)
# =============================================================================
mock_offers = [
    {
        "titre": "Recrutement de Consultant pour étude d'avant-projet détaillé - Extension du périmètre irrigué de Bama",
        "organisme": "MINISTERE DE L'AGRICULTURE, DE L'EAU ET DES RESSOURCES ANIMALES",
        "description": "Appel d'offres pour la réalisation d'étude d'avant-projet détaillé de l'extension du périmètre irrigué de Bama dans la commune de Bama, province du Houet, région des Hauts-Bassins. Mission : études techniques, hydrauliques, agronomiques et socio-économiques.",
        "date_publication": date(2026, 5, 8),
        "date_cloture": date(2026, 5, 25),
        "url_tdr": "https://www.j360.info/appels-d-offres/54845360-bama-irrigation/",
        "pays": "BF",
    },
    {
        "titre": "Fourniture et installation de matériel informatique pour 50 écoles primaires de la région du Centre",
        "organisme": "Ministère de l'Éducation Nationale, de l'Alphabétisation et de la Promotion des Langues Nationales",
        "description": "Acquisition de 500 ordinateurs portables, 50 vidéoprojecteurs, équipements réseau et logiciels éducatifs. Livraison, installation et formation des enseignants incluses. Durée d'exécution : 3 mois.",
        "date_publication": date(2026, 5, 1),
        "date_cloture": date(2026, 6, 15),
        "url_tdr": "https://www.j360.info/appels-d-offres/54845361-ecoles-informatique/",
        "pays": "BF",
    },
    {
        "titre": "Consultation pour étude d'impact environnemental et social - Projet routier Bobo-Dioulasso - Banfora",
        "organisme": "Agence Nationale de l'Environnement (ANDE)",
        "description": "Mission d'étude d'impact environnemental et social (EIES) pour le projet de réhabilitation de la route Bobo-Dioulasso - Banfora. Analyse des impacts, plan de gestion environnementale, consultation des parties prenantes.",
        "date_publication": date(2026, 4, 20),
        "date_cloture": date(2026, 5, 30),
        "url_tdr": "https://www.j360.info/appels-d-offres/54845362-route-eies/",
        "pays": "BF",
    },
    {
        "titre": "Marché de travaux : Construction de 10 salles de classes dans la province du Kadiogo",
        "organisme": "Ministère des Infrastructures et du Désenclavement",
        "description": "Construction clé en main de 10 salles de classes de type F+4 avec équipements sanitaires et mobiliers. Accès eau et électricité inclus. Délai d'exécution : 6 mois.",
        "date_publication": date(2026, 5, 5),
        "date_cloture": date(2026, 6, 10),
        "url_tdr": "https://www.j360.info/appels-d-offres/54845363-ecoles-kadiogo/",
        "pays": "BF",
    },
    {
        "titre": "Prestation de services : Audit financier et comptable d'une institution publique",
        "organisme": "Autorité Supérieure de Contrôle d'État (ASCE)",
        "description": "Mission d'audit financier, comptable et de conformité pour l'exercice 2025. Vérification des états financiers, contrôle interne, recommandations d'amélioration. Durée : 2 mois.",
        "date_publication": date(2026, 4, 28),
        "date_cloture": date(2026, 5, 20),
        "url_tdr": "https://www.j360.info/appels-d-offres/54845364-audit-asce/",
        "pays": "BF",
    },
]

# =============================================================================
# INSERTION EN BASE DE DONNÉES
# =============================================================================
print(f"\n Insertion de {len(mock_offers)} offre(s) en base de données...")
print("-" * 70)

inserted_count = 0
for i, data in enumerate(mock_offers, 1):
    try:
        obj, created = AppelOffre.objects.update_or_create(
            url_tdr=data["url_tdr"],  # Clé unique : évite les doublons
            defaults={
                "titre": data["titre"],
                "organisme": data["organisme"],
                "description": data["description"][:500],  # Limite CDC : résumé court
                "pays": data["pays"],
                "date_publication": data["date_publication"],
                "date_cloture": data["date_cloture"],
                "mode_acquisition": "AUTO",  # Marque l'origine automatique
                "source_origine": source,
                "statut": "Ouvert"
            }
        )
        status = " CRÉÉE" if created else " MISE À JOUR"
        print(f"{i}. {data['titre'][:65]}... [{status}]")
        inserted_count += 1
        
    except Exception as e:
        print(f"{i}.  Erreur : {e}")

# =============================================================================
# RÉCAPITULATIF
# =============================================================================
total_offres = AppelOffre.objects.count()
auto_offres = AppelOffre.objects.filter(mode_acquisition='AUTO').count()
ouvert_offres = AppelOffre.objects.filter(statut='Ouvert').count()

print("\n" + "=" * 70)
print(" RÉCAPITULATIF BASE DE DONNÉES")
print("=" * 70)
print(f"   • Total offres en base        : {total_offres}")
print(f"   • Offres scrapées (AUTO)      : {auto_offres}")
print(f"   • Offres ouvertes             : {ouvert_offres}")
print(f"   • Source configurée           : {source.nom}")
print("\n VÉRIFICATION DANS L'ADMIN DJANGO :")
print("    http://127.0.0.1:8000/admin/offres/appeloffre/")
print("    Filtrez par : mode_acquisition = AUTO")
print("=" * 70)
print(" Insertion terminée ! Votre backend est prêt pour le frontend.")