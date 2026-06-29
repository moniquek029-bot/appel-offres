# verifier_filtres.py
"""
Vérifie si les offres retournées par le filtre sont pertinentes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_offres.settings')
django.setup()

from offres.models import AppelOffre
from django.db.models import Q

# Mots-clés informatiques (même liste que dans views.py)
KEYWORDS_INFORMATIQUE = [
    'informatique', 'informatiques', 'informatisation',
    'logiciel', 'logiciels', 'application', 'applications',
    'développement', 'programmation', 'codage',
    'base de données', 'système d\'information',
    'réseau', 'cybersécurité', 'sécurité informatique',
    'serveur', 'cloud', 'infrastructure',
    'site web', 'internet', 'ordinateur', 'matériel informatique',
    'laptop', 'équipement informatique', 'digital', 'numérique',
    'ERP', 'SAP', 'CRM', 'intelligence artificielle', 'IA',
    'IT', 'information technology', 'software',
    'development', 'programming', 'coding',
    'database', 'network', 'cybersecurity',
    'server', 'website', 'computer', 'hardware',
    'informática', 'informatica', 'aplicación',
    'desarrollo', 'programación', 'base de datos',
    'red', 'ciberseguridad', 'servidor', 'nube',
    'sitio web', 'computadora', 'equipo informático',
]

print("=" * 80)
print("🔍 VÉRIFICATION DES OFFRES 'INFORMATIQUE' DU BURKINA FASO")
print("=" * 80)

# Récupérer les offres avec le même filtre que l'API
q_objects = Q()
for kw in KEYWORDS_INFORMATIQUE:
    q_objects |= Q(titre__icontains=kw)
    q_objects |= Q(description__icontains=kw)
    q_objects |= Q(organisme__icontains=kw)

offres = AppelOffre.objects.filter(q_objects, pays='BF').order_by('-date_publication')

print(f"\n📊 Total d'offres trouvées: {offres.count()}\n")

# Analyser chaque offre
offres_valides = []
offres_suspectes = []

for offre in offres:
    titre = offre.titre or ''
    description = offre.description or ''
    organisme = offre.organisme or ''
    texte_complet = (titre + ' ' + description + ' ' + organisme).lower()
    
    # Trouver les mots-clés qui ont matché
    mots_trouves = [kw for kw in KEYWORDS_INFORMATIQUE if kw.lower() in texte_complet]
    
    # Vérifier si c'est vraiment informatique
    is_reellement_informatique = any(kw in mots_trouves for kw in [
        'informatique', 'logiciel', 'software', 'IT', 'digital', 'numérique',
        'ordinateur', 'computer', 'hardware', 'développement', 'development',
        'système d\'information', 'database', 'réseau', 'network',
        'informática', 'software', 'aplicación'
    ])
    
    info = {
        'id': offre.id,
        'titre': titre[:80],
        'organisme': organisme,
        'mots_cles': mots_trouves[:5],
        'valide': is_reellement_informatique
    }
    
    if is_reellement_informatique:
        offres_valides.append(info)
    else:
        offres_suspectes.append(info)

# Afficher les résultats
print("=" * 80)
print("✅ OFFRES VRAIMENT INFORMATIQUES")
print("=" * 80)
for i, offre in enumerate(offres_valides, 1):
    print(f"\n{i}. ID {offre['id']}: {offre['titre']}")
    print(f"   Organisme: {offre['organisme']}")
    print(f"   Mots-clés trouvés: {', '.join(offre['mots_cles'])}")

if offres_suspectes:
    print("\n" + "=" * 80)
    print("⚠️  OFFRES SUSPECTES (pourraient ne pas être informatiques)")
    print("=" * 80)
    for i, offre in enumerate(offres_suspectes, 1):
        print(f"\n{i}. ID {offre['id']}: {offre['titre']}")
        print(f"   Organisme: {offre['organisme']}")
        print(f"   Mots-clés trouvés: {', '.join(offre['mots_cles'])}")

print("\n" + "=" * 80)
print(f"📊 RÉSUMÉ")
print("=" * 80)
print(f"✅ Offres valides: {len(offres_valides)}")
print(f"⚠️  Offres suspectes: {len(offres_suspectes)}")
print(f"📈 Taux de pertinence: {(len(offres_valides)/offres.count()*100):.1f}%")