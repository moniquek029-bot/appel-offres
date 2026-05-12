"""
offres/views.py
Vues avec contrôle d'accès par rôle et gestion des profils obligatoires.
"""

from django.shortcuts import render
from rest_framework import viewsets, generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import AppelOffre, Utilisateur, ProfilExpert, BureauEtude, CritereRecherche, InscriptionNewsletter
from .serializers import (
    RegisterSerializer, CustomTokenObtainPairSerializer, UserSerializer,
    AppelOffreSerializer, ProfilExpertSerializer, BureauEtudeSerializer,
    CritereRechercheSerializer, NewsletterSubscriptionSerializer, ChangePasswordSerializer
)
from .permissions import IsExpert, IsBureau, IsAdmin, IsAuthenticatedOrReadOnlyPublic, IsVisitorOrAuthenticated


# =============================================================================
# AUTHENTIFICATION
# =============================================================================

class RegisterView(generics.CreateAPIView):
    """Inscription avec choix du rôle → redirection vers complétion profil si nécessaire"""
    queryset = Utilisateur.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Génération des tokens JWT
        refresh = RefreshToken.for_user(user)
        
        # Détermination de la redirection selon le rôle et l'état du profil
        redirect_to = '/dashboard'
        if user.role == 'EXPERT' and not user.profil_expert.cv_fichier:
            redirect_to = '/expert/complete-profile'
        elif user.role == 'BUREAU' and not hasattr(user, 'bureauetude'):
            redirect_to = '/bureau/complete-profile'
        elif user.role == 'EXPERT':
            redirect_to = '/expert/dashboard'
        elif user.role == 'BUREAU':
            redirect_to = '/bureau/dashboard'
        
        return Response({
            'message': f'Compte {user.role} créé avec succès.',
            'user': UserSerializer(user).data,
            'tokens': {'refresh': str(refresh), 'access': str(refresh.access_token)},
            'redirect_to': redirect_to,
            'next_step': self._get_next_step_message(user)
        }, status=status.HTTP_201_CREATED)

    @staticmethod
    def _get_next_step_message(user):
        """Message guidant l'utilisateur vers l'étape suivante"""
        if user.role == 'EXPERT':
            return "Prochaine étape : Téléchargez votre CV pour accéder au tableau de bord Expert."
        elif user.role == 'BUREAU':
            return "Prochaine étape : Complétez les informations de votre structure."
        return "Vous pouvez dès maintenant consulter les appels d'offres."


class CustomTokenObtainPairView(TokenObtainPairView):
    """Connexion avec redirection intelligente selon le rôle"""
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    """Rafraîchissement de token"""
    pass


class LogoutView(APIView):
    """Déconnexion avec blacklist du refresh token"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response({'error': 'Refresh token requis'}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Déconnexion réussie.'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'error': 'Token invalide'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Consultation/modification de son propre profil"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    """Changement de mot de passe"""
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Mot de passe changé avec succès.'}, status=status.HTTP_200_OK)


# =============================================================================
# APPELS D'OFFRES - ACCÈS DIFFÉRENCIÉ
# =============================================================================

class AppelOffreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Consultation des offres :
    - Visiteurs non connectés : liste + recherche + filtres (métadonnées uniquement)
    - Utilisateurs connectés : accès aux détails complets + URL source
    """
    permission_classes = [IsAuthenticatedOrReadOnlyPublic]
    serializer_class = AppelOffreSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['pays', 'organisme', 'statut']
    search_fields = ['titre', 'organisme', 'description']
    ordering_fields = ['date_publication', 'date_cloture']
    ordering = ['-date_publication']

    def get_queryset(self):
        # Tous voient les offres "Ouvertes"
        return AppelOffre.objects.filter(statut="Ouvert")

    def retrieve(self, request, *args, **kwargs):
        """Détail d'une offre : masque l'URL pour les visiteurs non connectés"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)


# =============================================================================
# GESTION DES PROFILS (EXPERT / BUREAU)
# =============================================================================

class ProfilExpertViewSet(viewsets.ModelViewSet):
    """Gestion du profil Expert (CV, compétences) - Accès Expert uniquement"""
    serializer_class = ProfilExpertSerializer
    permission_classes = [IsExpert]

    def get_queryset(self):
        # Un expert ne voit que son propre profil
        return ProfilExpert.objects.filter(utilisateur=self.request.user)

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)

    @action(detail=False, methods=['post'], url_path='upload-cv')
    def upload_cv(self, request):
        """Endpoint dédié pour l'upload du CV"""
        try:
            profile = request.user.profil_expert
            if 'cv_fichier' not in request.FILES:
                return Response({'error': 'Fichier CV requis'}, status=status.HTTP_400_BAD_REQUEST)
            profile.cv_fichier = request.FILES['cv_fichier']
            profile.save()
            return Response({'message': 'CV téléchargé avec succès.', 'is_profile_complete': True})
        except ProfilExpert.DoesNotExist:
            return Response({'error': 'Profil expert non trouvé'}, status=status.HTTP_404_NOT_FOUND)


class BureauEtudeViewSet(viewsets.ModelViewSet):
    """Gestion du profil Bureau - Accès Bureau uniquement"""
    serializer_class = BureauEtudeSerializer
    permission_classes = [IsBureau]

    def get_queryset(self):
        return BureauEtude.objects.filter(gestionnaire=self.request.user)

    def perform_create(self, serializer):
        serializer.save(gestionnaire=self.request.user)


# =============================================================================
# ALERTES & CRITÈRES DE RECHERCHE (Experts)
# =============================================================================

class CritereRechercheViewSet(viewsets.ModelViewSet):
    """Gestion des critères de recherche pour les alertes email"""
    serializer_class = CritereRechercheSerializer
    permission_classes = [IsExpert]

    def get_queryset(self):
        return CritereRecherche.objects.filter(utilisateur=self.request.user)

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)



# NEWSLETTER - ACCÈS PUBLIC (VISITEURS NON CONNECTÉS)

class NewsletterSubscriptionView(generics.CreateAPIView):
    """
    Inscription à la newsletter sans compte.
    Les visiteurs reçoivent les nouvelles offres par email.
    """
    queryset = InscriptionNewsletter.objects.all()
    permission_classes = [permissions.AllowAny]  #  Accessible à tous, même non connectés
    serializer_class = NewsletterSubscriptionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save()
        
        # TODO: Intégrer avec Celery pour envoyer un email de confirmation
        # send_newsletter_confirmation.delay(subscription.email)
        
        return Response({
            'message': 'Inscription réussie ! Vous recevrez les nouvelles offres par email.'
        }, status=status.HTTP_201_CREATED)