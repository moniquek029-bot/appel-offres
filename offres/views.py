"""
offres/views.py
Vues avec contrôle d'accès par rôle et gestion des profils obligatoires.
✅ VERSION CORRIGÉE : Plus de doublons, scraping synchrone, imports organisés
"""
from offres.utils.search_keywords import get_domain_keywords, get_country_codes

from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from datetime import timedelta
from datetime import datetime



from offres.services.smart_matching import (
    trouver_offres_pour_expert,
    notifier_expert_nouvelles_offres,
    notifier_tous_les_experts,
    detecter_domaines_from_texte,
    DOMAINES_KEYWORDS
)
   
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .serializers import SuggestionOffreExpertSerializer, ReponseSuggestionSerializer

from offres.services.email_service import EmailService

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import PasswordResetToken
from .serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from .tasks import send_password_reset_email
import logging
from django.utils import timezone
import traceback
import os

from rest_framework.pagination import PageNumberPagination

from offres.scraping.tasks import run_scheduled_scraping_task

from rest_framework import viewsets, generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.http import FileResponse, Http404

# =============================================================================
# IMPORTS DES MODELS
# =============================================================================
from .models import (
    AppelOffre, Utilisateur, ProfilExpert, BureauEtude, 
    CritereRecherche, InscriptionNewsletter, Message,
    HistoriqueConnexion, SuggestionOffre, SourceScraping, Notification
)

# =============================================================================
# IMPORTS DES SERIALIZERS
# =============================================================================
from .serializers import (
    RegisterSerializer, CustomTokenObtainPairSerializer, UserSerializer,
    AppelOffreSerializer, ProfilExpertSerializer, BureauEtudeSerializer,
    CritereRechercheSerializer, NewsletterSubscriptionSerializer, 
    ChangePasswordSerializer, NotificationSerializer, MessageSerializer,
    HistoriqueConnexionSerializer, SuggestionOffreSerializer, SourceScrapingSerializer
)

# =============================================================================
# IMPORTS DES PERMISSIONS
# =============================================================================
from .permissions import IsAuthenticatedOrReadOnlyPublic, IsExpert, IsBureau, IsAdmin

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
        
        if user.role == 'EXPERT':
            ProfilExpert.objects.get_or_create(utilisateur=user)
        elif user.role in ['BUREAU', 'BUREAU_ETUDE']:
            BureauEtude.objects.get_or_create(gestionnaire=user)
        
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

# Classe de pagination personnalisée
class CustomPagination(PageNumberPagination):
    page_size = 4  #  4 offres par page
    page_size_query_param = 'page_size'
    max_page_size = 100


class AppelOffreViewSet(viewsets.ModelViewSet):
    """
    Consultation et gestion des offres avec recherche avancée et filtres
    """
    queryset = AppelOffre.objects.all()
    serializer_class = AppelOffreSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # ✅ AJOUTER CETTE LIGNE
    pagination_class = CustomPagination
    
    filterset_fields = {
        'pays': ['exact'],
        'domaine': ['exact'],
        'statut': ['exact'],
        'mode_acquisition': ['exact'],
        'date_publication': ['gte', 'lte'],
        'date_cloture': ['gte', 'lte'],
    }
    
    search_fields = ['titre', 'organisme', 'description']
    ordering_fields = ['date_publication', 'date_cloture', 'titre', 'date_scraping']
    ordering = ['-date_publication', '-date_scraping']
    
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'recent_offres', 'download_pdf']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        
        return [permission() for permission in permission_classes]
    
    # Dans offres/views.py - AppelOffreViewSet.get_queryset()

    # offres/views.py - Modifier AppelOffreViewSet.get_queryset()

    def get_queryset(self):
        """Récupère le queryset avec filtres optimisés et robustes"""
        # 1. Base : Uniquement les appels d'offres
        queryset = AppelOffre.objects.filter(type_offre='APPEL_D_OFFRES')
    
        # 2. Statut (Par défaut : Ouvert)
        statut = self.request.query_params.get('statut') or self.request.query_params.get('status')
        if statut and statut.strip().lower() != 'tous':
            queryset = queryset.filter(statut=statut.strip())
        else:
            queryset = queryset.filter(statut='Ouvert')
    
        # 3. Option admin : tout voir
        show_all = self.request.query_params.get('show_all', 'false')
        if show_all.lower() == 'true':
            queryset = AppelOffre.objects.all()
    
        # 4. Type d'offre
        type_offre_param = self.request.query_params.get('type_offre')
        if type_offre_param:
            queryset = queryset.filter(type_offre=type_offre_param.strip())
    
        # 5. Mots-clés
        keyword = self.request.query_params.get('keyword') or self.request.query_params.get('search')
        if keyword:
            keyword_clean = keyword.strip()
            queryset = queryset.filter(
                Q(titre__icontains=keyword_clean) | 
                Q(organisme__icontains=keyword_clean) |
                Q(description__icontains=keyword_clean)
            )
    
        # 6. DOMAINE (Filtrage robuste avec nettoyage des espaces)
        domaine = self.request.query_params.get('domaine') or self.request.query_params.get('categorie')
        if domaine:
            domaine_clean = domaine.strip()
            if domaine_clean.lower() in ['autres', 'non classifié', 'non_classifie']:
                queryset = queryset.filter(
                    Q(domaine__isnull=True) | 
                    Q(domaine='') | 
                    Q(domaine__iexact='autres') |
                    Q(domaine__iexact='non classifié')
                )
            else:
                # ✅ Utilisation de __iexact pour une correspondance exacte insensible à la casse
                queryset = queryset.filter(domaine__iexact=domaine_clean)
    
        # 7. PAYS (Filtrage robuste avec nettoyage et majuscules)
        pays = self.request.query_params.get('pays') or self.request.query_params.get('country')
        if pays:
            pays_clean = pays.strip().upper()
            if len(pays_clean) == 2 and pays_clean.isalpha():
                queryset = queryset.filter(pays=pays_clean)
            else:
                country_codes = get_country_codes(pays_clean)
                if country_codes:
                    queryset = queryset.filter(pays__in=country_codes)
                else:
                    queryset = queryset.filter(pays__iexact=pays_clean)
    
        # 8. STRUCTURE
        structure = self.request.query_params.get('structure')
        if structure:
            structure_clean = structure.strip().lower()
            if structure_clean in ['nationale', 'internationale']:
                if structure_clean == 'nationale':
                    queryset = queryset.filter(
                        Q(organisme__icontains='Gouvernement') |
                        Q(organisme__icontains='Ministère') |
                        Q(organisme__icontains='Burkina') |
                        Q(organisme__icontains='BF') |
                        Q(pays='BF')
                    )
                elif structure_clean == 'internationale':
                    queryset = queryset.filter(
                        Q(organisme__icontains='UN') |
                        Q(organisme__icontains='ONU') |
                        Q(organisme__icontains='Banque Mondiale') |
                        Q(organisme__icontains='World Bank') |
                        Q(organisme__icontains='UEMOA') |
                        Q(organisme__icontains='Union Européenne') |
                        Q(organisme__icontains='BAD') |
                        Q(organisme__icontains='AFD') |
                        Q(organisme__icontains='UNICEF') |
                        Q(organisme__icontains='OMS') |
                        Q(organisme__icontains='WHO') |
                        Q(organisme__icontains='UNDP') |
                        Q(organisme__icontains='PNUD') |
                        ~Q(pays='BF')
                    )
    
        # 9. DATE DE PUBLICATION
        date_pub = self.request.query_params.get('date_publication')
        if date_pub:
            try:
                date_obj = datetime.strptime(date_pub.strip(), '%Y-%m-%d').date()
                queryset = queryset.filter(date_publication=date_obj)
            except (ValueError, TypeError):
                pass
    
        # 10. DATE DE CLÔTURE
        date_cloture = self.request.query_params.get('date_cloture')
        if date_cloture:
            try:
                date_obj = datetime.strptime(date_cloture.strip(), '%Y-%m-%d').date()
                queryset = queryset.filter(date_cloture__lte=date_obj)
            except (ValueError, TypeError):
                pass
    
        # 11. MAX_DAYS (expire dans X jours)
        max_days = self.request.query_params.get('max_days')
        if max_days:
            try:
                days = int(max_days.strip())
                today = timezone.now().date()
                date_limite = today + timedelta(days=days)
                queryset = queryset.filter(
                    date_cloture__gte=today,
                    date_cloture__lte=date_limite
                )
            except (ValueError, TypeError):
                pass
    
        # 12. TRI : Plus récentes d'abord
        return queryset.order_by('-date_publication', '-date_scraping')

        
    def create(self, request, *args, **kwargs):
        """
        Création d'une offre avec support d'upload de fichier
        ✅ Gère automatiquement le mode_acquisition='MANUEL'
        """
        # Forcer le mode MANUEL pour les créations via l'interface admin
        data = request.data.copy()
        if request.user.is_staff:
            data['mode_acquisition'] = 'MANUEL'
        
        serializer = self.get_serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(
            {
                'message': '✅ Offre publiée avec succès',
                'offre': serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    def perform_create(self, serializer):
        """Sauvegarde avec mode MANUEL par défaut"""
        serializer.save(mode_acquisition='MANUEL')

    def retrieve(self, request, *args, **kwargs):
        """Détails d'une offre"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)
    
    def list(self, request, *args, **kwargs):
        """Liste paginée des offres"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='recent')
    def recent_offres(self, request):
        """Offres récentes (7 derniers jours)"""
        seven_days_ago = timezone.now().date() - timedelta(days=7)
        recent = AppelOffre.objects.filter(
            date_publication__gte=seven_days_ago,
            statut='Ouvert'
        ).order_by('-date_publication', '-date_scraping')[:20]
        serializer = self.get_serializer(recent, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='create-manuel')
    def create_manuel(self, request):
        """
        Création manuelle (action explicite)
        ✅ Supporte l'upload de fichier PDF
        """
        serializer = self.get_serializer(
            data=request.data, 
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        offre = serializer.save(mode_acquisition='MANUEL')
        
        return Response({
            'message': '✅ Offre publiée avec succès.',
            'offre': AppelOffreSerializer(offre, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)
    

    
    @action(detail=True, methods=['get'], url_path='download-pdf')
    def download_pdf(self, request, pk=None):
        """
        Téléchargement du PDF
        ✅ Priorité au fichier uploadé, sinon redirection vers URL externe
        """
        offre = self.get_object()
        
        # Priorité 1 : Fichier PDF uploadé localement
        if offre.fichier_pdf and offre.fichier_pdf.name:
            try:
                if os.path.exists(offre.fichier_pdf.path):
                    return FileResponse(
                        open(offre.fichier_pdf.path, 'rb'),
                        content_type='application/pdf',
                        as_attachment=True,
                        filename=f'TDR_{offre.id}_{offre.titre[:30].replace("/", "_")}.pdf'
                    )
                else:
                    return Response(
                        {'error': 'Fichier PDF non trouvé sur le serveur'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            except Exception as e:
                print(f"Erreur lecture fichier: {e}")
                return Response(
                    {'error': 'Erreur lors de la lecture du fichier PDF'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Priorité 2 : URL externe
        if offre.url_tdr:
            return Response(
                {'redirect_url': offre.url_tdr},
                status=status.HTTP_200_OK
            )
        
        # Aucun PDF disponible
        return Response(
            {'error': 'Aucun PDF disponible pour cette offre'},
            status=status.HTTP_404_NOT_FOUND
        )


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
            
            matching_offres = []
            criteres = CritereRecherche.objects.filter(utilisateur=user)
            if criteres.exists():
                query = Q()
                for critere in criteres:
                    if critere.mots_cles:
                        query |= Q(titre__icontains=critere.mots_cles) | Q(description__icontains=critere.mots_cles)
                if query:
                    matching_offres = AppelOffre.objects.filter(query).order_by('-date_publication')[:10]
            
            profile_data = None
            if profile:
                try:
                    profile_data = ProfilExpertSerializer(profile).data
                except Exception:
                    pass
            
            return Response({
                'user': {'id': user.id, 'email': user.email, 'nom': f"{user.first_name} {user.last_name}".strip(), 'role': user.role},
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
                print(f"❌ ERREUR DASHBOARD EXPERT: {e}\n{traceback.format_exc()}")
            return Response({'error': 'Erreur serveur interne'}, status=500)

    def _serialize_offres(self, offres):
        try:
            return AppelOffreSerializer(offres, many=True).data
        except Exception:
            return []

    def _get_next_steps(self, user, profile):
        steps = []
        if not profile or not getattr(profile, 'cv_fichier', None):
            steps.append({'priority': 'high', 'action': 'upload_cv', 'message': 'Téléchargez votre CV', 'url': '/expert/profile'})
        if not steps:
            steps.append({'priority': 'low', 'action': 'browse_offres', 'message': 'Consultez les offres', 'url': '/offres'})
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
            bureau_data = BureauEtudeSerializer(bureau).data if bureau else None
            
            return Response({
                'user': {'id': user.id, 'email': user.email, 'nom': f"{user.first_name} {user.last_name}".strip(), 'role': user.role},
                'bureau': bureau_data,
                'stats': {'profile_complete': bool(bureau and getattr(bureau, 'cv_fichier', None))},
                'next_steps': self._get_next_steps(user, bureau)
            })
        except Exception as e:
            if settings.DEBUG:
                import traceback
                print(f"❌ ERREUR DASHBOARD BUREAU: {e}\n{traceback.format_exc()}")
            return Response({'error': 'Erreur serveur interne'}, status=500)

    def _get_next_steps(self, user, bureau):
        steps = []
        if not bureau or not getattr(bureau, 'cv_fichier', None):
            steps.append({'priority': 'high', 'action': 'upload_cv', 'message': 'Téléchargez les documents', 'url': '/bureau/profile'})
        if not steps:
            steps.append({'priority': 'low', 'action': 'browse_offres', 'message': 'Consultez les offres', 'url': '/offres'})
        return steps


# =============================================================================
# GESTION DES PROFILS - EXPERT
# =============================================================================

class ProfilExpertViewSet(viewsets.ModelViewSet):
    """Gestion du profil Expert - Accès Expert uniquement"""
    serializer_class = ProfilExpertSerializer
    permission_classes = [IsExpert]
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']

    def get_queryset(self):
        return ProfilExpert.objects.filter(utilisateur=self.request.user)

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(utilisateur=self.request.user)

    @action(detail=False, methods=['put', 'patch'], url_path='update-profile')
    def update_profile(self, request):
        try:
            # ✅ CORRECTION : Utiliser get_or_create pour éviter les erreurs si le profil n'existe pas
            profile, created = ProfilExpert.objects.get_or_create(utilisateur=request.user)
            
            # ✅ Utiliser le serializer avec partial=True pour accepter les mises à jour partielles
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'Profil mis à jour avec succès', 
                    'profile': serializer.data
                }, status=status.HTTP_200_OK)
            else:
                # Retourne les erreurs de validation précises au frontend
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({'error': f'Erreur lors de la mise à jour: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='upload-cv')
    def upload_cv(self, request):
        try:
            profile, created = ProfilExpert.objects.get_or_create(utilisateur=request.user)
            if 'cv_fichier' not in request.FILES:
                return Response({'error': 'Fichier CV requis'}, status=status.HTTP_400_BAD_REQUEST)
            
            profile.cv_fichier = request.FILES['cv_fichier']
            profile.save()
            
            return Response({
                'message': 'CV téléchargé avec succès.',
                'cv_url': profile.cv_fichier.url if profile.cv_fichier else None,
                'is_profile_complete': bool(profile.domaines_competence and profile.cv_fichier)
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# =============================================================================
# GESTION DES PROFILS - BUREAU
# =============================================================================
class BureauEtudeViewSet(viewsets.ModelViewSet):
    """Gestion du profil Bureau d'Étude - Accès Bureau uniquement"""
    serializer_class = BureauEtudeSerializer
    permission_classes = [IsBureau]

    def get_queryset(self):
        return BureauEtude.objects.filter(gestionnaire=self.request.user)

    def perform_create(self, serializer):
        serializer.save(gestionnaire=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(gestionnaire=self.request.user)
    
    @action(detail=False, methods=['put', 'patch'], url_path='update-profile')
    def update_profile(self, request):
        try:
            # ✅ CORRECTION : Utiliser get_or_create au lieu de request.user.bureauetude
            bureau, created = BureauEtude.objects.get_or_create(gestionnaire=request.user)
            
            allowed_fields = ['nom_structure', 'pays', 'adresse', 'domaine_activite', 'email_contact', 'telephone', 'site_web']
            for field in allowed_fields:
                if field in request.data:
                    setattr(bureau, field, request.data[field])
            bureau.save()
            
            return Response({
                'message': 'Profil mis à jour avec succès.',
                'profile': BureauEtudeSerializer(bureau).data,
                'is_profile_complete': bool(bureau.nom_structure and bureau.email_contact and bureau.telephone)
            })
        except Exception as e:
            return Response({'error': f'Erreur lors de la mise à jour: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='my-profile')
    def my_profile(self, request):
        try:
            # ✅ CORRECTION : Utiliser get_or_create
            bureau, created = BureauEtude.objects.get_or_create(gestionnaire=request.user)
            return Response({
                'profile': BureauEtudeSerializer(bureau).data, 
                'is_complete': bool(bureau.nom_structure and bureau.email_contact and bureau.telephone)
            })
        except Exception as e:
            return Response({'error': f'Erreur: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

# =============================================================================
# CRITÈRES DE RECHERCHE & NEWSLETTER
# =============================================================================

class CritereRechercheViewSet(viewsets.ModelViewSet):
    """Gestion des critères de recherche pour les alertes email"""
    serializer_class = CritereRechercheSerializer
    permission_classes = [IsExpert]

    def get_queryset(self):
        return CritereRecherche.objects.filter(utilisateur=self.request.user)

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)



class NewsletterSubscriptionView(generics.CreateAPIView):
    """Inscription à la newsletter avec email de confirmation"""
    queryset = InscriptionNewsletter.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = NewsletterSubscriptionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        # ✅ ENVOI DE L'EMAIL DE CONFIRMATION
        try:
            nom = getattr(instance, 'nom', None) or getattr(instance, 'name', None)
            email_sent = EmailService.send_newsletter_confirmation(
                email=instance.email,
                nom=nom
            )
            
            if email_sent:
                logger.info(f"✅ Email de confirmation envoyé à {instance.email}")
            else:
                logger.warning(f"⚠️ Échec envoi email à {instance.email}")
        except Exception as e:
            logger.error(f"❌ Erreur envoi email newsletter: {e}")
            # On continue même si l'email échoue
        
        return Response({
            'message': 'Inscription réussie ! Un email de confirmation vous a été envoyé.',
            'email_sent': True
        }, status=status.HTTP_201_CREATED)

# =============================================================================
# MESSAGERIE
# =============================================================================

from offres.services.email_service import EmailService  # ✅ À ajouter en haut du fichier

class MessageViewSet(viewsets.ModelViewSet):
    """API pour la messagerie entre utilisateurs et administrateur"""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Message.objects.all()
        return Message.objects.filter(Q(expediteur=user) | Q(destinataire=user))
    
    def perform_create(self, serializer):
        user = self.request.user
        destinataire_id = self.request.data.get('destinataire')
        
        if not destinataire_id:
            admin = User.objects.filter(is_superuser=True).first()
            destinataire = admin
        else:
            destinataire = User.objects.get(id=destinataire_id)
        
        message = serializer.save(expediteur=user, destinataire=destinataire)
        
        # ✅ Notification interne
        Notification.objects.create(
            destinataire=destinataire,
            objet=f"Nouveau message: {serializer.validated_data.get('sujet', 'Sans sujet')}",
            message=f"Message de {user.email}: {serializer.validated_data.get('contenu', '')[:100]}",
            offre_liee=None
        )
        
        # ✅ ENVOI D'EMAIL AU DESTINATAIRE
        try:
            sender_name = f"{user.first_name} {user.last_name}".strip() or user.email
            EmailService.send_new_message_notification(
                recipient_email=destinataire.email,
                sender_name=sender_name,
                subject=serializer.validated_data.get('sujet', 'Sans sujet'),
                message_preview=serializer.validated_data.get('contenu', '')[:200]
            )
        except Exception as e:
            logger.error(f"❌ Erreur envoi email message: {e}")

    @action(detail=True, methods=['post'], url_path='marquer-lu')
    def marquer_lu(self, request, pk=None):
        message = self.get_object()
        if message.destinataire != request.user:
            return Response({'error': 'Vous ne pouvez pas marquer ce message'}, status=status.HTTP_403_FORBIDDEN)
        message.est_lu = True
        message.save()
        return Response({'status': 'Message marqué comme lu', 'est_lu': True}, status=status.HTTP_200_OK)
    
    # ✅ NOUVELLE ACTION : Répondre à un message (admin uniquement)
    @action(detail=True, methods=['post'], url_path='repondre', permission_classes=[permissions.IsAdminUser])
    def repondre(self, request, pk=None):
        """Permet à l'administrateur de répondre à un message"""
        try:
            message_original = self.get_object()
        except Message.DoesNotExist:
            return Response({'error': 'Message non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        
        contenu = request.data.get('contenu', '').strip()
        if not contenu:
            return Response({'error': 'Contenu requis'}, status=status.HTTP_400_BAD_REQUEST)
        
        # ✅ Créer la réponse
        reponse = Message.objects.create(
            expediteur=request.user,
            destinataire=message_original.expediteur,
            sujet=f"RE: {message_original.sujet}",
            contenu=contenu,
            est_reponse=True,
            reponse_contenu=contenu,
            message_original=message_original
        )
        
        # ✅ Marquer le message original comme lu
        message_original.est_lu = True
        message_original.save()
        
        # ✅ Notification interne pour l'expéditeur original (l'expert)
        Notification.objects.create(
            destinataire=message_original.expediteur,
            objet="Réponse à votre message",
            message=f"L'administrateur a répondu à votre message: {contenu[:200]}",
            offre_liee=None
        )
        
        # ✅ ENVOI D'EMAIL À L'EXPERT
        try:
            admin_name = f"{request.user.first_name} {request.user.last_name}".strip() or "L'administrateur"
            EmailService.send_new_message_notification(
                recipient_email=message_original.expediteur.email,
                sender_name=admin_name,
                sujet=f"RE: {message_original.sujet}",
                message_preview=contenu[:200]
            )
            logger.info(f"✅ Email de réponse envoyé à {message_original.expediteur.email}")
        except Exception as e:
            logger.error(f"❌ Erreur envoi email réponse: {e}")
        
        return Response({
            'message': 'Réponse envoyée',
            'reponse': MessageSerializer(reponse).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], url_path='envoyer-admin')
    def envoyer_a_admin(self, request):
        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            return Response({'error': 'Aucun administrateur trouvé'}, status=404)
        sujet = request.data.get('sujet', '')
        contenu = request.data.get('contenu', '')
        if not sujet or not contenu:
            return Response({'error': 'Sujet et contenu requis'}, status=400)
        
        message = Message.objects.create(
            expediteur=request.user, 
            destinataire=admin, 
            sujet=sujet, 
            contenu=contenu
        )
        
        # ✅ Notification interne pour l'admin
        Notification.objects.create(
            destinataire=admin, 
            objet=f"Nouveau message de {request.user.email}", 
            message=contenu[:200], 
            offre_liee=None
        )
        
        # ✅ ENVOI D'EMAIL À L'ADMIN
        try:
            sender_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.email
            EmailService.send_new_message_notification(
                recipient_email=admin.email,
                sender_name=sender_name,
                subject=sujet,
                message_preview=contenu[:200]
            )
        except Exception as e:
            logger.error(f"❌ Erreur envoi email à admin: {e}")
        
        return Response(MessageSerializer(message).data, status=201)
    
    @action(detail=False, methods=['get'], url_path='non-lus')
    def messages_non_lus(self, request):
        messages = Message.objects.filter(destinataire=request.user, est_lu=False)
        return Response({
            'count': messages.count(), 
            'results': MessageSerializer(messages, many=True).data
        })
    
    @action(detail=False, methods=['get'], url_path='conversation-admin')
    def conversation_avec_admin(self, request):
        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            return Response({'error': 'Aucun administrateur trouvé'}, status=404)
        messages = Message.objects.filter(
            Q(expediteur=request.user, destinataire=admin) | Q(expediteur=admin, destinataire=request.user)
        ).order_by('date_envoi')
        return Response(MessageSerializer(messages, many=True).data)

# =============================================================================
# ADMIN DASHBOARD & STATS
# ==========================================================================
class AdminDashboardView(APIView):
    """Tableau de bord administrateur avec statistiques"""
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        # =============================================================
        # 1. STATISTIQUES DES OFFRES (sans les offres de démonstration)
        # =============================================================
        
        # ✅ Exclure les offres de démonstration
        offres_reelles = AppelOffre.objects.exclude(
            Q(titre__icontains='demo') | Q(titre__icontains='Demo')
        )
        
        total_offres = AppelOffre.objects.filter(statut='Ouvert').count()
        offres_scrapees = offres_reelles.filter(mode_acquisition='AUTO').count()
        offres_manuelles = offres_reelles.filter(mode_acquisition='MANUEL').count()
        offres_actives = offres_reelles.filter(statut='Ouvert').count()
        
        # Offres par source (uniquement les sources avec offres)
        offres_par_source = []
        for s in SourceScraping.objects.all():
            count = offres_reelles.filter(source_origine=s).count()
            if count > 0:
                offres_par_source.append({'nom': s.nom, 'count': count})
        
        # =============================================================
        # 2. STATISTIQUES DES UTILISATEURS
        # =============================================================
        
        date_limite = timezone.now() - timedelta(days=30)
        
        total_utilisateurs = Utilisateur.objects.count()
        experts = Utilisateur.objects.filter(role='EXPERT').count()
        bureaux = Utilisateur.objects.filter(role='BUREAU').count()
        admins = Utilisateur.objects.filter(is_staff=True).count()
        nouveaux_30j = Utilisateur.objects.filter(date_joined__gte=date_limite).count()
        
        # =============================================================
        # 3. STATISTIQUES DES CONNEXIONS
        # =============================================================
        
        try:
            from offres.models import HistoriqueConnexion
            connexions_aujourdhui = HistoriqueConnexion.objects.filter(
                date_connexion__date=timezone.now().date()
            ).count()
            connexions_semaine = HistoriqueConnexion.objects.filter(
                date_connexion__gte=timezone.now() - timedelta(days=7)
            ).count()
        except (ImportError, NameError):
            connexions_aujourdhui = 0
            connexions_semaine = 0
        
        # =============================================================
        # 4. STATISTIQUES DES MESSAGES
        # =============================================================
        
        try:
            from offres.models import Message
            messages_non_lus = Message.objects.filter(
                destinataire=request.user, 
                est_lu=False
            ).count()
            messages_total = Message.objects.filter(
                Q(expediteur=request.user) | Q(destinataire=request.user)
            ).count()
            messages_envoyes = Message.objects.filter(expediteur=request.user).count()
            messages_recus = Message.objects.filter(destinataire=request.user).count()
        except (ImportError, NameError):
            messages_non_lus = 0
            messages_total = 0
            messages_envoyes = 0
            messages_recus = 0
        
        # =============================================================
        # 5. STATISTIQUES DES SUGGESTIONS
        # =============================================================
        
        try:
            from offres.models import SuggestionOffre
            suggestions_envoyees = SuggestionOffre.objects.count()
            suggestions_consultees = SuggestionOffre.objects.filter(
                est_consulte_par_expert=True
            ).count()
            suggestions_en_attente = suggestions_envoyees - suggestions_consultees
        except (ImportError, NameError):
            suggestions_envoyees = 0
            suggestions_consultees = 0
            suggestions_en_attente = 0
        
        # =============================================================
        # 6. CONSTRUCTION DE LA RÉPONSE
        # =============================================================
        
        data = {
            'offres': {
                'total': total_offres,
                'scrapees': offres_scrapees,
                'manuelles': offres_manuelles,
                'actives': offres_actives,
                'par_source': offres_par_source,
            },
            'utilisateurs': {
                'total': total_utilisateurs,
                'experts': experts,
                'bureaux': bureaux,
                'admins': admins,
                'nouveaux_30j': nouveaux_30j,
            },
            'connexions': {
                'aujourdhui': connexions_aujourdhui,
                'semaine': connexions_semaine,
            },
            'messages': {
                'non_lus': messages_non_lus,
                'total': messages_total,
                'envoyes': messages_envoyes,
                'recus': messages_recus,
            },
            'suggestions': {
                'envoyees': suggestions_envoyees,
                'consultees': suggestions_consultees,
                'en_attente': suggestions_en_attente,
            }
        }
        
        return Response(data)

# =============================================================================
# ADMIN - GESTION DES SOURCES DE SCRAPPING
# =============================================================================

class AdminSourceViewSet(viewsets.ModelViewSet):
    """CRUD complet pour les sources de scraping - Admin uniquement"""
    serializer_class = SourceScrapingSerializer
    permission_classes = [IsAdmin]
    queryset = SourceScraping.objects.all()
    pagination_class = None 
    @action(detail=False, methods=['post'], url_path='run')
    def run_scraping(self, request):
        import time
        start_time = time.time()
    
        try:
            source_ids = request.data.get('source_ids', [])
        
            print(f"\n{'='*60}")
            print(f"🚀 DÉBUT DU SCRAPPING - {len(source_ids)} source(s)")
            print(f"{'='*60}")
        
            if not isinstance(source_ids, list):
                return Response({'error': 'source_ids doit être une liste'}, status=status.HTTP_400_BAD_REQUEST)
            if not all(isinstance(i, int) for i in source_ids):
                return Response({'error': 'source_ids doit contenir des identifiants entiers'}, status=status.HTTP_400_BAD_REQUEST)
            if not source_ids:
                return Response({'error': 'Aucune source sélectionnée'}, status=status.HTTP_400_BAD_REQUEST)
        
            results = []
            for idx, source_id in enumerate(source_ids, 1):
                source_start = time.time()
                print(f"\n[{idx}/{len(source_ids)}] 🔍 Scraping source ID {source_id}...")
            
                try:
                    source = SourceScraping.objects.filter(id=source_id, est_actif=True).first()
                    if not source:
                        print(f"  ⚠️ Source {source_id} inactive ou inexistante")
                        results.append({
                            'source_id': source_id, 
                            'status': 'skipped', 
                            'reason': 'Source inactive ou inexistante'
                        })
                        continue
                
                    print(f"  📡 Source: {source.nom}")
                    print(f"  🌐 URL: {source.url_racine}")
                
                    # Lancer le scraping
                    result = run_scheduled_scraping_task(source_id=source_id)
                
                    source.last_scraped = timezone.now()
                    source.save(update_fields=['last_scraped'])
                
                    new_count = result.get('new', 0) if isinstance(result, dict) else 0
                    updated_count = result.get('updated', 0) if isinstance(result, dict) else 0
                
                    elapsed = time.time() - source_start
                    print(f"  ✅ Terminé en {elapsed:.2f}s")
                    print(f"     - Nouvelles offres: {new_count}")
                    print(f"     - Offres mises à jour: {updated_count}")
                
                    results.append({
                        'source_id': source_id,
                        'status': 'success',
                        'new': new_count,
                        'updated': updated_count,
                        'source_name': source.nom,
                        'duration': round(elapsed, 2)
                    })
                
                except Exception as task_err:
                    elapsed = time.time() - source_start
                    print(f"  ❌ Erreur après {elapsed:.2f}s: {task_err}")
                    print(traceback.format_exc())
                    results.append({
                        'source_id': source_id, 
                        'status': 'error', 
                        'error': str(task_err)
                    })
        
            total_duration = time.time() - start_time
            success_count = len([r for r in results if r['status'] == 'success'])
            error_count = len([r for r in results if r['status'] == 'error'])
            skipped_count = len([r for r in results if r['status'] == 'skipped'])
        
            print(f"\n{'='*60}")
            print(f"🏁 FIN DU SCRAPPING en {total_duration:.2f}s")
            print(f"   ✅ Succès: {success_count}")
            print(f"   ❌ Erreurs: {error_count}")
            print(f"   ⚠️ Ignorées: {skipped_count}")
            print(f"{'='*60}\n")
        
            return Response({
                'message': f'Scraping terminé en {total_duration:.2f}s: {success_count} succès, {error_count} erreurs, {skipped_count} ignorées',
                'results': results,
                'summary': {
                    'total': len(source_ids), 
                    'success': success_count, 
                    'errors': error_count, 
                    'skipped': skipped_count,
                    'duration': round(total_duration, 2)
                }
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(f"❌ ERREUR CRITIQUE run_scraping: {e}")
            print(traceback.format_exc())
            return Response({'error': f'Erreur serveur: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminSourcesRunView(APIView):
    """Endpoint alternatif pour lancer le scraping - Admin uniquement"""
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        source_ids = request.data.get('source_ids', [])
        if not source_ids:
            return Response({'error': 'Aucune source sélectionnée'}, status=400)
        
        sources = SourceScraping.objects.filter(id__in=source_ids, est_actif=True)
        if not sources.exists():
            return Response({'error': 'Aucune source active trouvée'}, status=400)
        
        total_new, total_updated = 0, 0
        for source in sources:
            try:
                result = run_scheduled_scraping_task(source_id=source.id)
                if isinstance(result, dict):
                    total_new += result.get('new', 0)
                    total_updated += result.get('updated', 0)
                source.last_scraped = timezone.now()
                source.save(update_fields=['last_scraped'])
            except Exception as e:
                print(f"❌ Erreur scraping {source.nom}: {e}")
        
        return Response({
            'message': f'Scraping terminé sur {sources.count()} source(s)',
            'new': total_new, 'updated': total_updated, 'sources': sources.count()
        })


# =============================================================================
# ADMIN - GESTION DES UTILISATEURS (✅ CORRIGÉ)
# =============================================================================


class AdminUtilisateurViewSet(viewsets.ModelViewSet):
    """Gestion complète des utilisateurs par l'admin"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return Utilisateur.objects.exclude(id=self.request.user.id)
    
    def perform_create(self, serializer):
        """Création d'un utilisateur par l'admin - ACTIF par défaut"""
        # ✅ Récupérer le mot de passe des données de la requête
        raw_password = self.request.data.get('password', '')
        
        # Sauvegarder l'utilisateur SANS mot de passe d'abord
        user = serializer.save(is_active=True)
        
        # ✅ Définir le mot de passe correctement
        if raw_password and len(raw_password) >= 6:
            user.set_password(raw_password)
            user.save(update_fields=['password'])
            if settings.DEBUG:
                print(f"✅ Utilisateur créé et activé : {user.email} | Mot de passe défini")
        else:
            # Mot de passe par défaut si non fourni (à éviter en prod)
            default_password = 'DefaultPass123!'
            user.set_password(default_password)
            user.save(update_fields=['password'])
            if settings.DEBUG:
                print(f"⚠️ Utilisateur créé avec mot de passe par défaut : {user.email}")
        
        # ✅ Forcer is_active = True (double vérification)
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=['is_active'])
        
        # Création automatique du profil lié
        if user.role == 'EXPERT':
            ProfilExpert.objects.get_or_create(utilisateur=user)
        elif user.role == 'BUREAU':
            BureauEtude.objects.get_or_create(gestionnaire=user)
        
        if settings.DEBUG:
            print(f"✅ Utilisateur {user.email} : is_active={user.is_active}, role={user.role}")
    
    def perform_update(self, serializer):
        user = serializer.save()
        if settings.DEBUG:
            print(f"Admin {self.request.user.email} a modifié {user.email}")
    
    @action(detail=True, methods=['patch'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        try:
            user = self.get_object()
            new_status = request.data.get('is_active')
            if new_status is not None:
                user.is_active = bool(new_status)
            else:
                user.is_active = not user.is_active
            
            user.save(update_fields=['is_active'])
            
            content_type = ContentType.objects.get_for_model(user)
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=content_type.pk,
                object_id=user.pk,
                object_repr=str(user),
                action_flag=2,
                change_message=f'Utilisateur {"bloqué" if not user.is_active else "débloqué"} par admin'
            )
            
            return Response({
                'message': f'Utilisateur {user.email} {"bloqué" if not user.is_active else "débloqué"}',
                'is_active': user.is_active,
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"❌ ERREUR toggle_active: {e}")
            print(traceback.format_exc())
            return Response({'error': f'Erreur serveur: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['delete'], url_path='force-delete')
    def force_delete(self, request, pk=None):
        try:
            user = self.get_object()
            if user.is_superuser or user.id == request.user.id:
                return Response({'error': 'Impossible de supprimer cet utilisateur'}, status=status.HTTP_403_FORBIDDEN)
            
            user_email = user.email
            user_id = user.pk
            content_type = ContentType.objects.get_for_model(user)
            user.delete()
            
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=content_type.pk,
                object_id=user_id,
                object_repr=f'Utilisateur supprimé: {user_email}',
                action_flag=3,
                change_message=f'Utilisateur {user_email} supprimé définitivement par admin'
            )
            return Response({'message': f'Utilisateur {user_email} supprimé'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"❌ ERREUR force_delete: {e}")
            print(traceback.format_exc())
            return Response({'error': f'Erreur serveur: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# ADMIN - HISTORIQUE DES CONNEXIONS
# =============================================================================

class AdminConnexionHistoriqueView(APIView):
    """Historique des connexions des utilisateurs"""
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        connexions = HistoriqueConnexion.objects.all().select_related('utilisateur').order_by('-date_connexion')[:100]
        return Response(HistoriqueConnexionSerializer(connexions, many=True).data)


# =============================================================================
# ADMIN - GESTION DES SUGGESTIONS
# =============================================================================

class AdminSuggestionOffreViewSet(viewsets.ModelViewSet):
    """Gestion des suggestions expert/offre par l'admin"""
    serializer_class = SuggestionOffreSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = SuggestionOffre.objects.select_related('expert__utilisateur', 'offre')
    
    def create(self, request, *args, **kwargs):
        """
        ✅ Création d'une suggestion avec conversion automatique ID utilisateur → ID ProfilExpert
        """
        print(f"📥 Données reçues: {request.data}")
        
        # Copier les données pour modification
        data = request.data.copy()
        
        # ✅ Convertir l'ID utilisateur en ID ProfilExpert si nécessaire
        if 'expert' in data:
            try:
                expert_id = int(data['expert'])
                
                # Essayer d'abord comme ID de ProfilExpert
                try:
                    profil = ProfilExpert.objects.get(id=expert_id)
                    data['expert'] = profil.id
                    print(f"✅ ID ProfilExpert trouvé: {profil.id}")
                except ProfilExpert.DoesNotExist:
                    # Essayer comme ID d'utilisateur
                    try:
                        user = Utilisateur.objects.get(id=expert_id)
                        profil = ProfilExpert.objects.get(utilisateur=user)
                        data['expert'] = profil.id
                        print(f"✅ Converti ID utilisateur {expert_id} → ID ProfilExpert {profil.id}")
                    except Utilisateur.DoesNotExist:
                        return Response(
                            {'expert': [f'Utilisateur ID {expert_id} non trouvé']},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    except ProfilExpert.DoesNotExist:
                        return Response(
                            {'expert': [f'Profil expert non trouvé pour l\'utilisateur ID {expert_id}']},
                            status=status.HTTP_400_BAD_REQUEST
                        )
            except (ValueError, TypeError):
                return Response(
                    {'expert': ['ID expert invalide']},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Créer le serializer avec les données modifiées
        serializer = self.get_serializer(data=data)
        
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        else:
            print(f"❌ Erreurs de validation: {serializer.errors}")
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
    
    
    def perform_create(self, serializer):
        suggestion = serializer.save()
        
        # ✅ Notification interne
        Notification.objects.create(
            destinataire=suggestion.expert.utilisateur,
            offre_liee=suggestion.offre,
            objet='Nouvelle suggestion d\'offre',
            message=f'Un administrateur vous suggère: {suggestion.offre.titre[:100]}'
        )
        
        # ✅ ENVOI D'EMAIL À L'EXPERT
        try:
            expert_name = f"{suggestion.expert.utilisateur.first_name} {suggestion.expert.utilisateur.last_name}".strip()
            EmailService.send_suggestion_notification(
                expert_email=suggestion.expert.utilisateur.email,
                expert_name=expert_name,
                offre_titre=suggestion.offre.titre,
                admin_name=f"{self.request.user.first_name} {self.request.user.last_name}".strip() or "L'administrateur"
            )
        except Exception as e:
            logger.error(f"❌ Erreur envoi email suggestion: {e}")
    
    @action(detail=True, methods=['post'], url_path='envoyer')
    def envoyer_suggestion(self, request, pk=None):
        suggestion = self.get_object()
        Notification.objects.create(
            destinataire=suggestion.expert.utilisateur,
            offre_liee=suggestion.offre,
            objet=f"Suggestion: {suggestion.offre.titre}",
            message=f"L'admin vous suggère cette offre: {suggestion.offre.titre}"
        )
        return Response({'status': 'Suggestion envoyée à l\'expert'})
    
    @action(detail=True, methods=['delete'], url_path='force-delete')
    def force_delete(self, request, pk=None):
        suggestion = self.get_object()
        suggestion_id = suggestion.id
        suggestion.delete()
        LogEntry.objects.log_action(
            user_id=request.user.id,
            content_type_id=suggestion._meta.content_type_id,
            object_id=suggestion_id,
            object_repr=f'Suggestion #{suggestion_id}',
            action_flag=3,
            change_message='Suggestion supprimée par admin'
        )
        return Response({'message': 'Suggestion supprimée'}, status=status.HTTP_200_OK)

# =============================================================================
# ADMIN - EFFACER L'HISTORIQUE
# =============================================================================


class AdminHistoryView(APIView):
    """Gestion de l'historique des connexions (Visualisation et suppression globale)"""
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        """Récupère les dernières connexions pour l'affichage de l'historique"""
        # On récupère les 100 dernières connexions
        connexions = HistoriqueConnexion.objects.select_related('utilisateur').order_by('-date_connexion')[:100]
        
        return Response([{
            'id': c.id,
            'utilisateur_email': c.utilisateur.email if c.utilisateur else 'Inconnu',
            'utilisateur_nom': f"{c.utilisateur.first_name} {c.utilisateur.last_name}".strip() if c.utilisateur else 'Inconnu',
            'utilisateur_role': c.utilisateur.role if c.utilisateur else 'EXPERT',
            'date_action': c.date_connexion,  # Aligné avec la clé attendue par le Front
            'ip_address': c.ip_address,
            'user_agent': c.user_agent
        } for c in connexions])
    
    def post(self, request):
        """Vide l'historique suite à la validation du formulaire de l'image"""
        # Vérification stricte du texte saisi dans le formulaire React
        if request.data.get('confirm') != 'EFFACER TOUT':
            return Response(
                {'error': '❌ Confirmation invalide : vous devez taper "EFFACER TOUT"'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Suppression effective de toutes les lignes dans la table HistoriqueConnexion
        count, _ = HistoriqueConnexion.objects.all().delete()
        
        return Response(
            {'message': f'✅ {count} entrées d\'historique ont été supprimées avec succès.'}, 
            status=status.HTTP_200_OK
        )

# =============================================================================
# NOTIFICATIONS & PRÉFÉRENCES (✅ DOUBLON SUPPRIMÉ, UNIQUE VERSION SÉCURISÉE)
# =============================================================================

class NotificationUserViewSet(viewsets.ModelViewSet):
    """Gestion des notifications utilisateur"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(destinataire=self.request.user).order_by('-date_envoi')

    @action(detail=True, methods=['post'], url_path='marquer-lue')
    def marquer_lue(self, request, pk=None):
        notification = self.get_object()
        if notification.destinataire == request.user:
            notification.est_lue = True
            notification.save()
            return Response({'status': 'Notification marquée comme lue'})
        return Response({'error': 'Vous ne pouvez pas modifier cette notification'}, status=403)


class PreferenceAlerteViewSet(viewsets.ModelViewSet):
    """Gestion des préférences d'alertes"""
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return []
    def get_object(self):
        return None


# =============================================================================
# OFFRES PUBLIQUES (VISITEURS NON CONNECTÉS)
# =============================================================================

class OffresPubliquesView(generics.ListAPIView):
    """Liste des offres accessible aux visiteurs (non connectés)"""
    serializer_class = AppelOffreSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['pays', 'statut']
    search_fields = ['titre', 'organisme', 'description']
    ordering_fields = ['date_publication', 'date_cloture']
    ordering = ['-date_publication']
    
    def get_queryset(self):
        return AppelOffre.objects.filter(statut='Ouvert')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


# =============================================================================
# TÉLÉCHARGEMENT DE PDF
# =============================================================================



class TelechargerPDFView(APIView):
    """
    Vue pour télécharger le PDF associé à une offre
    URL: /api/offres/<offre_id>/download-pdf/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, offre_id):
        try:
            offre = AppelOffre.objects.get(id=offre_id)
        except AppelOffre.DoesNotExist:
            return Response(
                {'error': 'Offre non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Cas 1: PDF stocké localement
        if offre.fichier_pdf and offre.fichier_pdf.name:
            try:
                # Vérifier si le fichier existe
                if os.path.exists(offre.fichier_pdf.path):
                    return FileResponse(
                        open(offre.fichier_pdf.path, 'rb'),
                        content_type='application/pdf',
                        as_attachment=True,
                        filename=f'TDR_{offre.id}.pdf'
                    )
                else:
                    return Response(
                        {'error': 'Fichier PDF non trouvé sur le serveur'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            except Exception as e:
                print(f"Erreur: {e}")
                return Response(
                    {'error': 'Erreur lors de la lecture du PDF'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Cas 2: URL externe (redirection)
        if offre.url_tdr:
            return Response(
                {'redirect_url': offre.url_tdr},
                status=status.HTTP_200_OK
            )
        
        # Cas 3: Aucun PDF
        return Response(
            {'error': 'Aucun PDF disponible pour cette offre'},
            status=status.HTTP_404_NOT_FOUND
        )


class SourceScrapingViewSet(viewsets.ModelViewSet):
    queryset = SourceScraping.objects.all()
    serializer_class = SourceScrapingSerializer
    
    def create(self, request, *args, **kwargs):
        try:
            print(f" Données reçues: {request.data}")  # ← Debug
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            print(f"❌ Erreur création source: {e}")  # ← Debug
            print(f"❌ Erreurs de validation: {serializer.errors if 'serializer' in locals() else 'N/A'}")
            return Response(
                {"error": str(e), "details": serializer.errors if 'serializer' in locals() else None},
                status=status.HTTP_400_BAD_REQUEST
            )



logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """
    Étape 1 : L'utilisateur demande la réinitialisation en fournissant son email
    """
    serializer = PasswordResetRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'error': 'Email invalide'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    email = serializer.validated_data['email'].lower()
    
    try:
        user = User.objects.get(email=email)
        
        # Invalider les anciens tokens
        PasswordResetToken.objects.filter(user=user, used=False).update(used=True)
        
        # Créer un nouveau token
        reset_token = PasswordResetToken.objects.create(user=user)
        
        # ✅ ENVOI SYNCHRONE (sans Celery) - Fonctionne sur Windows
        from .tasks import send_password_reset_email
        try:
            # Appel direct sans .delay()
            send_password_reset_email(user.email, reset_token.token)
            logger.info(f"✅ Email de réinitialisation envoyé à {email}")
        except Exception as email_error:
            logger.error(f"❌ Erreur envoi email: {email_error}")
            # On continue même si l'email échoue (l'utilisateur peut redemander)
        
        # TOUJOURS retourner succès même si l'email n'existe pas (sécurité)
        return Response(
            {
                'message': 'Si cet email est associé à un compte, vous recevrez un lien de réinitialisation.',
                'email': email
            },
            status=status.HTTP_200_OK
        )
        
    except User.DoesNotExist:
        # Sécurité : ne pas révéler si l'email existe ou non
        return Response(
            {
                'message': 'Si cet email est associé à un compte, vous recevrez un lien de réinitialisation.'
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"❌ Erreur demande réinitialisation: {e}")
        return Response(
            {'error': 'Une erreur est survenue. Veuillez réessayer.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """
    Étape 2 : L'utilisateur confirme la réinitialisation avec le token et le nouveau mot de passe
    """
    serializer = PasswordResetConfirmSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'error': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    token_str = serializer.validated_data['token']
    new_password = serializer.validated_data['new_password']
    
    try:
        # Récupérer le token
        reset_token = PasswordResetToken.objects.get(token=token_str)
        
        # Vérifier la validité
        if not reset_token.is_valid:
            return Response(
                {'error': 'Ce lien a expiré ou a déjà été utilisé. Veuillez faire une nouvelle demande.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mettre à jour le mot de passe
        user = reset_token.user
        user.set_password(new_password)
        user.save()
        
        # Marquer le token comme utilisé
        reset_token.used = True
        reset_token.save()
        
        logger.info(f"✅ Mot de passe réinitialisé pour {user.email}")
        
        return Response(
            {'message': 'Votre mot de passe a été réinitialisé avec succès. Vous pouvez maintenant vous connecter.'},
            status=status.HTTP_200_OK
        )
        
    except PasswordResetToken.DoesNotExist:
        return Response(
            {'error': 'Lien de réinitialisation invalide.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"❌ Erreur confirmation réinitialisation: {e}")
        return Response(
            {'error': 'Une erreur est survenue. Veuillez réessayer.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def password_reset_validate_token(request, token):
    """
    Vérifie si un token est valide (utilisé avant d'afficher le formulaire)
    """
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        if reset_token.is_valid:
            return Response({'valid': True}, status=status.HTTP_200_OK)
        else:
            return Response(
                {'valid': False, 'error': 'Ce lien a expiré ou a déjà été utilisé.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except PasswordResetToken.DoesNotExist:
        return Response(
            {'valid': False, 'error': 'Lien de réinitialisation invalide.'},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_user_details(request, user_id):
    """
    Récupère les détails complets d'un utilisateur avec son profil
    ✅ CORRIGÉ : Utilise les vrais noms de champs des modèles
    """
    try:
        user = get_object_or_404(Utilisateur, id=user_id)
        
        # Informations de base
        user_data = {
            'id': user.id,
            'email': user.email,
            'first_name': getattr(user, 'first_name', ''),
            'last_name': getattr(user, 'last_name', ''),
            'role': getattr(user, 'role', 'INCONNU'),
            'telephone': getattr(user, 'telephone', None),
            'pays': str(user.pays) if user.pays else None,
            'date_inscription': user.date_joined.isoformat() if user.date_joined else None,
            'derniere_connexion': user.last_login.isoformat() if user.last_login else None,
            'is_active': user.is_active,
            'est_certifie': getattr(user, 'est_certifie', False),
        }
        
        # ✅ PROFIL EXPERT - Utiliser les vrais champs
        if user.role == 'EXPERT':
            try:
                profil = ProfilExpert.objects.get(utilisateur=user)
                
                # ✅ Récupérer les domaines sous forme de liste
                domaines_list = []
                if profil.domaines_competence:
                    domaines_list = [d.strip() for d in profil.domaines_competence.split(',') if d.strip()]
                
                user_data['profil'] = {
                    # ✅ Champs réels du modèle
                    'domaines_competence': domaines_list,
                    'domaines_competence_raw': profil.domaines_competence,
                    'autres_competences': getattr(profil, 'autres_competences', None),
                    'disponible': getattr(profil, 'disponible', False),
                    'date_creation': profil.date_creation.isoformat() if getattr(profil, 'date_creation', None) else None,
                    'date_mise_a_jour': profil.date_mise_a_jour.isoformat() if getattr(profil, 'date_mise_a_jour', None) else None,
                    # ✅ CV - Utiliser cv_fichier
                    'cv': None,
                    'cv_url': None,
                }
                
                # ✅ Vérifier si le CV existe
                if hasattr(profil, 'cv_fichier') and profil.cv_fichier:
                    try:
                        cv_url = profil.cv_fichier.url
                        user_data['profil']['cv'] = cv_url
                        user_data['profil']['cv_url'] = request.build_absolute_uri(cv_url) if request else cv_url
                        print(f"✅ CV trouvé pour expert {user.id}: {cv_url}")
                    except Exception as e:
                        print(f" Erreur accès CV: {e}")
                else:
                    print(f" Aucun CV pour l'expert {user.id}")
                
                # ✅ Profil complet ?
                user_data['profil']['profil_complet'] = bool(
                    profil.cv_fichier and profil.domaines_competence
                )
                
            except ProfilExpert.DoesNotExist:
                print(f" ProfilExpert n'existe pas pour l'utilisateur {user.id}")
                user_data['profil'] = None
                user_data['profil_message'] = 'Aucun profil expert renseigné'
            except Exception as e:
                print(f" Erreur récupération profil expert: {e}")
                import traceback
                traceback.print_exc()
                user_data['profil'] = None
                user_data['profil_message'] = f'Erreur chargement profil: {str(e)}'
        
        #  PROFIL BUREAU - Utiliser les vrais champs
        elif user.role == 'BUREAU':
            try:
                #  Utiliser related_name='bureau_etude'
                bureau = user.bureau_etude
                
                user_data['profil'] = {
                    #  Champs réels du modèle
                    'nom_structure': getattr(bureau, 'nom_structure', None),
                    'pays': str(bureau.pays) if getattr(bureau, 'pays', None) else None,
                    'adresse': getattr(bureau, 'adresse', None),
                    'domaine_activite': getattr(bureau, 'domaine_activite', None),
                    'email_contact': getattr(bureau, 'email_contact', None),
                    'telephone': getattr(bureau, 'telephone', None),
                    'site_web': getattr(bureau, 'site_web', None),
                    'date_creation': bureau.date_creation.isoformat() if getattr(bureau, 'date_creation', None) else None,
                    'date_mise_a_jour': bureau.date_mise_a_jour.isoformat() if getattr(bureau, 'date_mise_a_jour', None) else None,
                }
                
                # ✅ Profil complet ?
                user_data['profil']['profil_complet'] = bool(
                    bureau.nom_structure and bureau.email_contact and bureau.telephone
                )
                
            except BureauEtude.DoesNotExist:
                print(f"⚠️ BureauEtude n'existe pas pour l'utilisateur {user.id}")
                user_data['profil'] = None
                user_data['profil_message'] = 'Aucun profil bureau renseigné'
            except Exception as e:
                print(f"❌ Erreur récupération profil bureau: {e}")
                import traceback
                traceback.print_exc()
                user_data['profil'] = None
                user_data['profil_message'] = f'Erreur chargement profil: {str(e)}'
        
        # ✅ Compter les activités
        try:
            from .models import SuggestionOffre
            try:
                suggestions_recues = SuggestionOffre.objects.filter(expert=user).count()
                suggestions_consultees = SuggestionOffre.objects.filter(
                    expert=user, est_consulte_par_expert=True
                ).count()
            except Exception:
                try:
                    suggestions_recues = SuggestionOffre.objects.filter(expert_utilisateur=user).count()
                    suggestions_consultees = SuggestionOffre.objects.filter(
                        expert_utilisateur=user, est_consulte_par_expert=True
                    ).count()
                except Exception:
                    suggestions_recues = 0
                    suggestions_consultees = 0
            
            user_data['activites'] = {
                'suggestions_recues': suggestions_recues if user.role == 'EXPERT' else 0,
                'suggestions_consultees': suggestions_consultees if user.role == 'EXPERT' else 0,
            }
        except Exception as e:
            print(f"❌ Erreur comptage activités: {e}")
            user_data['activites'] = {
                'suggestions_recues': 0,
                'suggestions_consultees': 0,
            }
        
        # ✅ DEBUG : Afficher les données avant envoi
        print(f"\n📤 Données envoyées pour user {user_id} ({user.role}):")
        if user_data.get('profil'):
            print(f"  - Profil complet: {user_data['profil'].get('profil_complet', False)}")
            if user.role == 'EXPERT':
                print(f"  - Domaines: {user_data['profil'].get('domaines_competence', [])}")
                print(f"  - CV URL: {user_data['profil'].get('cv_url', 'Aucun')}")
            elif user.role == 'BUREAU':
                print(f"  - Structure: {user_data['profil'].get('nom_structure', 'N/A')}")
                print(f"  - Email contact: {user_data['profil'].get('email_contact', 'N/A')}")
        else:
            print(f"  - Profil: {user_data.get('profil_message', 'Aucun')}")
        print()
        
        return Response(user_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        print(f"❌ ERREUR CRITIQUE admin_user_details: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': f'Erreur lors de la récupération des détails: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_list_experts_with_profiles(request):
    """
    Liste tous les experts avec leurs profils (ID du profil, pas de l'utilisateur)
    """
    try:
        # Récupérer tous les profils experts
        profils = ProfilExpert.objects.select_related('utilisateur').all()
        
        experts_data = []
        for profil in profils:
            experts_data.append({
                'id': profil.id,  # ✅ ID du ProfilExpert (ce que le backend attend)
                'user_id': profil.utilisateur.id,
                'nom': f"{profil.utilisateur.first_name} {profil.utilisateur.last_name}".strip() or profil.utilisateur.email,
                'email': profil.utilisateur.email,
                'specialite': profil.domaines_competence,
                'disponible': profil.disponible,
                'profil_complet': profil.profil_complet()
            })
        
        return Response(experts_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        print(f"❌ Erreur admin_list_experts_with_profiles: {e}")
        return Response(
            {'error': f'Erreur: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
 


class SuggestionExpertViewSet(viewsets.ViewSet):
    """
    API pour que l'expert puisse voir et répondre aux suggestions
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Liste toutes les suggestions de l'expert connecté"""
        try:
            # Récupérer le profil expert de l'utilisateur connecté
            profil_expert = ProfilExpert.objects.get(utilisateur=request.user)
            
            # Récupérer toutes les suggestions
            suggestions = SuggestionOffre.objects.filter(
                expert=profil_expert
            ).select_related('offre').order_by('-date_suggestion')
            
            # Filtrer par statut si demandé
            statut = request.query_params.get('statut')
            if statut:
                suggestions = suggestions.filter(statut_reponse=statut)
            
            serializer = SuggestionOffreExpertSerializer(suggestions, many=True)
            
            # Statistiques
            stats = {
                'total': suggestions.count(),
                'en_attente': suggestions.filter(statut_reponse='EN_ATTENTE').count(),
                'consultees': suggestions.filter(statut_reponse='CONSULTEE').count(),
                'acceptees': suggestions.filter(statut_reponse='ACCEPTEE').count(),
                'refusees': suggestions.filter(statut_reponse='REFUSEE').count(),
            }
            
            return Response({
                'suggestions': serializer.data,
                'stats': stats
            })
            
        except ProfilExpert.DoesNotExist:
            return Response(
                {'error': 'Profil expert non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"❌ Erreur list suggestions: {e}")
            return Response(
                {'error': f'Erreur serveur: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, pk=None):
        """Détails d'une suggestion spécifique"""
        try:
            profil_expert = ProfilExpert.objects.get(utilisateur=request.user)
            suggestion = SuggestionOffre.objects.get(
                id=pk, 
                expert=profil_expert
            )
            
            serializer = SuggestionOffreExpertSerializer(suggestion)
            return Response(serializer.data)
            
        except SuggestionOffre.DoesNotExist:
            return Response(
                {'error': 'Suggestion non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ProfilExpert.DoesNotExist:
            return Response(
                {'error': 'Profil expert non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], url_path='repondre')
    def repondre(self, request, pk=None):
        """
        Permet à l'expert de répondre à une suggestion
        Statuts possibles : CONSULTEE, ACCEPTEE, REFUSEE
        """
        try:
            profil_expert = ProfilExpert.objects.get(utilisateur=request.user)
            suggestion = SuggestionOffre.objects.get(
                id=pk, 
                expert=profil_expert
            )
            
            # Valider les données
            serializer = ReponseSuggestionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Mettre à jour la suggestion
            suggestion.statut_reponse = serializer.validated_data['statut_reponse']
            suggestion.date_reponse = timezone.now()
            suggestion.commentaire_expert = serializer.validated_data.get('commentaire_expert', '')
            
            # Mettre à jour l'ancien champ pour compatibilité
            if serializer.validated_data['statut_reponse'] == 'CONSULTEE':
                suggestion.est_consulte_par_expert = True
            
            suggestion.save()
            
            # Créer une notification pour l'admin
            try:
                admin = Utilisateur.objects.filter(is_staff=True).first()
                if admin:
                    Notification.objects.create(
                        destinataire=admin,
                        offre_liee=suggestion.offre,
                        objet=f"Expert a répondu à la suggestion",
                        message=f"L'expert {profil_expert.utilisateur.email} a {suggestion.get_statut_reponse_display().lower()} la suggestion pour l'offre: {suggestion.offre.titre[:50]}"
                    )
            except Exception as e:
                print(f"⚠️ Erreur notification: {e}")
            
            return Response({
                'message': f'Suggestion {suggestion.get_statut_reponse_display().lower()} avec succès',
                'suggestion': SuggestionOffreExpertSerializer(suggestion).data
            })
            
        except SuggestionOffre.DoesNotExist:
            return Response(
                {'error': 'Suggestion non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ProfilExpert.DoesNotExist:
            return Response(
                {'error': 'Profil expert non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"❌ Erreur repondre: {e}")
            return Response(
                {'error': f'Erreur serveur: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='marquer-consultee')
    def marquer_consultee(self, request, pk=None):
        """Marquer rapidement une suggestion comme consultée"""
        try:
            profil_expert = ProfilExpert.objects.get(utilisateur=request.user)
            suggestion = SuggestionOffre.objects.get(
                id=pk, 
                expert=profil_expert
            )
            
            suggestion.est_consulte_par_expert = True
            if suggestion.statut_reponse == 'EN_ATTENTE':
                suggestion.statut_reponse = 'CONSULTEE'
                suggestion.date_reponse = timezone.now()
            
            suggestion.save()
            
            return Response({
                'message': 'Suggestion marquée comme consultée',
                'suggestion': SuggestionOffreExpertSerializer(suggestion).data
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        


class NotificationUserViewSet(viewsets.ModelViewSet):
    """Gestion des notifications utilisateur"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(destinataire=self.request.user).order_by('-date_envoi')

    @action(detail=True, methods=['post'], url_path='marquer-lue')
    def marquer_lue(self, request, pk=None):
        notification = self.get_object()
        if notification.destinataire == request.user:
            notification.est_lue = True
            notification.save()
            return Response({'status': 'Notification marquée comme lue'})
        return Response({'error': 'Vous ne pouvez pas modifier cette notification'}, status=403)

    # : Supprimer une notification
    @action(detail=True, methods=['delete'], url_path='supprimer')
    def supprimer(self, request, pk=None):
        """Supprimer une notification spécifique"""
        try:
            notification = self.get_object()
            if notification.destinataire != request.user:
                return Response(
                    {'error': 'Vous ne pouvez pas supprimer cette notification'}, 
                    status=403
                )
            
            notification.delete()
            return Response({'status': 'Notification supprimée'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    # : Tout supprimer
    @action(detail=False, methods=['delete'], url_path='tout-supprimer')
    def tout_supprimer(self, request):
        """Supprimer toutes les notifications de l'utilisateur"""
        try:
            count, _ = Notification.objects.filter(destinataire=request.user).delete()
            return Response({
                'status': f'{count} notification(s) supprimée(s)',
                'count': count
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)



class ExpertMatchingView(APIView):
    """
    API pour trouver les offres correspondant aux critères d'un expert
    URL: GET /api/experts/matching/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            # Récupérer le profil expert de l'utilisateur
            profil = ProfilExpert.objects.get(utilisateur=request.user)
            
            # Trouver les offres correspondantes
            offres_match = trouver_offres_pour_expert(profil)
            
            # Sérialiser les résultats
            resultats = []
            for match in offres_match[:20]:  # Limiter à 20
                offre = match['offre']
                resultats.append({
                    'offre_id': offre.id,
                    'titre': offre.titre,
                    'organisme': offre.organisme,
                    'pays': offre.pays,
                    'domaine_detecte': match['domaine_detecte'],
                    'date_cloture': offre.date_cloture,
                    'match_direct': match['match_direct'],
                    'match_keywords': match['match_keywords'],
                })
            
            return Response({
                'success': True,
                'total': len(resultats),
                'domaines_expert': profil.domaines_competence,
                'offres': resultats
            })
            
        except ProfilExpert.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Profil expert non trouvé'
            }, status=404)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=500)


class ExpertTriggerNotificationView(APIView):
    """
    API pour déclencher manuellement les notifications
    URL: POST /api/experts/trigger-notifications/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            profil = ProfilExpert.objects.get(utilisateur=request.user)
            count = notifier_expert_nouvelles_offres(profil)
            
            return Response({
                'success': True,
                'notifications_creees': count,
                'message': f'{count} notification(s) créée(s)'
            })
            
        except ProfilExpert.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Profil expert non trouvé'
            }, status=404)


class DetectDomainesView(APIView):
    """
    API pour détecter les domaines dans un texte
    URL: POST /api/detect-domaines/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        texte = request.data.get('texte', '')
        if not texte:
            return Response({
                'success': False,
                'error': 'Texte requis'
            }, status=400)
        
        domaines = detecter_domaines_from_texte(texte)
        
        return Response({
            'success': True,
            'domaines_detectes': domaines,
            'total': len(domaines)
        })


class ListeDomainesView(APIView):
    """
    API pour lister tous les domaines disponibles
    URL: GET /api/domaines/
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        domaines_list = []
        for domaine, keywords in DOMAINES_KEYWORDS.items():
            domaines_list.append({
                'nom': domaine,
                'nb_mots_cles': len(keywords),
                'mots_cles': keywords[:10],  # Afficher les 10 premiers
            })
        
        return Response({
            'success': True,
            'total': len(domaines_list),
            'domaines': domaines_list
        })





@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """
    Étape 1 : Demande de réinitialisation par email
    POST /password-reset/
    Body: { "email": "user@example.com" }
    """
    email = request.data.get('email', '').strip().lower()
    
    if not email:
        return Response({'error': 'Email requis'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = Utilisateur.objects.get(email=email)
        
        # Invalider les anciens tokens
        PasswordResetToken.objects.filter(user=user, used=False).update(used=True)
        
        # Créer un nouveau token (valide 1 heure)
        reset_token = PasswordResetToken.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        # ✅ URL DU FRONTEND - Utilise FRONTEND_URL de settings.py
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        reset_link = f"{frontend_url}/reset-password?token={reset_token.token}"
        
        # ✅ Envoi de l'email
        try:
            from django.core.mail import send_mail
            
            subject = "Réinitialisation de votre mot de passe - Expertise-ID"
            message = f"""Bonjour {user.first_name or user.email},

Vous avez demandé une réinitialisation de votre mot de passe.

Cliquez sur le lien ci-dessous pour définir un nouveau mot de passe :

{reset_link}

Ce lien expirera dans 1 heure.

Si vous n'avez pas fait cette demande, ignorez cet email.

Cordialement,
L'équipe Expertise-ID
"""
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            print(f"✅ Email envoyé à {user.email} avec le lien: {reset_link}")
            
        except Exception as email_error:
            print(f" Erreur envoi email: {email_error}")
            return Response({'error': 'Erreur lors de l\'envoi de l\'email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'message': 'Si cet email est associé à un compte, vous recevrez un lien de réinitialisation.'
        }, status=status.HTTP_200_OK)
        
    except Utilisateur.DoesNotExist:
        # Sécurité : ne pas révéler si l'email existe
        return Response({
            'message': 'Si cet email est associé à un compte, vous recevrez un lien de réinitialisation.'
        }, status=status.HTTP_200_OK)