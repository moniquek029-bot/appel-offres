# offres/services/email_service.py
"""
Service centralisé pour l'envoi d'emails
Utilise Django's send_mail avec configuration SMTP
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service d'envoi d'emails avec templates HTML"""
    
    @staticmethod
    def send_email(subject, message, recipient_list, html_message=None):
        """Envoie un email simple"""
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"✅ Email envoyé à {recipient_list}: {subject}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur envoi email à {recipient_list}: {e}")
            return False
    
    @staticmethod
    def send_newsletter_confirmation(email, nom=None):
        """Email de confirmation d'inscription à la newsletter"""
        subject = "✅ Confirmation de votre inscription à notre newsletter"
        
        html_message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">🎉 Bienvenue !</h1>
            </div>
            
            <div style="padding: 30px; background: #f9fafb;">
                <p>Bonjour{f' {nom}' if nom else ''},</p>
                
                <p>Nous vous confirmons votre inscription à notre newsletter <strong>Expertise-ID</strong>.</p>
                
                <p>Vous recevrez désormais :</p>
                <ul>
                    <li>📧 Les nouveaux appels d'offres correspondant à vos critères</li>
                    <li>🔔 Des alertes personnalisées selon votre profil</li>
                    <li>📊 Des analyses et tendances du marché</li>
                </ul>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{settings.FRONTEND_URL}/offres" 
                       style="background: #1E3A8A; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Explorer les offres
                    </a>
                </div>
                
                <p style="color: #6b7280; font-size: 12px;">
                    Si vous ne souhaitez plus recevoir ces emails, 
                    <a href="{settings.FRONTEND_URL}/desinscription">cliquez ici</a>.
                </p>
            </div>
            
            <div style="background: #f3f4f6; padding: 20px; text-align: center; font-size: 12px; color: #6b7280;">
                <p>© 2026 Expertise-ID - Tous droits réservés</p>
            </div>
        </div>
        """
        
        text_message = f"""
        Bonjour{f' {nom}' if nom else ''},
        
        Nous vous confirmons votre inscription à notre newsletter Expertise-ID.
        
        Vous recevrez désormais :
        - Les nouveaux appels d'offres correspondant à vos critères
        - Des alertes personnalisées selon votre profil
        - Des analyses et tendances du marché
        
        Explorer les offres : {settings.FRONTEND_URL}/offres
        
        © 2026 Expertise-ID
        """
        
        return EmailService.send_email(
            subject=subject,
            message=text_message,
            recipient_list=[email],
            html_message=html_message
        )
    
    @staticmethod
    def send_new_message_notification(recipient_email, sender_name, subject, message_preview):
        """Notification d'un nouveau message"""
        email_subject = f"📩 Nouveau message de {sender_name}"
        
        html_message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #3B82F6; padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">📩 Nouveau message</h1>
            </div>
            
            <div style="padding: 30px; background: #f9fafb;">
                <p>Vous avez reçu un nouveau message de <strong>{sender_name}</strong>.</p>
                
                <div style="background: white; padding: 20px; border-left: 4px solid #3B82F6; margin: 20px 0;">
                    <p><strong>Sujet :</strong> {subject}</p>
                    <p><strong>Message :</strong></p>
                    <p style="color: #374151;">{message_preview}</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{settings.FRONTEND_URL}/messages" 
                       style="background: #3B82F6; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px;">
                        Lire le message complet
                    </a>
                </div>
            </div>
        </div>
        """
        
        return EmailService.send_email(
            subject=email_subject,
            message=f"Vous avez reçu un nouveau message de {sender_name}.\n\nSujet: {subject}\n\n{message_preview}\n\nConnectez-vous pour lire le message complet.",
            recipient_list=[recipient_email],
            html_message=html_message
        )
    
    @staticmethod
    def send_alerte_offres_matching(user_email, user_name, offres_correspondantes):
        """Alerte email pour les offres correspondant aux critères"""
        if not offres_correspondantes:
            return False
        
        subject = f"🔔 {len(offres_correspondantes)} nouvelle(s) offre(s) correspondant à vos critères"
        
        offres_html = ""
        for offre in offres_correspondantes[:10]:  # Max 10 offres
            offres_html += f"""
            <div style="background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #10B981;">
                <h3 style="margin: 0 0 10px 0; color: #1F2937;">{offre.titre}</h3>
                <p style="margin: 5px 0; color: #6B7280;">
                    <strong>Organisme :</strong> {offre.organisme}<br>
                    <strong>Pays :</strong> {offre.pays}<br>
                    <strong>Date limite :</strong> {offre.date_cloture.strftime('%d/%m/%Y') if offre.date_cloture else 'Non spécifiée'}
                </p>
                <a href="{settings.FRONTEND_URL}/offre/{offre.id}" 
                   style="color: #3B82F6; text-decoration: none;">
                    Voir l'offre →
                </a>
            </div>
            """
        
        html_message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">🔔 Alertes personnalisées</h1>
            </div>
            
            <div style="padding: 30px; background: #f9fafb;">
                <p>Bonjour {user_name},</p>
                
                <p>Nous avons trouvé <strong>{len(offres_correspondantes)} nouvelle(s) offre(s)</strong> correspondant à vos critères de recherche.</p>
                
                {offres_html}
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{settings.FRONTEND_URL}/offres" 
                       style="background: #10B981; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px;">
                        Voir toutes les offres
                    </a>
                </div>
                
                <p style="color: #6b7280; font-size: 12px;">
                    Vous recevez cet email car vous avez configuré des alertes dans votre profil.
                    <a href="{settings.FRONTEND_URL}/profil/criteres">Gérer mes critères</a>
                </p>
            </div>
        </div>
        """
        
        return EmailService.send_email(
            subject=subject,
            message=f"Bonjour {user_name},\n\nNous avons trouvé {len(offres_correspondantes)} nouvelle(s) offre(s) correspondant à vos critères.\n\nConnectez-vous pour les consulter.",
            recipient_list=[user_email],
            html_message=html_message
        )
    
    @staticmethod
    def send_suggestion_notification(expert_email, expert_name, offre_titre, admin_name="L'administrateur"):
        """Notification d'une nouvelle suggestion d'offre"""
        subject = f"💡 Nouvelle suggestion d'offre : {offre_titre[:50]}"
        
        html_message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">💡 Nouvelle suggestion</h1>
            </div>
            
            <div style="padding: 30px; background: #f9fafb;">
                <p>Bonjour {expert_name},</p>
                
                <p>{admin_name} vous suggère une offre qui pourrait correspondre à votre profil :</p>
                
                <div style="background: white; padding: 20px; border-left: 4px solid #F59E0B; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #1F2937;">{offre_titre}</h3>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{settings.FRONTEND_URL}/expert/suggestions" 
                       style="background: #F59E0B; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px;">
                        Voir la suggestion
                    </a>
                </div>
            </div>
        </div>
        """
        
        return EmailService.send_email(
            subject=subject,
            message=f"Bonjour {expert_name},\n\n{admin_name} vous suggère l'offre : {offre_titre}\n\nConnectez-vous pour consulter la suggestion.",
            recipient_list=[expert_email],
            html_message=html_message
        )