# offres/serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import (
    Utilisateur, AppelOffre, ProfilExpert, BureauEtude, 
    CritereRecherche, InscriptionNewsletter, Notification
)

User = get_user_model()


# =============================================================================
# AUTHENTIFICATION
# =============================================================================

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer d'inscription avec validation des mots de passe"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password_confirm', 'role', 'telephone', 'pays')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=validated_data.get('role', 'EXPERT'),
            telephone=validated_data.get('telephone', ''),
            pays=validated_data.get('pays', 'BF')
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Login personnalisé avec infos utilisateur + gestion sécurisée des champs spéciaux"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        
        # ✅ Conversion sécurisée : CountryField → string
        pays_value = getattr(user, 'pays', None)
        pays_str = str(pays_value) if pays_value else ''
        telephone = getattr(user, 'telephone', '') or ''
        
        user_data = {
            'id': user.id,
            'email': user.email,
            'nom': f"{user.first_name} {user.last_name}".strip(),
            'role': user.role,
            'telephone': telephone,
            'pays': pays_str,
        }
        
        # Ajout du profil lié si disponible
        if user.role == 'EXPERT' and hasattr(user, 'profil_expert'):
            try:
                user_data['profil'] = ProfilExpertSerializer(user.profil_expert).data
            except Exception:
                user_data['profil'] = None
        elif user.role in ['BUREAU', 'BUREAU_ETUDE'] and hasattr(user, 'bureauetude'):
            try:
                user_data['profil'] = BureauEtudeSerializer(user.bureauetude).data
            except Exception:
                user_data['profil'] = None
        
        data.update({'user': user_data})
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer utilisateur avec accès sécurisé aux profils"""
    nom = serializers.SerializerMethodField()
    profil = serializers.SerializerMethodField()
    pays = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'nom', 'role', 
                  'telephone', 'pays', 'date_joined', 'profil')
        read_only_fields = ('id', 'date_joined')
    
    def get_nom(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
    
    def get_pays(self, obj):
        """Convertit CountryField en string JSON-safe"""
        pays = getattr(obj, 'pays', None)
        return str(pays) if pays else ''
    
    def get_profil(self, obj):
        """Retourne le profil lié ou None de façon sécurisée"""
        if obj.role == 'EXPERT' and hasattr(obj, 'profil_expert'):
            try:
                return ProfilExpertSerializer(obj.profil_expert).data
            except Exception:
                return None
        elif obj.role in ['BUREAU', 'BUREAU_ETUDE'] and hasattr(obj, 'bureauetude'):
            try:
                return BureauEtudeSerializer(obj.bureauetude).data
            except Exception:
                return None
        return None


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer pour changer le mot de passe"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Les nouveaux mots de passe ne correspondent pas."})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Mot de passe actuel incorrect.")
        return value


# =============================================================================
# APPELS D'OFFRES - ACCÈS DIFFÉRENCIÉ AUX URLs
# =============================================================================

class AppelOffreSerializer(serializers.ModelSerializer):
    source_nom = serializers.ReadOnlyField(source='source_origine.nom')
    jours_restants = serializers.SerializerMethodField()
    
    # ✅ url_source : toujours visible
    url_source = serializers.URLField(read_only=True)
    
    # ✅ url_tdr : masquée pour les visiteurs non authentifiés
    url_tdr = serializers.SerializerMethodField()

    class Meta:
        model = AppelOffre
        fields = (
            'id', 'titre', 'organisme', 'description', 'pays', 
            'date_publication', 'date_cloture', 
            'url_source', 'url_tdr',  # ✅ Les deux URLs
            'source_nom', 'jours_restants', 'statut', 'mode_acquisition'
        )
        read_only_fields = ('id', 'mode_acquisition')

    def get_url_tdr(self, obj):
        """Retourne l'URL TDR uniquement si l'utilisateur est authentifié"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.url_tdr
        return None

    def get_jours_restants(self, obj):
        from django.utils import timezone
        if obj.date_cloture:
            delta = obj.date_cloture - timezone.now().date()
            return max(0, delta.days)
        return None


# =============================================================================
# PROFIL EXPERT - CHAMPS VALIDES UNIQUEMENT
# =============================================================================

class ProfilExpertSerializer(serializers.ModelSerializer):
    # ✅ Champs délégués à l'utilisateur (lecture seule)
    telephone = serializers.SerializerMethodField()
    pays = serializers.SerializerMethodField()
    
    class Meta:
        model = ProfilExpert
        fields = [
            'id', 'utilisateur', 
            'cv_fichier', 
            'competences', 
            'experience', 
            'disponibilite', 
            'alerte_active',
            'date_creation',
            # Champs délégués (lecture seule)
            'telephone', 'pays'
        ]
        read_only_fields = ['id', 'utilisateur', 'date_creation', 'telephone', 'pays']
        extra_kwargs = {'cv_fichier': {'required': False}}
    
    def get_telephone(self, obj):
        user = getattr(obj, 'utilisateur', None)
        return getattr(user, 'telephone', '') if user else ''
    
    def get_pays(self, obj):
        user = getattr(obj, 'utilisateur', None)
        if user and hasattr(user, 'pays'):
            pays = user.pays
            return str(pays) if pays else ''
        return ''


# =============================================================================
# BUREAU D'ÉTUDE - PARALLÈLE À EXPERT
# =============================================================================

class BureauEtudeSerializer(serializers.ModelSerializer):
    telephone = serializers.SerializerMethodField()
    pays = serializers.SerializerMethodField()
    
    class Meta:
        model = BureauEtude
        fields = [
            'id', 'gestionnaire',
            'nom_structure',
            'cv_fichier',
            'date_creation',
            'telephone', 'pays'
        ]
        read_only_fields = ['id', 'gestionnaire', 'date_creation', 'telephone', 'pays']
        extra_kwargs = {'cv_fichier': {'required': False}}
    
    def get_telephone(self, obj):
        user = getattr(obj, 'gestionnaire', None)
        return getattr(user, 'telephone', '') if user else ''
    
    def get_pays(self, obj):
        user = getattr(obj, 'gestionnaire', None)
        if user and hasattr(user, 'pays'):
            pays = user.pays
            return str(pays) if pays else ''
        return ''


# =============================================================================
# CRITÈRES & NEWSLETTER
# =============================================================================

class CritereRechercheSerializer(serializers.ModelSerializer):
    class Meta:
        model = CritereRecherche
        fields = '__all__'
        read_only_fields = ('id', 'utilisateur')


class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InscriptionNewsletter
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('id', 'envoyee_le')