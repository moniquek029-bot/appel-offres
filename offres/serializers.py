"""
offres/serializers.py
Sérialiseurs avec gestion des rôles (Expert, Bureau, Visiteur) et accès différenciés.
"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import AppelOffre, Utilisateur, ProfilExpert, BureauEtude, CritereRecherche, InscriptionNewsletter


# =============================================================================
# 1. INSCRIPTION UTILISATEUR - RÔLE SÉLECTIONNABLE
# =============================================================================
class RegisterSerializer(serializers.ModelSerializer):
    """
    Inscription avec choix du rôle (Expert, Bureau, Visiteur).
    Le rôle détermine les étapes de complétion de profil obligatoires.
    """
    password = serializers.CharField(write_only=True, required=True, min_length=8, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, min_length=8, style={'input_type': 'password'})

    class Meta:
        model = Utilisateur
        fields = ('first_name', 'last_name', 'email', 'password', 'password_confirm', 'telephone', 'pays', 'role')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }

    def validate_role(self, value):
        """Valide que le rôle choisi est autorisé à l'inscription"""
        if value not in ['EXPERT', 'BUREAU', 'VISITEUR']:
            raise serializers.ValidationError("Rôle non autorisé. Choisissez parmi: EXPERT, BUREAU, VISITEUR.")
        return value

    def validate(self, attrs):
        """Validation globale des données d'inscription"""
        # Mots de passe correspondants
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Les mots de passe ne correspondent pas."})
        
        # Email unique
        if Utilisateur.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Cet email est déjà utilisé."})
        
        return attrs

    def create(self, validated_data):
        """Création de l'utilisateur avec le rôle choisi"""
        validated_data.pop('password_confirm')
        
        # Hachage automatique du mot de passe via le manager personnalisé
        user = Utilisateur.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
            telephone=validated_data.get('telephone', ''),
            pays=validated_data.get('pays', 'BF'),
            role=validated_data.get('role', 'VISITEUR')  # Rôle choisi par l'utilisateur
        )
        
        # Création automatique du profil lié au rôle
        if user.role == 'EXPERT':
            ProfilExpert.objects.create(utilisateur=user)
        elif user.role == 'BUREAU':
            BureauEtude.objects.create(gestionnaire=user)
        # VISITEUR n'a pas de profil supplémentaire obligatoire
        
        return user


# =============================================================================
# 2. CONNEXION JWT PERSONNALISÉE
# =============================================================================
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Ajoute le rôle et l'état de complétion du profil dans la réponse"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        token['is_profile_complete'] = cls._is_profile_complete(user)
        return token

    @staticmethod
    def _is_profile_complete(user):
        """Vérifie si le profil est complet selon le rôle"""
        if user.role == 'EXPERT':
            return hasattr(user, 'profil_expert') and user.profil_expert.cv_fichier
        elif user.role == 'BUREAU':
            return hasattr(user, 'bureauetude')
        return True  # Visiteur n'a pas de profil supplémentaire

    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            'user': {
                'id': self.user.id,
                'email': self.user.email,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'role': self.user.role,
                'is_profile_complete': self._is_profile_complete(self.user),
            },
            'message': f'Bonjour {self.user.first_name} ! Connexion réussie.',
            'redirect_to': self._get_redirect_url(self.user)
        })
        return data

    @staticmethod
    def _get_redirect_url(user):
        """Détermine la page de redirection après connexion selon le rôle"""
        if user.role == 'EXPERT' and not user.profil_expert.cv_fichier:
            return '/expert/complete-profile'  # Doit uploader son CV
        elif user.role == 'BUREAU' and not hasattr(user, 'bureauetude'):
            return '/bureau/complete-profile'  # Doit compléter les infos bureau
        elif user.role == 'EXPERT':
            return '/expert/dashboard'
        elif user.role == 'BUREAU':
            return '/bureau/dashboard'
        return '/dashboard'  # Visiteur ou profil complet


# =============================================================================
# 3. PROFIL UTILISATEUR
# =============================================================================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'telephone', 'pays', 'adresse', 'date_naissance', 'genre')
        read_only_fields = ('id', 'email', 'role')  # Le rôle ne peut être modifié après inscription


# =============================================================================
# 4. APPELS D'OFFRES - ACCÈS PUBLIC LIMITÉ
# =============================================================================
class AppelOffreSerializer(serializers.ModelSerializer):
    """
    Pour les visiteurs non authentifiés : affiche uniquement les métadonnées.
    Pour les utilisateurs authentifiés : affiche plus de détails.
    """
    jours_restants = serializers.SerializerMethodField()
    source_nom = serializers.ReadOnlyField(source='source_origine.nom')
    # Champ conditionnel : URL complète seulement pour authentifiés
    url_tdr = serializers.SerializerMethodField()

    class Meta:
        model = AppelOffre
        fields = ('id', 'titre', 'organisme', 'description', 'pays', 'date_publication', 
                  'date_cloture', 'url_tdr', 'source_nom', 'jours_restants', 'statut')
        read_only_fields = ('mode_acquisition', 'source_origine', 'date_publication')

    def get_jours_restants(self, obj):
        from django.utils import timezone
        delta = obj.date_cloture - timezone.now().date()
        return max(0, delta.days)

    def get_url_tdr(self, obj):
        """Masque l'URL officielle pour les visiteurs non authentifiés"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.url_tdr
        return None  # Visiteur non connecté : pas d'accès au lien direct


# =============================================================================
# 5. PROFIL EXPERT (complétion obligatoire)
# =============================================================================
class ProfilExpertSerializer(serializers.ModelSerializer):
    utilisateur = UserSerializer(read_only=True)
    
    class Meta:
        model = ProfilExpert
        fields = '__all__'
        read_only_fields = ('utilisateur', 'date_mise_a_jour')

    def validate_cv_fichier(self, value):
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("Seuls les fichiers PDF sont acceptés pour le CV.")
        if value.size > 5 * 1024 * 1024:  # 5 Mo max
            raise serializers.ValidationError("Le CV ne doit pas dépasser 5 Mo.")
        return value


# =============================================================================
# 6. PROFIL BUREAU D'ÉTUDE (complétion obligatoire)
# =============================================================================
class BureauEtudeSerializer(serializers.ModelSerializer):
    gestionnaire = UserSerializer(read_only=True)
    
    class Meta:
        model = BureauEtude
        fields = '__all__'
        read_only_fields = ('gestionnaire',)


# =============================================================================
# 7. CRITÈRES DE RECHERCHE & ALERTES (pour Experts)
# =============================================================================
class CritereRechercheSerializer(serializers.ModelSerializer):
    class Meta:
        model = CritereRecherche
        fields = '__all__'
        read_only_fields = ('utilisateur',)


# =============================================================================
# 8. NEWSLETTER - ACCÈS PUBLIC (VISITEURS NON CONNECTÉS)
# =============================================================================
class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    """Inscription à la newsletter sans créer de compte"""
    class Meta:
        model = InscriptionNewsletter
        fields = ('email',)
    
    def validate_email(self, value):
        if InscriptionNewsletter.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email est déjà inscrit à la newsletter.")
        return value


# =============================================================================
# 9. CHANGEMENT DE MOT DE PASSE
# =============================================================================
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True, write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Les mots de passe ne correspondent pas."})
        validate_password(attrs['new_password'], self.context['user'])
        if not self.context['user'].check_password(attrs['old_password']):
            raise serializers.ValidationError({"old_password": "Ancien mot de passe incorrect."})
        return attrs

    def save(self):
        self.context['user'].set_password(self.validated_data['new_password'])
        self.context['user'].save()
        return self.context['user']