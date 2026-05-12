from django import forms
from django.contrib import admin

# Register your models here.
from django.db import models as django_models
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
from .models import (
    SuggestionOffre, Utilisateur, AppelOffre, SourceScraping, 
    ProfilExpert, CritereRecherche, 
    InscriptionNewsletter, Notification, BureauEtude
)
from .models import Utilisateur

#Pour éviter les redondances et garantir l'intégrité des données, on crée des classes d'administration personnalisées pour chaque modèle avec des permissions spécifiques à chaque rôle d'utilisateur. L'administrateur peut gérer les offres et les utilisateurs, mais ne peut pas modifier les profils d'experts ou de bureaux d'étude qui doivent être créés par les utilisateurs eux-mêmes.
class ProfilExpertInline(admin.StackedInline):
    model = ProfilExpert
    can_delete = False
    verbose_name_plural = 'Détails Professionnels (Expert)'

class BureauEtudeInline(admin.StackedInline):
    model = BureauEtude
    can_delete = False
    verbose_name_plural = 'Détails Structure (Bureau)'

# GESTION DES UTILISATEURS (CONTRÔLE DES ACCÈS)
@admin.register(Utilisateur)
class CustomUserAdmin(UserAdmin):
    # Liste principale (colonnes)
    list_display = ('last_name', 'first_name', 'email', 'telephone', 'pays', 'role', 'is_active')
    
    # On force le tri par email c
    ordering = ('email',)

    # Organisation du formulaire de consultation
    fieldsets = (
        ('Identité', {'fields': ('last_name', 'first_name', 'email', 'genre', 'date_naissance')}),
        ('Contact & Localisation', {'fields': ('telephone', 'adresse', 'pays')}),
        ('Statut & Rôles', {'fields': ('role', 'is_active', 'is_staff')}),
    )

    # Indispensable quand on n'a pas de username :
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password'),
        }),
    )
    # On ajoute les détails pro directement en bas de la fiche utilisateur
    def get_inlines(self, request, obj=None):
        if obj and obj.role == 'EXPERT':
            return [ProfilExpertInline]
        if obj and obj.role == 'BUREAU':
            return [BureauEtudeInline]
        return []

    # L'admin peut tout voir tout les informations d'un utilisateur, mais ne peut pas les modifier pour garantir l'intégrité des données
    readonly_fields = ('last_login', 'date_joined')
    
    def has_add_permission(self, request):
        return False 
    
    formfield_overrides = {
        django_models.DateField: {
            'widget': forms.SelectDateWidget(
                years=range(1950, 2040) # Affiche de 1950 à 2040
            )
        },
    }
# GESTION DES OFFRES (L'ADMINISTRATEUR PEUT PUBLIER DES OFFRES MANUELLEMENT, MAIS NE PEUT PAS MODIFIER LES OFFRES SCRAPÉES POUR GARANTIR L'INTÉGRITÉ DES DONNÉES)

@admin.register(AppelOffre)
class AppelOffreAdmin(admin.ModelAdmin):
    """
    L'admin peut publier, mais ne peut pas modifier l'origine d'une offre scrapée.
    """
    list_display = ('titre', 'organisme', 'pays', 'mode_acquisition', 'date_cloture')
    list_filter = ('mode_acquisition', 'pays', 'statut')
    #Recherche par titre et organisme
    search_fields = ('titre', 'organisme')

    # Protection de l'intégrité des données
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.mode_acquisition == 'AUTO':
    # Si l'offre vient du scraping, l'administrateur ne peut pas changer l'URL ni la source
            return ('mode_acquisition', 'url_tdr', 'source_origine')
        return ('mode_acquisition',)



#GESTION DES PROFILS D'EXPERTS ET BUREAUX (L'ADMINISTRATEUR NE PEUT PAS MODIFIER CES PROFILS, SEULEMENT LES SUPPRIMER SI SUSPECTS)

class ReadOnlyMetadataAdmin(admin.ModelAdmin):
    """
    Classe de base pour empêcher l'admin d'ajouter ou modifier 
    des profils qui doivent être créés par les utilisateurs eux-mêmes.
    """
    def has_add_permission(self, request):
        return False # Désactive le bouton "Ajouter"

    def has_change_permission(self, request, obj=None):
        return False # Désactive la modification des champs

#
@admin.register(BureauEtude)
class BureauEtudeAdmin(ReadOnlyMetadataAdmin):
    list_display = ('nom_structure', 'domaine_activite', 'gestionnaire')



# Les autres modules : SOURCES DE SCRAPING, NEWSLETTER, NOTIFICATIONS, CRITÈRES DE RECHERCHE

# =============================================================================
# AJOUT : Action personnalisée pour lancer le scraping manuellement
# =============================================================================

@admin.register(SourceScraping)
class SourceScrapingAdmin(admin.ModelAdmin):
    list_display = ('nom', 'url_racine', 'frequence_maj', 'est_actif')
    list_filter = ('est_actif',)
    search_fields = ('nom', 'url_racine')
    
    #  Ajout de l'action personnalisée dans la liste des actions admin
    actions = ['lancer_scraping_selection']
    
    @admin.action(
        description=" Lancer le scraping pour les sources sélectionnées",
        permissions=['change']  # Seul un admin avec permission "change" peut lancer
    )
    def lancer_scraping_selection(self, request, queryset):
        """
        Action admin : Lance immédiatement le scraping pour les sources cochées.
        Utilise Celery pour exécuter la tâche en arrière-plan.
        """
        from offres.scraping.tasks import run_scheduled_scraping_task
        
        count = 0
        for source in queryset:
            if source.est_actif:
                # Lance la tâche Celery pour CETTE source uniquement
                # On passe l'ID de la source pour filtrer dans la tâche
                run_scheduled_scraping_task.delay(source_id=source.id)
                count += 1
        
        if count > 0:
            self.message_user(
                request,
                f" Scraping lancé pour {count} source(s) active(s). "
                f"Vérifiez les logs du worker Celery pour suivre l'exécution.",
                level="success"
            )
        else:
            self.message_user(
                request,
                " Aucune source active sélectionnée. Cochez une source avec 'Est actif = Oui'.",
                level="warning"
            )

# --- NEWSLETTER : AUCUN AJOUT, AUCUNE MODIFICATION ---
@admin.register(InscriptionNewsletter)
class InscriptionNewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_inscription')
    
    #L'administrateur ne peut pas créer une inscription à la newsletter manuellement
    def has_add_permission(self, request):
        return False 

# L'administrateur ne peut pas modifier une inscription à la newsletter mais peut la supprimer
    def has_change_permission(self, request, obj=None):
        return False 


# --- NOTIFICATIONS : L'ADMINISTRATEUR NE PEUT PAS CRÉER OU MODIFIER DES NOTIFICATIONS, SEULEMENT LES SUPPRIMER SI NÉCESSAIRE ---
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('destinataire', 'objet', 'date_envoi', 'est_lue')
    

    #L'administrateur ne peut pas créer de notification manuellement
    def has_add_permission(self, request):
        return False

#L'administrateur ne peut pas modifier une notification mais peut le supprimer
    def has_change_permission(self, request, obj=None):
        return False 


#L'administrateur doit pouvoir choisir l'expert à suggerer et l'offre
# offres/admin.py

@admin.register(SuggestionOffre)
class SuggestionOffreAdmin(admin.ModelAdmin):
    list_display = ('expert', 'offre', 'date_suggestion', 'est_consulte_par_expert')
    list_filter = ('date_suggestion', 'est_consulte_par_expert')
    search_fields = ('expert__utilisateur__last_name', 'offre__titre')
    
    # L'admin choisit l'expert et l'offre dans des listes déroulantes
    autocomplete_fields = ['expert', 'offre']




@admin.register(ProfilExpert)
class ProfilExpertAdmin(admin.ModelAdmin):
    # L'administrateur voit les infos clés pour la sélection
    list_display = ('get_nom_complet', 'domaine_competence', 'get_cv_link', 'date_mise_a_jour')
    search_fields = ('utilisateur__last_name', 'utilisateur__first_name', 'domaine_competence')
    
    # Empêche l'ajout/modification manuelle (doit venir du profil utilisateur)
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False

    # Affiche un lien cliquable pour que l'admin consulte le CV
    def get_cv_link(self, obj):
        if obj.cv_fichier:
            return format_html('<a href="{}" target="_blank">📄 Voir le CV</a>', obj.cv_fichier.url)
        return "Aucun CV"
    get_cv_link.short_description = "Curriculum Vitae"

    def get_nom_complet(self, obj):
        return f"{obj.utilisateur.last_name} {obj.utilisateur.first_name}"
    get_nom_complet.short_description = "Nom de l'Expert"