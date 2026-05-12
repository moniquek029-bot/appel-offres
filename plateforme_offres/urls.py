from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from offres.views import (
    # Auth
    RegisterView, CustomTokenObtainPairView, CustomTokenRefreshView,
    LogoutView, UserProfileView, ChangePasswordView,
    # Offres
    AppelOffreViewSet,
    # Profils
    ProfilExpertViewSet, BureauEtudeViewSet, CritereRechercheViewSet,
    # Newsletter
    NewsletterSubscriptionView,
)

router = DefaultRouter()
# Offres : accès public en lecture
router.register(r'offres', AppelOffreViewSet, basename='offres')
# Profils : accès restreint par rôle
router.register(r'expert/profil', ProfilExpertViewSet, basename='expert-profil')
router.register(r'bureau/profil', BureauEtudeViewSet, basename='bureau-profil')
router.register(r'expert/criteres', CritereRechercheViewSet, basename='criteres')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # === AUTHENTIFICATION ===
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('api/auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/profile/', UserProfileView.as_view(), name='profile'),
    path('api/auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # === NEWSLETTER (ACCÈS PUBLIC) ===
    path('api/newsletter/subscribe/', NewsletterSubscriptionView.as_view(), name='newsletter_subscribe'),
    
    # === API ROUTER ===
    path('api/', include(router.urls)),
]

# Servir les fichiers médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)