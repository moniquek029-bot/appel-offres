# offres/services/smart_matching.py
"""
Service de matching intelligent entre experts et offres
Analyse les domaines de compétence et envoie des notifications
"""
import logging
from datetime import date
from django.db.models import Q
from offres.models import AppelOffre, ProfilExpert, Notification
from offres.utils.search_keywords import detecter_domaine

logger = logging.getLogger(__name__)

# Mapping étendu des domaines et mots-clés associés
DOMAINES_KEYWORDS = {
    'IT & Digital': [
        'informatique', 'digital', 'logiciel', 'software', 'plateforme',
        'développement', 'application', 'système', 'base de données',
        'cybersécurité', 'cloud', 'data', 'intelligence artificielle',
        'ordinateur', 'laptop', 'serveur', 'réseau', 'site web',
        'technologie', 'hardware', 'équipement informatique',
    ],
    'Ingénierie & Construction': [
        'construction', 'bâtiment', 'travaux', 'génie civil',
        'réhabilitation', 'infrastructure', 'chantier', 'architecture',
        'rénovation', 'route', 'pont', 'béton', 'matériaux',
    ],
    'Santé & Médical': [
        'santé', 'médical', 'hôpital', 'clinique', 'pharmacie',
        'équipement médical', 'soins', 'patient', 'pharmaceutique',
        'vaccin', 'laboratoire', 'diagnostic', 'traitement',
    ],
    'Agriculture & Alimentation': [
        'agriculture', 'élevage', 'culture', 'semence', 'irrigation',
        'alimentation', 'sécurité alimentaire', 'nourriture',
        'bétail', 'récolte', 'fertilisant', 'agro',
    ],
    'Éducation & Formation': [
        'éducation', 'formation', 'école', 'université', 'pédagogie',
        'apprentissage', 'enseignement', 'curriculum', 'étudiant',
        'formation professionnelle', 'alphabétisation',
    ],
    'Environnement & Climat': [
        'environnement', 'climat', 'énergie', 'renouvelable',
        'écologie', 'développement durable', 'eau', 'assainissement',
        'déforestation', 'biodiversité', 'pollution',
    ],
    'Finance & Comptabilité': [
        'finance', 'comptabilité', 'audit', 'budget', 'fiscal',
        'banque', 'microfinance', 'investissement', 'trésorerie',
    ],
    'Communication & Médias': [
        'communication', 'média', 'vidéo', 'documentaire', 'radio',
        'publicité', 'journal', 'presse', 'télévision', 'production',
    ],
    'Transport & Logistique': [
        'transport', 'logistique', 'véhicule', 'motocyclette',
        'livraison', 'camion', 'fret', 'chaîne d\'approvisionnement',
    ],
    'Social & Égalité': [
        'social', 'égalité', 'femme', 'jeune', 'genre', 'pauvreté',
        'humanitaire', 'droits humains', 'inclusion', 'vulnérable',
    ],
    'Juridique & Droit': [
        'juridique', 'droit', 'loi', 'légal', 'contrat',
        'réglementation', 'justice', 'avocat', 'législation',
    ],
    'Ressources Humaines': [
        'ressources humaines', 'recrutement', 'RH', 'personnel',
        'embauche', 'gestion du personnel', 'formation staff',
    ],
    'Sécurité & Protection': [
        'sécurité', 'protection', 'défense', 'armée', 'police',
        'frontière', 'sûreté', 'militaire', 'garde',
    ],
    'Services & Conseil': [
        'conseil', 'consulting', 'expertise', 'étude',
        'accompagnement', 'assistance technique', 'audit',
    ],
    'Biens & Équipements': [
        'équipement', 'matériel', 'fourniture', 'achat',
        'acquisition', 'bien', 'marchandise',
    ],
}


def detecter_domaines_from_texte(texte: str) -> list[str]:
    """
    Détecte tous les domaines pertinents dans un texte
    Retourne une liste de domaines trouvés
    """
    if not texte:
        return []
    
    texte_lower = texte.lower()
    domaines_trouves = []
    
    for domaine, keywords in DOMAINES_KEYWORDS.items():
        for keyword in keywords:
            if keyword in texte_lower:
                if domaine not in domaines_trouves:
                    domaines_trouves.append(domaine)
                break  # Passer au domaine suivant
    
    return domaines_trouves


def trouver_offres_pour_expert(profil_expert: ProfilExpert) -> list[dict]:
    """
    Trouve toutes les offres qui correspondent aux critères d'un expert
    """
    # Récupérer les domaines de compétence de l'expert
    domaines_str = profil_expert.domaines_competence or ''
    if not domaines_str:
        return []
    
    # Parser les domaines (séparés par virgule)
    domaines_expert = [d.strip() for d in domaines_str.split(',') if d.strip()]
    
    if not domaines_expert:
        return []
    
    # Récupérer les offres actives non expirées
    offres_actives = AppelOffre.objects.filter(
        statut='Ouvert',
        date_cloture__gte=date.today()
    ).order_by('-date_publication')[:100]  # Limiter pour performance
    
    offres_match = []
    
    for offre in offres_actives:
        # Texte complet à analyser
        texte_complet = f"{offre.titre} {offre.description or ''}".lower()
        
        # Détection du domaine de l'offre
        domaine_offre = detecter_domaine(texte_complet)
        
        # Vérifier si le domaine de l'offre correspond à un domaine de l'expert
        match_direct = domaine_offre in domaines_expert
        
        # Vérifier par mots-clés
        match_keywords = False
        for domaine_expert in domaines_expert:
            keywords = DOMAINES_KEYWORDS.get(domaine_expert, [])
            if any(kw in texte_complet for kw in keywords):
                match_keywords = True
                break
        
        if match_direct or match_keywords:
            offres_match.append({
                'offre': offre,
                'domaine_detecte': domaine_offre,
                'match_direct': match_direct,
                'match_keywords': match_keywords,
            })
    
    return offres_match


def notifier_expert_nouvelles_offres(profil_expert: ProfilExpert) -> int:
    """
    Notifie un expert des nouvelles offres correspondant à ses critères
    Retourne le nombre de notifications créées
    """
    offres_match = trouver_offres_pour_expert(profil_expert)
    
    if not offres_match:
        return 0
    
    utilisateur = profil_expert.utilisateur
    count = 0
    
    for match in offres_match:
        offre = match['offre']
        
        # Vérifier si une notification existe déjà pour cette offre
        existe_deja = Notification.objects.filter(
            destinataire=utilisateur,
            offre_liee=offre,
            objet__icontains='Nouvelle offre correspondant'
        ).exists()
        
        if existe_deja:
            continue
        
        # Créer la notification
        try:
            notification = Notification.objects.create(
                destinataire=utilisateur,
                offre_liee=offre,
                objet=f"Nouvelle offre correspondant à vos critères: {offre.titre[:80]}",
                message=f"""Bonjour {utilisateur.first_name or 'Expert'},

Une nouvelle offre correspondant à vos domaines de compétence vient d'être publiée :

{offre.titre}
Organisme: {offre.organisme}
Pays: {offre.pays}
Date de clôture: {offre.date_cloture}
Domaine: {match['domaine_detecte']}

Consultez les détails sur la plateforme pour plus d'informations.

Cordialement,
L'équipe Expertise-ID""",
                type_notification='MATCH_OFFRE',
                est_lue=False
            )
            count += 1
            logger.info(f"🔔 Notification créée pour {utilisateur.email}: {offre.titre[:50]}")
            
        except Exception as e:
            logger.error(f"❌ Erreur création notification: {e}")
            continue
    
    return count


def notifier_tous_les_experts() -> dict:
    """
    Notifie tous les experts des nouvelles offres
    Utilisé par la tâche Celery quotidienne
    """
    profils = ProfilExpert.objects.filter(
        utilisateur__is_active=True,
        domaines_competence__isnull=False
    ).exclude(domaines_competence='')
    
    total_notifs = 0
    experts_notifies = 0
    
    for profil in profils:
        try:
            count = notifier_expert_nouvelles_offres(profil)
            if count > 0:
                total_notifs += count
                experts_notifies += 1
                logger.info(f"✅ {profil.utilisateur.email}: {count} nouvelles offres")
        except Exception as e:
            logger.error(f"❌ Erreur pour {profil.utilisateur.email}: {e}")
    
    return {
        'experts_notifies': experts_notifies,
        'total_notifications': total_notifs,
        'total_experts': profils.count()
    }

import logging
from django.utils import timezone
from datetime import timedelta
from offres.models import AppelOffre, Utilisateur, Notification
from offres.services.email_service import EmailService

logger = logging.getLogger(__name__)

def notifier_tous_les_experts():
    """
    Envoie des notifications à TOUS les experts pour les nouvelles offres des dernières 24h
    """
    hier = timezone.now() - timedelta(days=1)
    nouvelles_offres = AppelOffre.objects.filter(
        date_scraping__gte=hier,
        statut='Ouvert',
        type_offre='APPEL_D_OFFRES'
    )
    
    if not nouvelles_offres.exists():
        logger.info("ℹ️ Aucune nouvelle offre à notifier aux experts")
        return 0
    
    experts = Utilisateur.objects.filter(role='EXPERT', is_active=True)
    total_notifications = 0
    
    for expert in experts:
        try:
            if not hasattr(expert, 'profil_expert') or not expert.profil_expert.domaines_competence:
                continue
            
            domaines = [d.strip() for d in expert.profil_expert.domaines_competence.split(',')]
            offres_match = nouvelles_offres.filter(domaine__in=domaines)
            
            if not offres_match.exists():
                continue
            
            # Créer les notifications internes (max 5 pour éviter le spam)
            for offre in offres_match[:5]:
                Notification.objects.get_or_create(
                    destinataire=expert,
                    offre_liee=offre,
                    objet=f"Nouvelle offre: {offre.titre[:80]}",
                    defaults={'est_lue': False, 'message': f"Correspond à vos critères: {offre.domaine}"}
                )
                total_notifications += 1
            
            # Envoyer l'email récapitulatif
            EmailService.send_nouvelles_offres_notification(
                expert_email=expert.email,
                expert_name=f"{expert.first_name} {expert.last_name}".strip() or expert.email,
                offres=list(offres_match[:5])
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur notification expert {expert.email}: {e}")
    
    logger.info(f"✅ {total_notifications} notifications envoyées à {experts.count()} experts")
    return total_notifications


def notifier_tous_les_bureaux():
    """
    Envoie des notifications à TOUS les bureaux d'études pour les nouvelles offres des dernières 24h
    """
    hier = timezone.now() - timedelta(days=1)
    nouvelles_offres = AppelOffre.objects.filter(
        date_scraping__gte=hier,
        statut='Ouvert',
        type_offre='APPEL_D_OFFRES'
    )
    
    if not nouvelles_offres.exists():
        logger.info("ℹ️ Aucune nouvelle offre à notifier aux bureaux")
        return 0
    
    bureaux = Utilisateur.objects.filter(role='BUREAU', is_active=True)
    total_notifications = 0
    
    for bureau_user in bureaux:
        try:
            if not hasattr(bureau_user, 'bureauetude'):
                continue
            
            bureau = bureau_user.bureauetude
            
            # Filtrer par domaine d'activité du bureau, ou par pays si vide
            if bureau.domaine_activite:
                offres_match = nouvelles_offres.filter(domaine__iexact=bureau.domaine_activite)
            else:
                pays = str(bureau.pays) if bureau.pays else 'BF'
                offres_match = nouvelles_offres.filter(pays=pays)
            
            if not offres_match.exists():
                continue
            
            # Créer les notifications internes (max 5)
            for offre in offres_match[:5]:
                Notification.objects.get_or_create(
                    destinataire=bureau_user,
                    offre_liee=offre,
                    objet=f"Nouvelle offre: {offre.titre[:80]}",
                    defaults={'est_lue': False, 'message': f"Opportunité pour votre structure"}
                )
                total_notifications += 1
            
            # Envoyer l'email récapitulatif
            EmailService.send_nouvelles_offres_notification(
                expert_email=bureau_user.email,
                expert_name=bureau.nom_structure or bureau_user.email,
                offres=list(offres_match[:5])
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur notification bureau {bureau_user.email}: {e}")
    
    logger.info(f"✅ {total_notifications} notifications envoyées à {bureaux.count()} bureaux")
    return total_notifications


