# offres/tasks.py
from celery import shared_task
import logging

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
                <h1>🎉 Bienvenue !</h1>
            </div>
            <div class="content">
                <p>Bonjour{f' {nom}' if nom else ''},</p>
                
                <p>Nous vous confirmons votre inscription à la newsletter de la <strong>Plateforme EXPERTISE-ID</strong>.</p>
                
                <p>Vous recevrez désormais :</p>
                <ul>
                    <li>✅ Les nouvelles offres d'appels d'offres</li>
                    <li>✅ Les alertes personnalisées selon vos critères</li>
                    <li>✅ Les mises à jour importantes de la plateforme</li>
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
        
        logger.info(f"✅ Email de confirmation envoyé à {email}")
        return {'status': 'success', 'email': email}
        
    except Exception as e:
        logger.error(f"❌ Erreur envoi email newsletter à {email}: {e}")
        raise


# ✅ Version Celery pour plus tard
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_newsletter_confirmation_email_async(self, email, nom=''):
    """
    Version asynchrone (Celery) - Pour utilisation future avec Redis
    """
    return send_newsletter_confirmation_email(email, nom)



# ✅ VERSION SYNCHRONE (sans Celery) - Fonctionne sur Windows
def send_password_reset_email(email, token):
    """
    Envoie l'email de réinitialisation de mot de passe (version synchrone)
    """
    try:
        # URL du frontend pour réinitialiser le mot de passe
        reset_url = f"http://localhost:3000/reset-password/{token}"
        
        subject = '🔐 Réinitialisation de votre mot de passe - Plateforme Offres'
        
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
                    padding: 14px 35px;
                    background: #1E3A8A;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .warning {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    font-size: 12px;
                    color: #666;
                }}
                .token-box {{
                    background: #f8f9fa;
                    border: 1px solid #dee2e6;
                    padding: 15px;
                    word-break: break-all;
                    font-family: monospace;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔐 Réinitialisation du mot de passe</h1>
            </div>
            <div class="content">
                <p>Bonjour,</p>
                
                <p>Vous avez demandé la réinitialisation de votre mot de passe pour votre compte sur la <strong>Plateforme EXPERTISE-ID</strong>.</p>
                
                <p style="text-align: center;">
                    <a href="{reset_url}" class="button">Réinitialiser mon mot de passe</a>
                </p>
                
                <div class="warning">
                    <strong>⚠️ Important :</strong>
                    <ul style="margin: 10px 0;">
                        <li>Ce lien est valide pendant <strong>24 heures</strong></li>
                        <li>Il ne peut être utilisé qu'<strong>une seule fois</strong></li>
                        <li>Si vous n'avez pas fait cette demande, ignorez simplement cet email</li>
                    </ul>
                </div>
                
                <p><strong>Si le bouton ne fonctionne pas</strong>, copiez et collez ce lien dans votre navigateur :</p>
                <div class="token-box">{reset_url}</div>
                
                <p>Pour votre sécurité, ne partagez jamais ce lien avec qui que ce soit.</p>
                
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
        Réinitialisation de votre mot de passe
        
        Vous avez demandé la réinitialisation de votre mot de passe.
        
        Cliquez sur ce lien pour réinitialiser votre mot de passe (valide 24h) :
        {reset_url}
        
        Si vous n'avez pas fait cette demande, ignorez cet email.
        
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
        
        logger.info(f"✅ Email de réinitialisation envoyé à {email}")
        return {'status': 'success', 'email': email}
        
    except Exception as e:
        logger.error(f"❌ Erreur envoi email réinitialisation à {email}: {e}")
        raise


# ✅ Gardez aussi la version Celery pour plus tard (quand Redis sera installé)
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email_async(self, email, token):
    """
    Version asynchrone (Celery) - Pour utilisation future avec Redis
    """
    return send_password_reset_email(email, token)