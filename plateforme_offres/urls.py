# plateforme_offres/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# 🔐 Imports JWT (SimpleJWT)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# 🔹 Imports des vues personnalisées
from offres.views import (
    # Auth
    RegisterView, CustomTokenObtainPairView, CustomTokenRefreshView,
    LogoutView, UserProfileView, ChangePasswordView,
    # Offres
    AppelOffreViewSet,
    # Profils
    ProfilExpertViewSet, BureauEtudeViewSet, CritereRechercheViewSet,
    # Dashboard
    ExpertDashboardView, BureauDashboardView,  # ← AJOUTER BureauDashboardView
    # Newsletter
    NewsletterSubscriptionView,
)
from rest_framework.routers import DefaultRouter

# =============================================================================
# CONFIGURATION DU ROUTER DRF
# =============================================================================
router = DefaultRouter()

# Offres : accès public en lecture
router.register(r'offres', AppelOffreViewSet, basename='offres')

# Profils : accès restreint par rôle
router.register(r'expert/profil', ProfilExpertViewSet, basename='expert-profil')
router.register(r'bureau/profil', BureauEtudeViewSet, basename='bureau-profil')
router.register(r'expert/criteres', CritereRechercheViewSet, basename='criteres')

# =============================================================================
# URL PATTERNS PRINCIPAUX
# =============================================================================
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 🔐 Endpoints JWT (SimpleJWT)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # === AUTHENTIFICATION PERSONNALISÉE ===
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/profile/', UserProfileView.as_view(), name='profile'),
    path('api/auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # === DASHBOARDS PAR RÔLE ===
    path('api/expert/dashboard/', ExpertDashboardView.as_view(), name='expert_dashboard'),
    
    # ✅ ROUTE MANQUANTE AJOUTÉE ICI :
    path('api/bureau/dashboard/', BureauDashboardView.as_view(), name='bureau_dashboard'),
    
    # === NEWSLETTER (ACCÈS PUBLIC) ===
    path('api/newsletter/subscribe/', NewsletterSubscriptionView.as_view(), name='newsletter_subscribe'),
    
    # === API ROUTER (offres, profils, criteres) ===
    path('api/', include(router.urls)),
]

# Servir les fichiers médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)