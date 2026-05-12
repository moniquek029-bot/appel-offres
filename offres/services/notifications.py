"""
offres/services/notifications.py
Service centralisé pour la gestion des emails et le matching CV/Offres.
Conforme au CDC Module 4 : "Notification automatisée"
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from offres.models import (
    AppelOffre, CritereRecherche, Notification, SuggestionOffre
)
import logging

logger = logging.getLogger(__name__)

def send_email_notification(user, subject, template_name, context):
    """
    Envoie un email HTML formaté à un utilisateur.
    Utilise les templates Django pour la cohérence du design.
    """
    try:
        html_content = render_to_string(f"emails/{template_name}.html", context)
        text_content = render_to_string(f"emails/{template_name}.txt", context)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f" Email envoyé à {user.email} : {subject}")
        return True
    except Exception as e:
        logger.error(f" Erreur envoi email à {user.email} : {e}")
        return False

def check_and_notify_matches():
    """
     LOGIQUE DE MATCHING (CDC Module 4)
    Scanne les nouvelles offres (créées < 24h) et vérifie si elles correspondent 
    aux critères des Experts.
    """
    today = timezone.now().date()
    yesterday = today - timezone.timedelta(days=1)
    
    # 1. Récupérer les offres récentes (automatiques ou manuelles)
    recent_offers = AppelOffre.objects.filter(
        Q(date_publication__gte=yesterday) | Q(created_at__gte=yesterday),
        statut="Ouvert"
    )
    
    if not recent_offers.exists():
        logger.info(" Aucune nouvelle offre à matcher aujourd'hui.")
        return 0

    notifications_count = 0

    # 2. Parcourir les critères des Experts
    criteria = CritereRecherche.objects.filter(alerte_active=True).select_related('utilisateur')
    
    for critere in criteria:
        user = critere.utilisateur
        if user.role != 'EXPERT':
            continue

        # Parsing des mots-clés (ex: "forage, audit" -> ["forage", "audit"])
        keywords = [kw.strip().lower() for kw in critere.mots_cles.split(',') if kw.strip()]
        
        matching_offers = []
        for offer in recent_offers:
            # Vérification flexible (titre + description)
            title_lower = offer.titre.lower()
            desc_lower = offer.description.lower()
            
            # Si un mot clé est présent dans le titre ou la description
            if any(kw in title_lower or kw in desc_lower for kw in keywords):
                matching_offers.append(offer)

        # 3. Envoyer l'email s'il y a des correspondances
        if matching_offers:
            send_email_notification(
                user=user,
                subject=f" {len(matching_offers)} nouvelle(s) offre(s) correspondant à vos critères",
                template_name="alerte_nouvelles_offres",
                context={
                    'user': user,
                    'offres': matching_offers,
                    'keywords': critere.mots_cles
                }
            )
            
            # 4. Enregistrer dans l'historique (Notification Model)
            Notification.objects.create(
                destinataire=user,
                offre_liee=matching_offers[0], # On lie à la première pour l'historique
                objet=f"Alerte: {len(matching_offers)} offres correspondantes",
                message=f"Correspondance trouvée pour les mots-clés : {critere.mots_cles}",
                est_lue=False
            )
            notifications_count += 1

    logger.info(f"Matching terminé. {notifications_count} experts notifiés.")
    return notifications_count

def notify_expert_suggestion(suggestion: SuggestionOffre):
    """
    Notifie l'expert que l'administrateur l'a suggéré pour une offre.
    """
    user = suggestion.expert.utilisateur
    send_email_notification(
        user=user,
        subject=f" Suggestion pour l'offre : {suggestion.offre.titre}",
        template_name="suggestion_expert",
        context={
            'user': user,
            'offre': suggestion.offre,
            'commentaire': suggestion.commentaire_admin,
            'lien_offre': suggestion.offre.url_tdr
        }
    )
    
    Notification.objects.create(
        destinataire=user,
        offre_liee=suggestion.offre,
        objet="Suggestion Expert",
        message="L'administrateur vous a suggéré pour cette offre.",
        est_lue=False
    )