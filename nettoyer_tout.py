# nettoyer_tout.py
"""
Nettoyage AGRESSIF de toutes les offres non-valides
"""
import os
import sys
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_offres.settings')
django.setup()

from offres.models import AppelOffre

def nettoyer_agressif(dry_run=True):
    """Nettoyage avec critères très stricts"""
    
    # Mots-clés qui DOIVENT être présents
    MOTS_CLES_VALIDES = [
        'appel d\'offre', 'appel d\'offres', 'appels d\'offres',
        'call for tender', 'call for tenders', 'call for proposal', 'call for proposals',
        'invitation to bid', 'request for proposal', 'request for quotation',
        'terms of reference', 'procurement', 'tender document',
        'avis de marché', 'avis d\'attribution', 'manifestation d\'intérêt',
        'recrutement d\'un', 'recrutement d\'une', 'bureau d\'études',
        'consultant', 'consulting', 'consulting firm',
        'marché public', 'marchés publics', 'cahier des charges',
        'expression of interest', 'bidding',
    ]
    
    # Mots-clés de rejet ABSOLU
    MOTS_REJET_ABSOLU = [
        'earthquake', 'flood', 'cyclone', 'typhoon', 'hurricane',
        'tsunami', 'landslide', 'drought', 'famine',
        'cholera', 'ebola', 'measles', 'dengue', 'diphtheria',
        'outbreak', 'epidemic', 'pandemic',
        'world news', 'news in brief', 'press release',
        'annual report', 'rapport annuel',
        'trending data', 'feature story',
        'careers', 'vacancies', 'jobs',
        'conference', 'summit', 'workshop',
        'environmental & social',
        'financing products',
        'bonds & investment',
    ]
    
    print("=" * 80)
    print("🧹 NETTOYAGE AGRESSIF DES OFFRES")
    print("=" * 80)
    
    toutes_offres = AppelOffre.objects.all()
    total = toutes_offres.count()
    
    print(f"\n📊 Total: {total} offres\n")
    
    a_supprimer = []
    valides = []
    
    for offre in toutes_offres:
        titre = (offre.titre or '').lower()
        desc = (offre.description or '').lower()
        texte = titre + ' ' + desc
        
        # Vérifier rejet absolu
        est_rejete = any(mot in texte for mot in MOTS_REJET_ABSOLU)
        
        # Vérifier présence mots-clés valides
        a_mot_valide = any(mot in texte for mot in MOTS_CLES_VALIDES)
        
        if est_rejete or not a_mot_valide:
            raison = []
            if est_rejete:
                raison.append("contenu rejeté")
            if not a_mot_valide:
                raison.append("pas de mots-clés valides")
            
            a_supprimer.append({
                'id': offre.id,
                'titre': offre.titre[:60] if offre.titre else '',
                'raison': ', '.join(raison)
            })
        else:
            valides.append(offre.id)
    
    print(f"✅ Offres valides: {len(valides)}")
    print(f"❌ À supprimer: {len(a_supprimer)}")
    print(f"📈 Taux: {(len(valides)/total*100):.1f}%\n")
    
    if a_supprimer and not dry_run:
        print("🗑️  SUPPRESSION EN COURS...\n")
        ids = [o['id'] for o in a_supprimer]
        
        # Supprimer PDF
        for offre in AppelOffre.objects.filter(id__in=ids):
            if offre.fichier_pdf:
                try:
                    offre.fichier_pdf.delete(save=False)
                except:
                    pass
        
        count, _ = AppelOffre.objects.filter(id__in=ids).delete()
        print(f"✅ {count} offre(s) supprimée(s)")
    
    elif a_supprimer:
        print(" EXEMPLES D'OFFRES À SUPPRIMER:\n")
        for i, offre in enumerate(a_supprimer[:10], 1):
            print(f"{i}. ID {offre['id']}: {offre['titre']}...")
            print(f"   Raison: {offre['raison']}\n")
        
        print("💡 Pour supprimer, exécutez:")
        print("   python nettoyer_tout.py --execute\n")
    
    print("=" * 80)
    return len(a_supprimer)

if __name__ == '__main__':
    dry = '--execute' not in sys.argv
    if dry:
        print("⚠️  MODE SIMULATION\n")
    else:
        print("⚠️  MODE EXÉCUTION\n")
        if input("Confirmer (OUI): ").strip().upper() != 'OUI':
            print("❌ Annulé")
            sys.exit(0)
    
    nettoyer_agressif(dry_run=dry)