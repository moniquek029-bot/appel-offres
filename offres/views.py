"""
offres/views.py
Vues avec contrôle d'accès par rôle et gestion des profils obligatoires.
"""

from django.shortcuts import render
from django.conf import settings
from django.db.models import Q
from rest_framework import viewsets, generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth import get_user_model

from .permissions import IsAuthenticatedOrReadOnlyPublic, IsExpert, IsBureau, IsAdmin, IsVisitorOrAuthenticated
from .models import (
    AppelOffre, Utilisateur, ProfilExpert, BureauEtude, 
    CritereRecherche, InscriptionNewsletter, Notification
)
from .serializers import (
    RegisterSerializer, CustomTokenObtainPairSerializer, UserSerializer,
    AppelOffreSerializer, ProfilExpertSerializer, BureauEtudeSerializer,
    CritereRechercheSerializer, NewsletterSubscriptionSerializer, 
    ChangePasswordSerializer, NotificationSerializer
)

User = get_user_model()


# =============================================================================
# AUTHENTIFICATION
# =============================================================================

class RegisterView(generics.CreateAPIView):
    """Inscription avec choix du rôle → création automatique du profil"""
    queryset = Utilisateur.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Création automatique du profil lié
        if user.role == 'EXPERT':
            ProfilExpert.objects.create(utilisateur=user)
        elif user.role in ['BUREAU', 'BUREAU_ETUDE']:
            BureauEtude.objects.create(gestionnaire=user)
        
        redirect_to = '/dashboard'
        if user.role == 'EXPERT':
            redirect_to = '/expert/dashboard'
        elif user.role in ['BUREAU', 'BUREAU_ETUDE']:
            redirect_to = '/bureau/dashboard'
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': f'Compte {user.role} créé avec succès.',
            'user': UserSerializer(user).data,
            'tokens': {'refresh': str(refresh), 'access': str(refresh.access_token)},
            'redirect_to': redirect_to,
            'next_step': self._get_next_step_message(user)
        }, status=status.HTTP_201_CREATED)

    @staticmethod
    def _get_next_step_message(user):
        if user.role == 'EXPERT':
            return "Prochaine étape : Complétez votre profil expert."
        elif user.role in ['BUREAU', 'BUREAU_ETUDE']:
            return "Prochaine étape : Complétez les informations de votre structure."
        return "Vous pouvez dès maintenant consulter les appels d'offres."


class CustomTokenObtainPairView(TokenObtainPairView):
    """Connexion avec réponse personnalisée"""
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
        except Exception as e:
            return Response({'error': f'Token invalide: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Consultation/modification de son propre profil utilisateur"""
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
        user = serializer.save()
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Mot de passe changé avec succès.'}, status=status.HTTP_200_OK)


# =============================================================================
# APPELS D'OFFRES - ACCÈS DIFFÉRENCIÉ
# =============================================================================

class AppelOffreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Consultation des offres :
    - Visiteurs : liste + recherche + filtres (métadonnées uniquement)
    - Connectés : détails complets + URL TDR officielle
    """
    permission_classes = [IsAuthenticatedOrReadOnlyPublic]
    serializer_class = AppelOffreSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    filterset_fields = ['pays', 'organisme', 'statut']
    search_fields = ['titre', 'organisme', 'description']
    ordering_fields = ['date_publication', 'date_cloture', 'titre']
    ordering = ['-date_publication']

    def get_queryset(self):
        # ✅ VERSION DÉVELOPPEMENT : Afficher TOUTES les offres scrapées
        return AppelOffre.objects.all()

    def retrieve(self, request, *args, **kwargs):
        """Détail d'une offre : passe le contexte request pour gérer url_tdr"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)


# =============================================================================
# ESPACE EXPERT - DASHBOARD
# =============================================================================

class ExpertDashboardView(APIView):
    """Tableau de bord Expert avec toutes les informations"""
    permission_classes = [IsExpert]
    
    def get(self, request):
        user = request.user
        
        if not user.is_authenticated:
            return Response({'error': 'Authentification requise'}, status=401)
        
        user_role = getattr(user, 'role', None)
        if not user_role or str(user_role).upper() != 'EXPERT':
            return Response({'error': 'Accès réservé aux experts'}, status=403)
        
        try:
            profile = getattr(user, 'profil_expert', None)
            criteres_count = CritereRecherche.objects.filter(utilisateur=user).count()
            
            # Offres correspondantes aux critères
            matching_offres = []
            criteres = CritereRecherche.objects.filter(utilisateur=user)
            
            if criteres.exists():
                query = Q()
                for critere in criteres:
                    if critere.mots_cles:
                        query |= Q(titre__icontains=critere.mots_cles) | \
                                 Q(description__icontains=critere.mots_cles)
                if query:
                    matching_offres = AppelOffre.objects.filter(query).order_by('-date_publication')[:10]
            
            profile_data = None
            if profile:
                try:
                    profile_data = ProfilExpertSerializer(profile).data
                except Exception as e:
                    if settings.DEBUG:
                        print(f"⚠️ Erreur sérialisation profil: {e}")
            
            return Response({
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'nom': f"{user.first_name} {user.last_name}".strip(),
                    'role': user.role,
                },
                'profile': profile_data,
                'stats': {
                    'criteres_count': criteres_count,
                    'matching_offres_count': len(matching_offres),
                    'profile_complete': bool(profile and getattr(profile, 'cv_fichier', None)),
                },
                'recent_matching_offres': self._serialize_offres(matching_offres),
                'next_steps': self._get_next_steps(user, profile)
            })
            
        except Exception as e:
            if settings.DEBUG:
                import traceback
                print(f"❌ ERREUR DASHBOARD EXPERT: {str(e)}")
                print(traceback.format_exc())
            return Response({'error': 'Erreur serveur interne'}, status=500)

    def _serialize_offres(self, offres):
        try:
            return AppelOffreSerializer(offres, many=True).data
        except Exception:
            return []

    def _get_next_steps(self, user, profile):
        steps = []
        if not profile or not getattr(profile, 'cv_fichier', None):
            steps.append({
                'priority': 'high',
                'action': 'upload_cv',
                'message': 'Téléchargez votre CV pour compléter votre profil',
                'url': '/expert/profile'
            })
        if not steps:
            steps.append({
                'priority': 'low',
                'action': 'browse_offres',
                'message': 'Consultez les dernières offres disponibles',
                'url': '/offres'
            })
        return steps


# =============================================================================
# ESPACE BUREAU D'ÉTUDE - DASHBOARD
# =============================================================================

class BureauDashboardView(APIView):
    """Tableau de bord Bureau d'Études"""
    permission_classes = [IsBureau]
    
    def get(self, request):
        user = request.user
        
        if not user.is_authenticated:
            return Response({'error': 'Authentification requise'}, status=401)
        
        user_role = getattr(user, 'role', None)
        if not user_role or str(user_role).upper() not in ['BUREAU', 'BUREAU_ETUDE']:
            return Response({'error': 'Accès réservé aux bureaux d\'études'}, status=403)
        
        try:
            bureau = getattr(user, 'bureauetude', None)
            
            bureau_data = None
            if bureau:
                try:
                    bureau_data = BureauEtudeSerializer(bureau).data
                except Exception as e:
                    if settings.DEBUG:
                        print(f"⚠️ Erreur sérialisation bureau: {e}")
            
            return Response({
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'nom': f"{user.first_name} {user.last_name}".strip(),
                    'role': user.role,
                },
                'bureau': bureau_data,
                'stats': {
                    'profile_complete': bool(bureau and getattr(bureau, 'cv_fichier', None)),
                },
                'next_steps': self._get_next_steps(user, bureau)
            })
            
        except Exception as e:
            if settings.DEBUG:
                import traceback
                print(f"❌ ERREUR DASHBOARD BUREAU: {str(e)}")
                print(traceback.format_exc())
            return Response({'error': 'Erreur serveur interne'}, status=500)

    def _get_next_steps(self, user, bureau):
        steps = []
        if not bureau or not getattr(bureau, 'cv_fichier', None):
            steps.append({
                'priority': 'high',
                'action': 'upload_cv',
                'message': 'Téléchargez les documents de votre structure',
                'url': '/bureau/profile'
            })
        if not steps:
            steps.append({
                'priority': 'low',
                'action': 'browse_offres',
                'message': 'Consultez les dernières offres disponibles',
                'url': '/offres'
            })
        return steps


# =============================================================================
# GESTION DES PROFILS - EXPERT
# =============================================================================

class ProfilExpertViewSet(viewsets.ModelViewSet):
    """Gestion du profil Expert - Accès Expert uniquement"""
    serializer_class = ProfilExpertSerializer
    permission_classes = [IsExpert]

    def get_queryset(self):
        return ProfilExpert.objects.filter(utilisateur=self.request.user)

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)
    
    def perform_update(self, serializer):
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
            
            return Response({
                'message': 'CV téléchargé avec succès.',
                'cv_url': profile.cv_fichier.url if profile.cv_fichier else None,
                'is_profile_complete': True
            })
        except ProfilExpert.DoesNotExist:
            return Response({'error': 'Profil expert non trouvé'}, status=status.HTTP_404_NOT_FOUND)


# =============================================================================
# GESTION DES PROFILS - BUREAU
# =============================================================================

class BureauEtudeViewSet(viewsets.ModelViewSet):
    """Gestion du profil Bureau - Accès Bureau uniquement"""
    serializer_class = BureauEtudeSerializer
    permission_classes = [IsBureau]

    def get_queryset(self):
        return BureauEtude.objects.filter(gestionnaire=self.request.user)

    def perform_create(self, serializer):
        serializer.save(gestionnaire=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(gestionnaire=self.request.user)

    @action(detail=False, methods=['post'], url_path='upload-cv')
    def upload_cv(self, request):
        """Endpoint dédié pour l'upload des documents du bureau"""
        try:
            bureau = request.user.bureauetude
            if 'cv_fichier' not in request.FILES:
                return Response({'error': 'Fichier requis'}, status=status.HTTP_400_BAD_REQUEST)
            
            bureau.cv_fichier = request.FILES['cv_fichier']
            bureau.save()
            
            return Response({
                'message': 'Document téléchargé avec succès.',
                'cv_url': bureau.cv_fichier.url if bureau.cv_fichier else None,
                'is_profile_complete': True
            })
        except BureauEtude.DoesNotExist:
            return Response({'error': 'Profil bureau non trouvé'}, status=status.HTTP_404_NOT_FOUND)


# =============================================================================
# CRITÈRES DE RECHERCHE (Experts uniquement)
# =============================================================================

class CritereRechercheViewSet(viewsets.ModelViewSet):
    """Gestion des critères de recherche pour les alertes email"""
    serializer_class = CritereRechercheSerializer
    permission_classes = [IsExpert]

    def get_queryset(self):
        return CritereRecherche.objects.filter(utilisateur=self.request.user)

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)


# =============================================================================
# NEWSLETTER - ACCÈS PUBLIC
# =============================================================================

class NewsletterSubscriptionView(generics.CreateAPIView):
    """Inscription à la newsletter sans compte."""
    queryset = InscriptionNewsletter.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = NewsletterSubscriptionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save()
        
        return Response({
            'message': 'Inscription réussie ! Vous recevrez les nouvelles offres par email.'
        }, status=status.HTTP_201_CREATED)