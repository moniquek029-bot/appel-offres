# offres/tasks.py
from celery import shared_task
import logging

from django.db.models import Q
from offres.models import CritereRecherche, AppelOffre, Utilisateur
from offres.services.email_service import EmailService
from django.utils import timezone
from datetime import timedelta



logger = logging.getLogger(__name__)


@shared_task
def test_task():
    """Tâche de test simple."""
    logger.info(" Tâche de test exécutée !")
    return " Test OK"


#  Pour importer les tâches de scraping, fates-le DANS une fonction, pas au niveau module :
def register_scraping_tasks():
    """Enregistre les tâches de scraping (appelé après chargement Django)."""
    try:
        from offres.scraping.tasks import (
            run_scheduled_scraping_task,
            daily_archive_task,
            daily_alert_matching_task,
        )
        return True
    except ImportError as e:
        logger.warning(f" Import scraping tasks : {e}")
        return False
    # offres/tasks.py - Ajouter à la fin du fichier

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
# ✅ VERSION SYNCHRONE (sans Celery)
def send_newsletter_confirmation_email(email, nom=''):
    """
    Envoie l'email de confirmation de newsletter (version synchrone)
    """
    try:
        subject = '✅ Confirmation d\'inscription à la newsletter - EXPERTISE-ID'
        
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #1E3A8A 0%, #172554 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #1E3A8A;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1> Bienvenue !</h1>
            </div>
            <div class="content">
                <p>Bonjour{f' {nom}' if nom else ''},</p>
                
                <p>Nous vous confirmons votre inscription à la newsletter de la <strong>Plateforme EXPERTISE-ID</strong>.</p>
                
                <p>Vous recevrez désormais :</p>
                <ul>
                    <li> Les nouvelles offres d'appels d'offres</li>
                    <li> Les alertes personnalisées selon vos critères</li>
                    <li> Les mises à jour importantes de la plateforme</li>
                </ul>
                
                <p style="text-align: center;">
                    <a href="http://localhost:3000" class="button">Visiter la plateforme</a>
                </p>
                
                <p>Si vous ne souhaitez plus recevoir ces emails, vous pouvez vous désinscrire à tout moment.</p>
                
                <p>Cordialement,<br>
                <strong>L'équipe EXPERTISE-ID</strong></p>
            </div>
            <div class="footer">
                <p>Cet email a été envoyé automatiquement. Merci de ne pas y répondre.</p>
                <p>© 2026 Plateforme EXPERTISE-ID</p>
            </div>
        </body>
        </html>
        """
        
        plain_message = f"""
        Bienvenue {nom if nom else ''} !
        
        Nous vous confirmons votre inscription à la newsletter de la Plateforme EXPERTISE-ID.
        
        Vous recevrez désormais :
        - Les nouvelles offres d'appels d'offres
        - Les alertes personnalisées selon vos critères
        - Les mises à jour importantes de la plateforme
        
        Visitez la plateforme : http://localhost:3000
        
        Cordialement,
        L'équipe EXPERTISE-ID
        """
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f" Email de confirmation envoyé à {email}")
        return {'status': 'success', 'email': email}
        
    except Exception as e:
        logger.error(f" Erreur envoi email newsletter à {email}: {e}")
        raise


# ✅ Version Celery pour plus tard
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_newsletter_confirmation_email_async(self, email, nom=''):
    """
    Version asynchrone (Celery) - Pour utilisation future avec Redis
    """
    return send_newsletter_confirmation_email(email, nom)


from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_password_reset_email(user_email, token):
    """Envoie l'email de réinitialisation de mot de passe"""
    
    # ✅ URL du frontend (pas du backend !)
    FRONTEND_URL = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    subject = " Réinitialisation de votre mot de passe - Expertise-ID"
    
    html_message = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0;"> Réinitialisation du mot de passe</h1>
        </div>
        
        <div style="padding: 30px; background: #f9fafb;">
            <p>Bonjour,</p>
            
            <p>Vous avez demandé la réinitialisation de votre mot de passe. Cliquez sur le bouton ci-dessous pour définir un nouveau mot de passe :</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}" 
                   style="background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); 
                          color: white; padding: 14px 35px; text-decoration: none; 
                          border-radius: 5px; display: inline-block; font-weight: bold;">
                    Réinitialiser mon mot de passe
                </a>
            </div>
            
            <p style="color: #6b7280; font-size: 14px;">
                Ou copiez ce lien dans votre navigateur :<br>
                <a href="{reset_link}" style="color: #3B82F6; word-break: break-all;">{reset_link}</a>
            </p>
            
            <div style="background: #FEF3C7; padding: 15px; border-left: 4px solid #F59E0B; margin: 20px 0;">
                <p style="margin: 0; color: #92400E;">
                    <strong> Important :</strong> Ce lien est valide pendant <strong>24 heures</strong> et ne peut être utilisé qu'une seule fois.
                </p>
            </div>
            
            <p style="color: #6b7280; font-size: 14px;">
                Si vous n'avez pas demandé cette réinitialisation, ignorez simplement cet email.
            </p>
        </div>
        
        <div style="background: #f3f4f6; padding: 20px; text-align: center; font-size: 12px; color: #6b7280;">
            <p>© 2026 Expertise-ID - Tous droits réservés</p>
        </div>
    </div>
    """
    
    text_message = f"""
    Réinitialisation de votre mot de passe
    
    Bonjour,
    
    Vous avez demandé la réinitialisation de votre mot de passe.
    Cliquez sur le lien ci-dessous pour définir un nouveau mot de passe :
    
    {reset_link}
    
    Ce lien est valide pendant 24 heures et ne peut être utilisé qu'une seule fois.
    
    Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.
    
    © 2026 Expertise-ID
    """
    
    try:
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"✅ Email de réinitialisation envoyé à {user_email}")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur envoi email: {e}")
        return False
# ✅ Gardez aussi la version Celery pour plus tard (quand Redis sera installé)
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email_async(self, email, token):
    """
    Version asynchrone (Celery) - Pour utilisation future avec Redis
    """
    return send_password_reset_email(email, token)




@shared_task
def send_matching_alerts_task():
    """
    Tâche quotidienne : envoie des emails aux experts
    pour les nouvelles offres correspondant à leurs critères
    """
    try:
        # Récupérer tous les critères de recherche
        criteres = CritereRecherche.objects.select_related('utilisateur').all()
        
        # Grouper par utilisateur
        users_criteres = {}
        for critere in criteres:
            user_id = critere.utilisateur.id
            if user_id not in users_criteres:
                users_criteres[user_id] = {
                    'user': critere.utilisateur,
                    'criteres': []
                }
            users_criteres[user_id]['criteres'].append(critere)
        
        alerts_sent = 0
        
        for user_id, data in users_criteres.items():
            user = data['user']
            criteres_list = data['criteres']
            
            # Construire la requête pour trouver les offres correspondantes
            # On cherche les offres des dernières 24h
            since = timezone.now() - timedelta(hours=24)
            
            q_objects = Q()
            for critere in criteres_list:
                if critere.mots_cles:
                    q_objects |= (
                        Q(titre__icontains=critere.mots_cles) |
                        Q(description__icontains=critere.mots_cles) |
                        Q(organisme__icontains=critere.mots_cles)
                    )
                if critere.pays:
                    q_objects &= Q(pays=critere.pays)
            
            if not q_objects:
                continue
            
            # Récupérer les offres correspondantes
            offres = AppelOffre.objects.filter(
                q_objects,
                date_publication__gte=since,
                statut='Ouvert'
            ).distinct()[:10]
            
            if offres.exists():
                # Envoyer l'email
                user_name = f"{user.first_name} {user.last_name}".strip() or user.email
                email_sent = EmailService.send_alerte_offres_matching(
                    user_email=user.email,
                    user_name=user_name,
                    offres_correspondantes=list(offres)
                )
                
                if email_sent:
                    alerts_sent += 1
                    logger.info(f"✅ Alerte envoyée à {user.email} ({offres.count()} offres)")
        
        logger.info(f" {alerts_sent} alertes envoyées au total")
        return {'alerts_sent': alerts_sent}
        
    except Exception as e:
        logger.error(f" Erreur send_matching_alerts_task: {e}")
        return {'error': str(e)}