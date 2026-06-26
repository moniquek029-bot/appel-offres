# plateforme_offres/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from offres.views import (
    # Auth
    RegisterView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    
    # User
    UserProfileView,
    ChangePasswordView,
    
    # Offres
    AppelOffreViewSet,
    OffresPubliquesView,
    TelechargerPDFView,
    
    # Expert
    ExpertDashboardView,
    ProfilExpertViewSet,
    CritereRechercheViewSet,
    SuggestionExpertViewSet,
    
    # Bureau
    BureauDashboardView,
    BureauEtudeViewSet,
    
    # Messages & Notifications
    MessageViewSet,
    NotificationUserViewSet,
    
    # Admin
    AdminDashboardView,
    AdminSourceViewSet,
    AdminSourcesRunView,
    AdminUtilisateurViewSet,
    AdminConnexionHistoriqueView,
    AdminSuggestionOffreViewSet,
    AdminHistoryView,
    
    # Newsletter
    NewsletterSubscriptionView,
    
    # Password reset
    password_reset_request,
    password_reset_confirm,
    password_reset_validate_token,
    admin_user_details,
    admin_list_experts_with_profiles,
    
    # ❌ AdminReponseMessageView SUPPRIMÉ (maintenant dans MessageViewSet)
)
urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # =========================================================================
    # AUTHENTIFICATION (avec alias pour compatibilité frontend)
    # =========================================================================
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/auth/register/', RegisterView.as_view(), name='auth-register'),  # ✅ ALIAS
    
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='auth-login'),  # ✅ ALIAS
    
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/refresh/', CustomTokenRefreshView.as_view(), name='auth-refresh'),  # ✅ ALIAS
    
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/logout/', LogoutView.as_view(), name='auth-logout'),  # ✅ ALIAS
    
    # =========================================================================
    # PROFIL UTILISATEUR
    # =========================================================================
    path('api/profile/', UserProfileView.as_view(), name='user-profile'),
    path('api/change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # ... reste du fichier inchangé ...urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # =========================================================================
    # AUTHENTIFICATION (avec alias pour compatibilité frontend)
    # =========================================================================
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/auth/register/', RegisterView.as_view(), name='auth-register'),  # ✅ ALIAS
    
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='auth-login'),  # ✅ ALIAS
    
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/refresh/', CustomTokenRefreshView.as_view(), name='auth-refresh'),  # ✅ ALIAS
    
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/logout/', LogoutView.as_view(), name='auth-logout'),  # ✅ ALIAS
    
    # =========================================================================
    # PROFIL UTILISATEUR
    # =========================================================================
    path('api/profile/', UserProfileView.as_view(), name='user-profile'),
    path('api/change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # ... reste du fichier inchangé ...urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # =========================================================================
    # AUTHENTIFICATION (avec alias pour compatibilité frontend)
    # =========================================================================
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/auth/register/', RegisterView.as_view(), name='auth-register'),  # ✅ ALIAS
    
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='auth-login'),  # ✅ ALIAS
    
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/refresh/', CustomTokenRefreshView.as_view(), name='auth-refresh'),  # ✅ ALIAS
    
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/logout/', LogoutView.as_view(), name='auth-logout'),  # ✅ ALIAS
    
    # =========================================================================
    # PROFIL UTILISATEUR
    # =========================================================================
    path('api/profile/', UserProfileView.as_view(), name='user-profile'),
    path('api/change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # ... reste du fichier inchangé ...urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # =========================================================================
    # AUTHENTIFICATION (avec alias pour compatibilité frontend)
    # =========================================================================
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/auth/register/', RegisterView.as_view(), name='auth-register'),  # ✅ ALIAS
    
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='auth-login'),  # ✅ ALIAS
    
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/refresh/', CustomTokenRefreshView.as_view(), name='auth-refresh'),  # ✅ ALIAS
    
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/logout/', LogoutView.as_view(), name='auth-logout'),  # ✅ ALIAS
    
    # =========================================================================
    # PROFIL UTILISATEUR
    # =========================================================================
    path('api/profile/', UserProfileView.as_view(), name='user-profile'),
    path('api/change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # ... reste du fichier inchangé ...urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # =========================================================================
    # AUTHENTIFICATION (avec alias pour compatibilité frontend)
    # =========================================================================
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/auth/register/', RegisterView.as_view(), name='auth-register'),  # ✅ ALIAS
    
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='auth-login'),  # ✅ ALIAS
    
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/refresh/', CustomTokenRefreshView.as_view(), name='auth-refresh'),  # ✅ ALIAS
    
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/logout/', LogoutView.as_view(), name='auth-logout'),  # ✅ ALIAS
    
    # =========================================================================
    # PROFIL UTILISATEUR
    # =========================================================================
    path('api/profile/', UserProfileView.as_view(), name='user-profile'),
    path('api/change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # ... reste du fichier inchangé ...urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # =========================================================================
    # AUTHENTIFICATION (avec alias pour compatibilité frontend)
    # =========================================================================
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/auth/register/', RegisterView.as_view(), name='auth-register'),  # ✅ ALIAS
    
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='auth-login'),  # ✅ ALIAS
    
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/refresh/', CustomTokenRefreshView.as_view(), name='auth-refresh'),  # ✅ ALIAS
    
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/logout/', LogoutView.as_view(), name='auth-logout'),  # ✅ ALIAS
    
    # =========================================================================
    # PROFIL UTILISATEUR
    # =========================================================================
    path('api/profile/', UserProfileView.as_view(), name='user-profile'),
    path('api/change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # ... reste du fichier inchangé ...urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # =========================================================================
    # AUTHENTIFICATION (avec alias pour compatibilité frontend)
    # =========================================================================
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/auth/register/', RegisterView.as_view(), name='auth-register'),  # ✅ ALIAS
    
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='auth-login'),  # ✅ ALIAS
    
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/refresh/', CustomTokenRefreshView.as_view(), name='auth-refresh'),  # ✅ ALIAS
    
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/logout/', LogoutView.as_view(), name='auth-logout'),  # ✅ ALIAS
    
    # =========================================================================
    # PROFIL UTILISATEUR
    # =========================================================================
    path('api/profile/', UserProfileView.as_view(), name='user-profile'),
    path('api/change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # ... reste du fichier inchangé ...urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # =========================================================================
    # AUTHENTIFICATION (avec alias pour compatibilité frontend)
    # =========================================================================
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/auth/register/', RegisterView.as_view(), name='auth-register'),  # ✅ ALIAS
    
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='auth-login'),  # ✅ ALIAS
    
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/refresh/', CustomTokenRefreshView.as_view(), name='auth-refresh'),  # ✅ ALIAS
    
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/logout/', LogoutView.as_view(), name='auth-logout'),  # ✅ ALIAS
    
    # =========================================================================
    # PROFIL UTILISATEUR
    # =========================================================================
    path('api/profile/', UserProfileView.as_view(), name='user-profile'),
    path('api/change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # ... reste du fichier inchangé ...urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # =========================================================================
    # AUTHENTIFICATION (avec alias pour compatibilité frontend)
    # =========================================================================
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/auth/register/', RegisterView.as_view(), name='auth-register'),  # ✅ ALIAS
    
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='auth-login'),  # ✅ ALIAS
    
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/refresh/', CustomTokenRefreshView.as_view(), name='auth-refresh'),  # ✅ ALIAS
    
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/logout/', LogoutView.as_view(), name='auth-logout'),  # ✅ ALIAS
    
    # =========================================================================
    # PROFIL UTILISATEUR
    # =========================================================================
    path('api/profile/', UserProfileView.as_view(), name='user-profile'),
    path('api/change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # ... reste du fichier inchangé ...
    # =========================================================================
    # PROFIL UTILISATEUR
    # =========================================================================
    path('api/profile/', UserProfileView.as_view(), name='user-profile'),
    path('api/change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # =========================================================================
    # APPELS D'OFFRES
    # =========================================================================
    path('api/offres/', AppelOffreViewSet.as_view({'get': 'list'}), name='offre-list'),
    path('api/offres/<int:pk>/', AppelOffreViewSet.as_view({'get': 'retrieve'}), name='offre-detail'),
    path('api/offres/recent/', AppelOffreViewSet.as_view({'get': 'recent_offres'}), name='offre-recent'),
    path('api/offres/create-manuel/', AppelOffreViewSet.as_view({'post': 'create_manuel'}), name='offre-create-manuel'),
    path('api/offres/<int:pk>/download-pdf/', AppelOffreViewSet.as_view({'get': 'download_pdf'}), name='offre-download-pdf'),
    path('api/offres-publiques/', OffresPubliquesView.as_view(), name='offres-publiques'),
    path('api/offres/<int:offre_id>/download/', TelechargerPDFView.as_view(), name='telecharger-pdf'),
    
    # =========================================================================
    # ESPACE EXPERT
    # =========================================================================
    path('api/expert/dashboard/', ExpertDashboardView.as_view(), name='expert-dashboard'),
    path('api/expert/profil/', ProfilExpertViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='expert-profil'),
    path('api/expert/profil/update/', ProfilExpertViewSet.as_view({
        'put': 'update_profile',
        'patch': 'update_profile'
    }), name='expert-profil-update'),
    path('api/expert/profil/upload-cv/', ProfilExpertViewSet.as_view({
        'post': 'upload_cv'
    }), name='expert-upload-cv'),
    path('api/expert/criteres/', CritereRechercheViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='expert-criteres'),
    path('api/expert/criteres/<int:pk>/', CritereRechercheViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='expert-critere-detail'),
    path('api/expert/suggestions/', SuggestionExpertViewSet.as_view({
        'get': 'list'
    }), name='expert-suggestions-list'),
    path('api/expert/suggestions/<int:pk>/', SuggestionExpertViewSet.as_view({
        'get': 'retrieve'
    }), name='expert-suggestion-detail'),
    path('api/expert/suggestions/<int:pk>/repondre/', SuggestionExpertViewSet.as_view({
        'post': 'repondre'
    }), name='expert-suggestion-repondre'),
    path('api/expert/suggestions/<int:pk>/marquer-consultee/', SuggestionExpertViewSet.as_view({
        'post': 'marquer_consultee'
    }), name='expert-suggestion-marquer-consultee'),
    
    # =========================================================================
    # ESPACE BUREAU
    # =========================================================================
    path('api/bureau/dashboard/', BureauDashboardView.as_view(), name='bureau-dashboard'),
    path('api/bureau/profil/', BureauEtudeViewSet.as_view({
        'get': 'my_profile'
    }), name='bureau-profil'),
    path('api/bureau/profil/update/', BureauEtudeViewSet.as_view({
        'put': 'update_profile'
    }), name='bureau-profil-update'),
    
    # =========================================================================
    # MESSAGES & NOTIFICATIONS
    # =========================================================================
    path('api/messages/', MessageViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='message-list'),
    path('api/messages/<int:pk>/', MessageViewSet.as_view({
        'get': 'retrieve',
        'delete': 'destroy'
    }), name='message-detail'),
    path('api/messages/<int:pk>/marquer-lu/', MessageViewSet.as_view({
        'post': 'marquer_lu'
    }), name='message-marquer-lu'),
    path('api/messages/<int:pk>/repondre/', MessageViewSet.as_view({
        'post': 'repondre'
    }), name='message-repondre'),  # ✅ NOUVELLE ROUTE
    path('api/messages/envoyer-admin/', MessageViewSet.as_view({
        'post': 'envoyer_a_admin'
    }), name='message-envoyer-admin'),
    path('api/messages/non-lus/', MessageViewSet.as_view({
        'get': 'messages_non_lus'
    }), name='messages-non-lus'),
    path('api/messages/conversation-admin/', MessageViewSet.as_view({
        'get': 'conversation_avec_admin'
    }), name='conversation-admin'),
    
    path('api/notifications/', NotificationUserViewSet.as_view({
        'get': 'list'
    }), name='notification-list'),
    path('api/notifications/<int:pk>/marquer-lue/', NotificationUserViewSet.as_view({
        'post': 'marquer_lue'
    }), name='notification-marquer-lue'),
    
    # =========================================================================
    # ADMIN DASHBOARD
    # =========================================================================
    path('api/admin/dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    
    # Sources de scraping
    path('api/admin/sources/', AdminSourceViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='admin-source-list'),
    path('api/admin/sources/<int:pk>/', AdminSourceViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='admin-source-detail'),
    path('api/admin/sources/run/', AdminSourceViewSet.as_view({
        'post': 'run_scraping'
    }), name='admin-source-run'),
    path('api/admin/sources/run-alt/', AdminSourcesRunView.as_view(), name='admin-source-run-alt'),
    
    # Utilisateurs
    path('api/admin/utilisateurs/', AdminUtilisateurViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='admin-utilisateur-list'),
    path('api/admin/utilisateurs/<int:pk>/', AdminUtilisateurViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='admin-utilisateur-detail'),
    path('api/admin/utilisateurs/<int:pk>/toggle-active/', AdminUtilisateurViewSet.as_view({
        'patch': 'toggle_active'
    }), name='admin-utilisateur-toggle-active'),
    path('api/admin/utilisateurs/<int:pk>/force-delete/', AdminUtilisateurViewSet.as_view({
        'delete': 'force_delete'
    }), name='admin-utilisateur-force-delete'),
    path('api/admin/utilisateurs/<int:user_id>/details/', admin_user_details, name='admin-user-details'),
    path('api/admin/experts/', admin_list_experts_with_profiles, name='admin-list-experts'),
    
    # Suggestions
    path('api/admin/suggestions/', AdminSuggestionOffreViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='admin-suggestion-list'),
    path('api/admin/suggestions/<int:pk>/', AdminSuggestionOffreViewSet.as_view({
        'get': 'retrieve',
        'delete': 'destroy'
    }), name='admin-suggestion-detail'),
    path('api/admin/suggestions/<int:pk>/envoyer/', AdminSuggestionOffreViewSet.as_view({
        'post': 'envoyer_suggestion'
    }), name='admin-suggestion-envoyer'),
    path('api/admin/suggestions/<int:pk>/force-delete/', AdminSuggestionOffreViewSet.as_view({
        'delete': 'force_delete'
    }), name='admin-suggestion-force-delete'),
    
    # Historique
    path('api/admin/historique/', AdminHistoryView.as_view(), name='admin-historique'),
    path('api/admin/historique/clear/', AdminHistoryView.as_view(), name='admin-historique-clear'),
    path('api/admin/connexions/', AdminConnexionHistoriqueView.as_view(), name='admin-connexions'),
    
    # ❌ AdminReponseMessageView SUPPRIMÉ - maintenant : POST /api/messages/{id}/repondre/
    
    # =========================================================================
    # NEWSLETTER
    # =========================================================================
    path('api/newsletter/subscribe/', NewsletterSubscriptionView.as_view(), name='newsletter-subscribe'),
    
    # =========================================================================
    # PASSWORD RESET
    # =========================================================================
    path('api/password-reset/', password_reset_request, name='password-reset'),
    path('api/password-reset/confirm/', password_reset_confirm, name='password-reset-confirm'),
    path('api/password-reset/validate/<str:token>/', password_reset_validate_token, name='password-reset-validate'),
]

# Servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)