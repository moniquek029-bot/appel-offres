# plateforme_offres/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from offres.views import TelechargerPDFView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from rest_framework.routers import DefaultRouter

# ✅ Imports des vues
from offres.views import (
    RegisterView, CustomTokenObtainPairView, CustomTokenRefreshView,
    LogoutView, UserProfileView, ChangePasswordView,
    AppelOffreViewSet,
    ProfilExpertViewSet, BureauEtudeViewSet, CritereRechercheViewSet,
    ExpertDashboardView, BureauDashboardView,
    NewsletterSubscriptionView,
    MessageViewSet,
    NotificationUserViewSet,
    AdminDashboardView,
    AdminUtilisateurViewSet,
    AdminConnexionHistoriqueView,
    AdminSuggestionOffreViewSet,
    AdminReponseMessageView,
    OffresPubliquesView,
    AdminSourceViewSet,
    AdminHistoryView,
    AdminSourcesRunView,
    SuggestionExpertViewSet,
    # ✅ Fonctions de réinitialisation de mot de passe
    password_reset_request,
    password_reset_confirm,
    password_reset_validate_token,
    admin_user_details,
)

# =============================================================================
# ROUTER DRF
# =============================================================================
router = DefaultRouter()

# Routes existantes
router.register(r'offres', AppelOffreViewSet, basename='offres')
router.register(r'expert/profil', ProfilExpertViewSet, basename='expert-profil')
router.register(r'bureau/profil', BureauEtudeViewSet, basename='bureau-profil')
router.register(r'expert/criteres', CritereRechercheViewSet, basename='criteres')
router.register(r'messages', MessageViewSet, basename='messages')
router.register(r'admin/utilisateurs', AdminUtilisateurViewSet, basename='admin-utilisateurs')
router.register(r'admin/suggestions', AdminSuggestionOffreViewSet, basename='admin-suggestions')
router.register(r'admin/sources', AdminSourceViewSet, basename='admin-sources')
router.register(r'notifications', NotificationUserViewSet, basename='notification')
# =============================================================================
# URL PATTERNS
# =============================================================================
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 🔐 JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # === AUTH ===
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/profile/', UserProfileView.as_view(), name='profile'),
    path('api/auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # ✅ RÉCUPÉRATION DE MOT DE PASSE
    path('api/auth/password-reset/', password_reset_request, name='password-reset-request'),
    path('api/auth/password-reset/confirm/', password_reset_confirm, name='password-reset-confirm'),
    path('api/auth/password-reset/validate/<str:token>/', password_reset_validate_token, name='password-reset-validate'),
    
    # === DASHBOARDS ===
    path('api/expert/dashboard/', ExpertDashboardView.as_view(), name='expert_dashboard'),
    path('api/bureau/dashboard/', BureauDashboardView.as_view(), name='bureau_dashboard'),

    # === EXPERT - SUGGESTIONS ===
    path('api/expert/suggestions/', SuggestionExpertViewSet.as_view({'get': 'list'}), name='expert-suggestions'),
    path('api/expert/suggestions/<int:pk>/', SuggestionExpertViewSet.as_view({'get': 'retrieve'}), name='expert-suggestion-detail'),
    path('api/expert/suggestions/<int:pk>/repondre/', SuggestionExpertViewSet.as_view({'post': 'repondre'}), name='expert-suggestion-repondre'),
    path('api/expert/suggestions/<int:pk>/marquer-consultee/', SuggestionExpertViewSet.as_view({'post': 'marquer_consultee'}), name='expert-suggestion-marquer-consultee'),
    
    # === ADMIN DASHBOARD ===
    path('api/admin/dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('api/admin/dashboard/stats/', AdminDashboardView.as_view(), name='admin-dashboard-stats'),
    
    # === ADMIN - UTILISATEURS ===
    # ✅ URLS STATIQUES EN PREMIER
    path('api/admin/utilisateurs/', AdminUtilisateurViewSet.as_view({'get': 'list', 'post': 'create'}), name='admin-utilisateurs-list'),
    path('api/admin/experts/', AdminUtilisateurViewSet.as_view({'get': 'list'}), name='admin-experts'),
    
    # ✅ URLS DYNAMIQUES APRÈS
    path('api/admin/utilisateurs/<int:user_id>/details/', admin_user_details, name='admin-user-details'),
    path('api/admin/utilisateurs/<int:pk>/toggle-active/', AdminUtilisateurViewSet.as_view({'patch': 'toggle_active'}), name='admin-user-toggle'),
    path('api/admin/utilisateurs/<int:pk>/force-delete/', AdminUtilisateurViewSet.as_view({'delete': 'force_delete'}), name='admin-user-delete'),
    
    # === ADMIN - SOURCES ===
    # ✅ URLS STATIQUES EN PREMIER
    path('api/admin/sources/', AdminSourceViewSet.as_view({'get': 'list', 'post': 'create'}), name='admin-sources-list'),
    path('api/admin/sources/run/', AdminSourceViewSet.as_view({'post': 'run_scraping'}), name='admin-sources-run'),
    
    # ✅ URLS DYNAMIQUES APRÈS
    path('api/admin/sources/<int:pk>/', AdminSourceViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='admin-sources-detail'),
    
    # === ADMIN - HISTORIQUE ===
    path('api/admin/historique/', AdminHistoryView.as_view(), name='admin-history'),
    path('api/admin/historique/clear/', AdminHistoryView.as_view(), name='admin-history-clear'),
    
    # === ADMIN - SUGGESTIONS ===
    # ✅ URLS STATIQUES EN PREMIER
    path('api/admin/suggestions/', AdminSuggestionOffreViewSet.as_view({'get': 'list', 'post': 'create'}), name='admin-suggestions-list'),
    
    # ✅ URLS DYNAMIQUES APRÈS
    path('api/admin/suggestions/<int:pk>/force-delete/', AdminSuggestionOffreViewSet.as_view({'delete': 'force_delete'}), name='admin-suggestion-delete'),
    
    # === ADMIN - CONNEXIONS & MESSAGES ===
    path('api/admin/connexions/', AdminConnexionHistoriqueView.as_view(), name='admin-connexions'),
    path('api/admin/messages/<int:message_id>/reply/', AdminReponseMessageView.as_view(), name='admin-reply-message'),
    
    # === PUBLIC ===
    path('api/newsletter/subscribe/', NewsletterSubscriptionView.as_view(), name='newsletter_subscribe'),
    path('api/offres/publiques/', OffresPubliquesView.as_view(), name='offres-publiques'),

    # PDF
    path('api/offres/<int:offre_id>/download-pdf/', TelechargerPDFView.as_view(), name='download-pdf'),
    
    # === ROUTER (DOIT ÊTRE EN DERNIER) ===
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)