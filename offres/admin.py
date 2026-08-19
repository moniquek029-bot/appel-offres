# offres/admin.py
from django import forms
from django.contrib import admin
from django.db import models as django_models
from django.utils.html import format_html
from offres.scraping.tasks import run_scheduled_scraping_task  # Import direct pour l'action admin 
from django.contrib.auth.admin import UserAdmin
from django.urls import path

from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import (
    SuggestionOffre, Utilisateur, AppelOffre, SourceScraping, 
    ProfilExpert, CritereRecherche, 
    InscriptionNewsletter, Notification, BureauEtude, HistoriqueConnexion, Message,
    SourceCredentials
)


# =============================================================================
# VUES PERSONNALISÉES POUR LE SCRAPING
# =============================================================================

def run_scraping_view(request, source_id=None):
    """Vue pour lancer le scraping depuis l'admin"""
    try:
        if source_id:
            result = run_scheduled_scraping_task(source_id=source_id)
            messages.success(request, f"✅ Scraping terminé ! {result.get('new', 0)} nouvelles offres, {result.get('updated', 0)} mises à jour.")
        else:
            # Lancer toutes les sources
            sources = SourceScraping.objects.filter(est_actif=True)
            total_new = 0
            total_updated = 0
            for source in sources:
                result = run_scheduled_scraping_task(source_id=source.id)
                total_new += result.get('new', 0)
                total_updated += result.get('updated', 0)
            messages.success(request, f"✅ Scraping terminé sur {sources.count()} sources ! {total_new} nouvelles offres, {total_updated} mises à jour.")
    except Exception as e:
        messages.error(request, f"❌ Erreur lors du scraping: {str(e)}")
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/offres/sourcescraping/'))


def run_scraping_all_view(request):
    """Lancer le scraping sur toutes les sources actives"""
    try:
        sources = SourceScraping.objects.filter(est_actif=True)
        total_new = 0
        total_updated = 0
        for source in sources:
            result = run_scheduled_scraping_task(source_id=source.id)
            total_new += result.get('new', 0)
            total_updated += result.get('updated', 0)
        messages.success(request, f"✅ Scraping terminé sur {sources.count()} sources ! {total_new} nouvelles offres, {total_updated} mises à jour.")
    except Exception as e:
        messages.error(request, f"❌ Erreur: {str(e)}")
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/offres/sourcescraping/'))


# =============================================================================
# CLASSES INLINE POUR LES PROFILS (Version simplifiée sans erreurs)
# =============================================================================

class ProfilExpertInline(admin.StackedInline):
    """Affiche le profil expert dans la fiche utilisateur"""
    model = ProfilExpert
    can_delete = False
    verbose_name_plural = 'Détails Professionnels (Expert)'
    fields = ('domaines_competence', 'autres_competences', 'cv_fichier', 'disponible')
    readonly_fields = ('date_creation', 'date_mise_a_jour')


class BureauEtudeInline(admin.StackedInline):
    """Affiche le profil bureau dans la fiche utilisateur"""
    model = BureauEtude
    can_delete = False
    verbose_name_plural = 'Détails Structure (Bureau)'
    fields = ('nom_structure', 'pays', 'adresse', 'domaine_activite', 
              'email_contact', 'telephone', 'site_web')
    readonly_fields = ('date_creation', 'date_mise_a_jour')


# =============================================================================
# ✅ NOUVEAU : Inline pour les credentials d'authentification
# ✅ DÉPLACÉ AVANT SourceScrapingAdmin pour éviter l'erreur AlreadyRegistered
# =============================================================================

class SourceCredentialsInline(admin.StackedInline):
    """Inline pour gérer les credentials directement dans la page SourceScraping"""
    model = SourceCredentials
    can_delete = True
    verbose_name = "Identifiants d'authentification"
    verbose_name_plural = "Identifiants d'authentification"
    fk_name = 'source'
    
    fieldsets = (
        ('Informations de connexion', {
            'fields': ('username', 'password_display', 'login_url', 'auth_type', 'is_active'),
        }),
        ('Configuration Formulaire HTML', {
            'fields': ('username_field', 'password_field'),
            'classes': ('collapse',),
            'description': 'Configuration pour l\'authentification par formulaire HTML'
        }),
        ('Configuration Selenium', {
            'fields': ('username_selector', 'password_selector', 'submit_selector', 'success_indicator'),
            'classes': ('collapse',),
            'description': 'Configuration pour l\'authentification avec Selenium (sites JavaScript)'
        }),
    )
    
    readonly_fields = ('password_display', 'last_login')
    
    def password_display(self, obj):
        if obj.pk and obj.encrypted_password:
            return "•••••••••••• (chiffré)"
        return "Non défini"
    password_display.short_description = "Mot de passe"


# =============================================================================
# GESTION DES UTILISATEURS (CONTRÔLE DES ACCÈS)
# =============================================================================

@admin.register(Utilisateur)
class CustomUserAdmin(UserAdmin):
    """Gestion des utilisateurs avec affichage des profils inline"""
    
    list_display = ('last_name', 'first_name', 'email', 'telephone', 'pays', 'role', 'is_active')
    ordering = ('email',)
    
    list_display_links = ('email',)
    
    fieldsets = (
        ('Identité', {'fields': ('last_name', 'first_name', 'email', 'genre', 'date_naissance')}),
        ('Contact & Localisation', {'fields': ('telephone', 'adresse', 'pays')}),
        ('Statut & Rôles', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    def get_inlines(self, request, obj=None):
        inlines = []
        if obj:
            if obj.role == 'EXPERT':
                inlines.append(ProfilExpertInline)
            elif obj.role == 'BUREAU':
                inlines.append(BureauEtudeInline)
        return inlines
    
    readonly_fields = ('last_login', 'date_joined')
    
    def has_add_permission(self, request):
        return True
    
    formfield_overrides = {
        django_models.DateField: {
            'widget': forms.SelectDateWidget(years=range(1950, 2040))
        },
    }
    
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('role', 'is_active', 'pays')


# =============================================================================
# GESTION DES OFFRES
# =============================================================================

@admin.register(AppelOffre)
class AppelOffreAdmin(admin.ModelAdmin):
    """L'admin peut publier, mais ne peut pas modifier l'origine d'une offre scrapée."""
    
    list_display = ('titre', 'organisme', 'pays', 'mode_acquisition', 'date_cloture', 'statut')
    list_filter = ('mode_acquisition', 'pays', 'statut')
    search_fields = ('titre', 'organisme')
    ordering = ('-date_publication',)
    
    fieldsets = (
        ('Informations principales', {'fields': ('titre', 'organisme', 'description', 'statut')}),
        ('Dates', {'fields': ('date_publication', 'date_cloture')}),
        ('Localisation', {'fields': ('pays',)}),
        ('Sources', {'fields': ('mode_acquisition', 'url_source', 'url_tdr', 'source_origine')}),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.mode_acquisition == 'AUTO':
            return ('mode_acquisition', 'url_tdr', 'url_source', 'source_origine')
        return ('mode_acquisition',)
    
    def save_model(self, request, obj, form, change):
        if not obj.mode_acquisition:
            obj.mode_acquisition = 'MANUEL'
        super().save_model(request, obj, form, change)


# =============================================================================
# SOURCES DE SCRAPING - AVEC BOUTON "LANCER" ET INLINE CREDENTIALS
# =============================================================================



# =============================================================================
# SOURCES DE SCRAPING - AVEC ACTION SYNCHRONE ET INLINE CREDENTIALS
# =============================================================================

# 1. On définit D'ABORD la fonction d'action (pour qu'elle existe avant la classe)
@admin.action(description='🚀 Lancer le scraping pour les sources sélectionnées')
def lancer_scraping_manuel(modeladmin, request, queryset):
    total_new = 0
    total_updated = 0
    erreurs = 0

    for source in queryset:
        try:
            # .apply() exécute la tâche de manière SYNCHRONE (localement), 
            # contournant totalement le besoin de Redis/Celery !
            resultat = run_scheduled_scraping_task.apply(kwargs={'source_id': source.id}).get()
            
            if isinstance(resultat, dict):
                total_new += resultat.get('new', 0)
                total_updated += resultat.get('updated', 0)
                
        except Exception as e:
            erreurs += 1
            modeladmin.message_user(request, f"❌ Erreur sur '{source.nom}': {str(e)}", messages.ERROR)

    modeladmin.message_user(
        request,
        f"✅ Scraping terminé ! {total_new} nouvelles offres, {total_updated} mises à jour. ({erreurs} erreurs)",
        messages.SUCCESS
    )


# 2. Ensuite, on définit la classe Admin qui utilise cette fonction
@admin.register(SourceScraping)
class SourceScrapingAdmin(admin.ModelAdmin):
    list_display = ['nom', 'url_racine', 'pays', 'parser', 'use_js', 'delay', 'est_actif', 'last_scraped', 'scrape_button']
    list_filter = ['est_actif', 'pays', 'parser']
    search_fields = ['nom', 'url_racine']
    list_editable = ['est_actif', 'delay', 'use_js']
    
    # ✅ On référence la fonction d'action définie juste au-dessus
    actions = [lancer_scraping_manuel]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'url_racine', 'pays', 'est_actif')
        }),
        ('Configuration du scraping', {
            'fields': ('parser', 'use_js', 'delay', 'frequence_maj')
        }),
        ('Métadonnées', {
            'fields': ('last_scraped', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # ✅ Inline des credentials
    inlines = [SourceCredentialsInline]
    
    readonly_fields = ['last_scraped', 'created_at', 'updated_at']
    
    def scrape_button(self, obj):
        """Bouton pour lancer le scraping sur une source"""
        url = f'/admin/run-scraping/{obj.id}/'
        return format_html(
            '<a class="button" href="{}" style="background: #28a745; color: white; padding: 5px 12px; text-decoration: none; border-radius: 3px; font-size: 12px;">🚀 Lancer</a>',
            url
        )
    scrape_button.short_description = 'Scraping'
    
    def get_urls(self):
        """Ajouter des URLs personnalisées pour les boutons individuels"""
        urls = super().get_urls()
        custom_urls = [
            path('run-scraping/<int:source_id>/', self.admin_site.admin_view(run_scraping_view), name='run_scraping'),
            path('run-scraping-all/', self.admin_site.admin_view(run_scraping_all_view), name='run_scraping_all'),
        ]
        return custom_urls + urls
# =============================================================================
# PROFIL EXPERT - LECTURE SEULE POUR L'ADMIN
# =============================================================================

@admin.register(ProfilExpert)
class ProfilExpertAdmin(admin.ModelAdmin):
    """L'administrateur voit les infos clés pour la sélection"""
    
    list_display = ('get_nom_complet', 'domaines_competence', 'get_cv_link', 'disponible', 'date_mise_a_jour')
    search_fields = ('utilisateur__last_name', 'utilisateur__first_name', 'domaines_competence')
    list_filter = ('disponible',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def get_cv_link(self, obj):
        if obj.cv_fichier:
            return format_html('<a href="{}" target="_blank">📄 Voir le CV</a>', obj.cv_fichier.url)
        return " Aucun CV"
    get_cv_link.short_description = "Curriculum Vitae"
    
    def get_nom_complet(self, obj):
        return f"{obj.utilisateur.last_name} {obj.utilisateur.first_name}"
    get_nom_complet.short_description = "Nom de l'Expert"
    
    readonly_fields = ('utilisateur', 'domaines_competence', 'autres_competences', 
                      'cv_fichier', 'disponible', 'date_creation', 'date_mise_a_jour')


# =============================================================================
# PROFIL BUREAU - LECTURE SEULE POUR L'ADMIN
# =============================================================================

@admin.register(BureauEtude)
class BureauEtudeAdmin(admin.ModelAdmin):
    """Gestion du profil Bureau - Lecture seule pour l'admin"""
    
    list_display = ('nom_structure', 'domaine_activite', 'pays', 'telephone', 'email_contact', 'get_gestionnaire')
    search_fields = ('nom_structure', 'email_contact', 'gestionnaire__email', 'gestionnaire__first_name')
    list_filter = ('pays',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def get_gestionnaire(self, obj):
        return f"{obj.gestionnaire.first_name} {obj.gestionnaire.last_name}"
    get_gestionnaire.short_description = "Gestionnaire"
    
    readonly_fields = ('gestionnaire', 'nom_structure', 'pays', 'adresse', 
                      'domaine_activite', 'email_contact', 'telephone', 
                      'site_web', 'date_creation', 'date_mise_a_jour')


# =============================================================================
# CRITÈRES DE RECHERCHE
# =============================================================================

@admin.register(CritereRecherche)
class CritereRechercheAdmin(admin.ModelAdmin):
    list_display = ('get_expert_nom', 'mots_cles', 'pays', 'alerte_active', 'frequence')
    list_filter = ('alerte_active', 'frequence', 'pays')
    search_fields = ('utilisateur__email', 'utilisateur__last_name', 'mots_cles')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def get_expert_nom(self, obj):
        return f"{obj.utilisateur.last_name} {obj.utilisateur.first_name}"
    get_expert_nom.short_description = "Expert"
    
    readonly_fields = ('utilisateur', 'mots_cles', 'pays', 'domaines', 'alerte_active', 'frequence', 'date_creation')


# =============================================================================
# NEWSLETTER - LECTURE SEULE POUR L'ADMIN
# =============================================================================

@admin.register(InscriptionNewsletter)
class InscriptionNewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_inscription')
    search_fields = ('email',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# =============================================================================
# NOTIFICATIONS - LECTURE SEULE POUR L'ADMIN
# =============================================================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('destinataire', 'objet', 'date_envoi', 'est_lue')
    list_filter = ('est_lue', 'date_envoi')
    search_fields = ('destinataire__email', 'objet')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# =============================================================================
# SUGGESTION D'OFFRE - ADMIN PEUT CRÉER
# =============================================================================

@admin.register(SuggestionOffre)
class SuggestionOffreAdmin(admin.ModelAdmin):
    list_display = ('expert', 'offre', 'date_suggestion', 'est_consulte_par_expert')
    list_filter = ('date_suggestion', 'est_consulte_par_expert')
    search_fields = ('expert__utilisateur__last_name', 'offre__titre')
    autocomplete_fields = ['expert', 'offre']
    
    fieldsets = (
        ('Suggestion', {
            'fields': ('expert', 'offre', 'commentaire_admin')
        }),
        ('Statut', {
            'fields': ('est_consulte_par_expert',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('date_suggestion',)
        return ()


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sujet', 'expediteur', 'destinataire', 'date_envoi', 'est_lu')
    list_filter = ('est_lu', 'date_envoi')
    search_fields = ('sujet', 'contenu', 'expediteur__email', 'destinataire__email')
    readonly_fields = ('date_envoi',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(HistoriqueConnexion)
class HistoriqueConnexionAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'date_connexion', 'ip_address')
    list_filter = ('date_connexion',)
    search_fields = ('utilisateur__email', 'ip_address')
    readonly_fields = ('utilisateur', 'date_connexion', 'ip_address', 'user_agent')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False