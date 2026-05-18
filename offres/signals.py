# offres/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import ProfilExpert, BureauEtude

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Crée automatiquement le profil lié quand un utilisateur est créé"""
    if created:
        if instance.role == 'EXPERT':
            ProfilExpert.objects.create(utilisateur=instance)
        elif instance.role == 'BUREAU_ETUDE':
            BureauEtude.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """Sauvegarde automatiquement le profil lié"""
    if hasattr(instance, 'profil_expert'):
        instance.profil_expert.save()
    elif hasattr(instance, 'bureau_etude'):
        instance.bureau_etude.save()