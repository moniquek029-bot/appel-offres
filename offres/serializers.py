# offres/serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

from django.contrib.auth.models import User

from django.contrib.auth.password_validation import validate_password
from .models import (
    SourceScraping, Utilisateur, AppelOffre, ProfilExpert, BureauEtude, 
    CritereRecherche, InscriptionNewsletter, Notification, Message, HistoriqueConnexion, SuggestionOffre
)

User = get_user_model()


# =============================================================================
# AUTHENTIFICATION
# =============================================================================

# offres/serializers.py - Modifier RegisterSerializer

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    adresse = serializers.CharField(required=False, allow_blank=True)
    date_naissance = serializers.DateField(required=False, allow_null=True)
    genre = serializers.CharField(required=False, allow_blank=True, max_length=1)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password_confirm', 
                  'role', 'telephone', 'pays', 'adresse', 'date_naissance', 'genre')
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
        adresse = validated_data.pop('adresse', '')
        date_naissance = validated_data.pop('date_naissance', None)
        genre = validated_data.pop('genre', '')
        
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=validated_data.get('role', 'EXPERT'),
            telephone=validated_data.get('telephone', ''),
            pays=validated_data.get('pays', 'BF'),
            adresse=adresse,
            date_naissance=date_naissance,
            genre=genre
        )
        
        # ✅ CORRECTION : Vérifier si le profil existe déjà avant de le créer
        if user.role == 'EXPERT':
            ProfilExpert.objects.get_or_create(utilisateur=user)
        elif user.role == 'BUREAU':
            BureauEtude.objects.get_or_create(gestionnaire=user)
        
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Login personnalisé avec infos utilisateur"""
    
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
        
        pays_value = getattr(user, 'pays', None)
        pays_str = str(pays_value) if pays_value else ''
        telephone = getattr(user, 'telephone', '') or ''
        
        user_data = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
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
        elif user.role == 'BUREAU' and hasattr(user, 'bureau_etude'):
            try:
                user_data['profil'] = BureauEtudeSerializer(user.bureau_etude).data
            except Exception:
                user_data['profil'] = None
        
        data.update({'user': user_data})
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer utilisateur avec accès sécurisé aux profils"""
    nom = serializers.SerializerMethodField()
    profil = serializers.SerializerMethodField()
    pays_str = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'nom', 'role', 
                  'telephone', 'pays', 'pays_str', 'date_naissance', 'genre',
                  'adresse', 'date_joined', 'profil')
        read_only_fields = ('id', 'date_joined')
    
    def get_nom(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
    
    def get_pays_str(self, obj):
        pays = getattr(obj, 'pays', None)
        return str(pays) if pays else ''
    
    def get_profil(self, obj):
        if obj.role == 'EXPERT' and hasattr(obj, 'profil_expert'):
            try:
                return ProfilExpertSerializer(obj.profil_expert).data
            except Exception:
                return None
        elif obj.role == 'BUREAU' and hasattr(obj, 'bureau_etude'):
            try:
                return BureauEtudeSerializer(obj.bureau_etude).data
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
# APPELS D'OFFRES

class AppelOffreSerializer(serializers.ModelSerializer):
    """
    Serializer pour AppelOffre
    """
    fichier_pdf_url = serializers.SerializerMethodField()
    
    class Meta:
        model = AppelOffre
        fields = [
            'id', 'titre', 'organisme', 'description', 'pays',
            'date_publication', 'date_cloture', 'url_source',
            'url_tdr', 'fichier_pdf', 'fichier_pdf_url',
            'statut', 'mode_acquisition', 'source_origine',
            'date_scraping', 'est_expire',
            'domaine', 'type_offre',
        ]
        read_only_fields = ['date_scraping', 'est_expire']
    
    def get_fichier_pdf_url(self, obj):
        """Retourne l'URL absolue du fichier PDF uploadé"""
        if obj.fichier_pdf:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.fichier_pdf.url)
            return obj.fichier_pdf.url
        return None
    
    def validate_fichier_pdf(self, value):
        """Validation du fichier PDF"""
        if value:
            # Vérifier l'extension
            if not value.name.lower().endswith('.pdf'):
                raise serializers.ValidationError(
                    "Seuls les fichiers PDF sont acceptés. Extension trouvée: " + value.name.split('.')[-1]
                )
            
            # Vérifier la taille (max 10 MB)
            max_size = 10 * 1024 * 1024  # 10 MB
            if value.size > max_size:
                size_mb = value.size / (1024 * 1024)
                raise serializers.ValidationError(
                    f"Le fichier ne doit pas dépasser 10 MB. Taille actuelle: {size_mb:.2f} MB"
                )
        
        return value
    
    def validate(self, data):
        """Validation globale"""
        # Au moins une source de PDF doit être fournie (optionnel mais recommandé)
        # On ne force pas, car certaines offres peuvent ne pas avoir de PDF
        
        # Vérifier que date_cloture est après date_publication
        if data.get('date_publication') and data.get('date_cloture'):
            if data['date_cloture'] < data['date_publication']:
                raise serializers.ValidationError({
                    'date_cloture': "La date de clôture doit être après la date de publication"
                })
        
        return data
# =============================================================================
# PROFIL EXPERT (avec domaines de compétence et CV)
# =============================================================================

class ProfilExpertSerializer(serializers.ModelSerializer):
    """Serializer complet pour le profil Expert"""
    
    # Informations utilisateur (lecture seule)
    email = serializers.EmailField(source='utilisateur.email', read_only=True)
    first_name = serializers.CharField(source='utilisateur.first_name', read_only=True)
    last_name = serializers.CharField(source='utilisateur.last_name', read_only=True)
    date_naissance = serializers.DateField(source='utilisateur.date_naissance', read_only=True)
    genre = serializers.CharField(source='utilisateur.genre', read_only=True)
    telephone = serializers.CharField(source='utilisateur.telephone', read_only=True)
    adresse = serializers.CharField(source='utilisateur.adresse', read_only=True)
    
    complet_pourcentage = serializers.SerializerMethodField()
    
    class Meta:
        model = ProfilExpert
        fields = [
            'id',
            # Informations utilisateur
            'email', 'first_name', 'last_name', 'date_naissance', 'genre',
            'telephone', 'adresse',
            # Profil expert
            'domaines_competence', 'autres_competences',
            'cv_fichier', 'disponible',
            'date_creation', 'date_mise_a_jour',
            'complet_pourcentage'
        ]
        read_only_fields = ['id', 'date_creation', 'date_mise_a_jour', 'email', 
                           'first_name', 'last_name', 'date_naissance', 'genre',
                           'telephone', 'adresse']
        extra_kwargs = {'cv_fichier': {'required': False}}
    
    def get_complet_pourcentage(self, obj):
        total = 0
        filled = 0
        
        # CV (obligatoire)
        total += 40
        if obj.cv_fichier:
            filled += 40
        
        # Domaines de compétence (obligatoire)
        total += 40
        if obj.domaines_competence:
            filled += 40
        
        # Disponibilité
        total += 20
        if obj.disponible is not None:
            filled += 20
        
        return int((filled / total) * 100) if total > 0 else 0
    
    def validate_cv_fichier(self, value):
        """Validation du fichier CV"""
        if value:
            import os
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in ['.pdf', '.doc', '.docx']:
                raise serializers.ValidationError("Format de fichier non supporté. Utilisez PDF, DOC ou DOCX.")
        return value


# =============================================================================
# PROFIL BUREAU (nom, pays, adresse, domaine, email, numéro - pas de CV)
# =============================================================================

class BureauEtudeSerializer(serializers.ModelSerializer):
    """Serializer complet pour le profil Bureau d'Étude"""
    
    # Informations du gestionnaire
    email_gestionnaire = serializers.EmailField(source='gestionnaire.email', read_only=True)
    nom_gestionnaire = serializers.SerializerMethodField()
    
    complet_pourcentage = serializers.SerializerMethodField()
    
    class Meta:
        model = BureauEtude
        fields = [
            'id',
            # Gestionnaire
            'email_gestionnaire', 'nom_gestionnaire',
            # Structure
            'nom_structure', 'pays', 'adresse', 'domaine_activite',
            'email_contact', 'telephone', 'site_web',
            'date_creation', 'date_mise_a_jour',
            'complet_pourcentage'
        ]
        read_only_fields = ['id', 'date_creation', 'date_mise_a_jour', 
                           'email_gestionnaire', 'nom_gestionnaire']
    
    def get_nom_gestionnaire(self, obj):
        user = obj.gestionnaire
        return f"{user.first_name} {user.last_name}".strip()
    
    def get_complet_pourcentage(self, obj):
        total = 0
        filled = 0
        
        # Nom de la structure
        total += 20
        if obj.nom_structure:
            filled += 20
        
        # Email de contact
        total += 20
        if obj.email_contact:
            filled += 20
        
        # Téléphone
        total += 20
        if obj.telephone:
            filled += 20
        
        # Adresse
        total += 20
        if obj.adresse:
            filled += 20
        
        # Domaine d'activité
        total += 20
        if obj.domaine_activite:
            filled += 20
        
        return int((filled / total) * 100) if total > 0 else 0


# =============================================================================
# CRITÈRES & NEWSLETTER
# =============================================================================

class CritereRechercheSerializer(serializers.ModelSerializer):
    mots_cles_list = serializers.SerializerMethodField()
    
    class Meta:
        model = CritereRecherche
        fields = '__all__'
        read_only_fields = ('id', 'utilisateur', 'last_notified')
    
    def get_mots_cles_list(self, obj):
        return obj.get_mots_cles_list()


class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InscriptionNewsletter
        fields = '__all__'


# offres/serializers.py

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'destinataire', 'offre_liee', 'objet', 'message', 'date_envoi', 'est_lue']
        read_only_fields = ['destinataire', 'date_envoi']



# Ajoutez ce serializer pour les utilisateurs
class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'nom', 'first_name', 'last_name', 'username']

class MessageSerializer(serializers.ModelSerializer):
    expediteur_nom = serializers.SerializerMethodField()
    destinataire_nom = serializers.SerializerMethodField()
    expediteur_email = serializers.SerializerMethodField()
    destinataire_email = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ('id', 'date_envoi', 'est_lu', 'expediteur')
    
    def get_expediteur_nom(self, obj):
        if obj.expediteur:  # ← AJOUTER CE TEST
            nom = f"{obj.expediteur.first_name} {obj.expediteur.last_name}".strip()
            return nom if nom else obj.expediteur.email
        return "Système"  # Valeur par défaut
    
    def get_destinataire_nom(self, obj):
        if obj.destinataire:  # ← AJOUTER CE TEST
            nom = f"{obj.destinataire.first_name} {obj.destinataire.last_name}".strip()
            return nom if nom else obj.destinataire.email
        return "Système"  # Valeur par défaut
    
    def get_expediteur_email(self, obj):
        return obj.expediteur.email if obj.expediteur else None  # ← AJOUTER CE TEST
    
    def get_destinataire_email(self, obj):
        return obj.destinataire.email if obj.destinataire else None  # ← AJOUTER CE TEST
# offres/serializers.py - Ajouter ces serializers à la fin du fichier

# =============================================================================
# ADMIN - SERIALIZERS
# =============================================================================

class HistoriqueConnexionSerializer(serializers.ModelSerializer):
    """Serializer pour l'historique des connexions"""
    utilisateur_email = serializers.EmailField(source='utilisateur.email', read_only=True)
    utilisateur_nom = serializers.SerializerMethodField()
    utilisateur_role = serializers.CharField(source='utilisateur.role', read_only=True)
    
    class Meta:
        model = HistoriqueConnexion
        fields = [
            'id', 'utilisateur', 'utilisateur_email', 'utilisateur_nom', 
            'utilisateur_role', 'date_connexion', 'ip_address', 'user_agent'
        ]
        read_only_fields = ('id', 'date_connexion')
    
    def get_utilisateur_nom(self, obj):
        return f"{obj.utilisateur.first_name} {obj.utilisateur.last_name}".strip() or obj.utilisateur.email


class SuggestionOffreSerializer(serializers.ModelSerializer):
    """Serializer pour les suggestions d'experts"""
    expert_nom = serializers.SerializerMethodField()
    expert_email = serializers.EmailField(source='expert.utilisateur.email', read_only=True)
    expert_telephone = serializers.CharField(source='expert.utilisateur.telephone', read_only=True)
    offre_titre = serializers.CharField(source='offre.titre', read_only=True)
    offre_organisme = serializers.CharField(source='offre.organisme', read_only=True)
    offre_date_cloture = serializers.DateField(source='offre.date_cloture', read_only=True)
    
    class Meta:
        model = SuggestionOffre
        fields = [
            'id', 'expert', 'expert_nom', 'expert_email', 'expert_telephone',
            'offre', 'offre_titre', 'offre_organisme', 'offre_date_cloture',
            'date_suggestion', 'commentaire_admin', 'est_consulte_par_expert'
        ]
        read_only_fields = ('id', 'date_suggestion')
    
    def get_expert_nom(self, obj):
        return f"{obj.expert.utilisateur.first_name} {obj.expert.utilisateur.last_name}".strip() or obj.expert.utilisateur.email


class AdminUserDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour l'admin (avec plus d'informations)"""
    profil_expert = serializers.SerializerMethodField()
    bureau_etude = serializers.SerializerMethodField()
    dernieres_connexions = serializers.SerializerMethodField()
    nombre_connexions = serializers.SerializerMethodField()
    
    class Meta:
        model = Utilisateur
        fields = [
            'id', 'email', 'first_name', 'last_name', 'role', 'telephone', 
            'pays', 'adresse', 'date_naissance', 'genre', 'is_active', 
            'is_staff', 'date_joined', 'last_login', 'profil_expert', 
            'bureau_etude', 'dernieres_connexions', 'nombre_connexions'
        ]
        read_only_fields = ('id', 'date_joined', 'last_login')
    
    def get_profil_expert(self, obj):
        if obj.role == 'EXPERT' and hasattr(obj, 'profil_expert'):
            try:
                return {
                    'id': obj.profil_expert.id,
                    'domaines_competence': obj.profil_expert.domaines_competence,
                    'cv_fichier': obj.profil_expert.cv_fichier.url if obj.profil_expert.cv_fichier else None,
                    'disponible': obj.profil_expert.disponible,
                    'date_creation': obj.profil_expert.date_creation
                }
            except:
                return None
        return None
    
    def get_bureau_etude(self, obj):
        if obj.role == 'BUREAU' and hasattr(obj, 'bureau_etude'):
            try:
                return {
                    'id': obj.bureau_etude.id,
                    'nom_structure': obj.bureau_etude.nom_structure,
                    'domaine_activite': obj.bureau_etude.domaine_activite,
                    'email_contact': obj.bureau_etude.email_contact,
                    'telephone': obj.bureau_etude.telephone,
                    'adresse': obj.bureau_etude.adresse
                }
            except:
                return None
        return None
    
    def get_dernieres_connexions(self, obj):
        from .models import HistoriqueConnexion
        dernieres = HistoriqueConnexion.objects.filter(utilisateur=obj).order_by('-date_connexion')[:5]
        return [
            {
                'date': conn.date_connexion,
                'ip': conn.ip_address
            } for conn in dernieres
        ]
    
    def get_nombre_connexions(self, obj):
        from .models import HistoriqueConnexion
        return HistoriqueConnexion.objects.filter(utilisateur=obj).count()


class AdminStatistiquesSerializer(serializers.Serializer):
    """Serializer pour les statistiques de l'admin dashboard"""
    total_offres = serializers.IntegerField()
    offres_scrapees = serializers.IntegerField()
    offres_manuelles = serializers.IntegerField()
    offres_actives = serializers.IntegerField()
    total_utilisateurs = serializers.IntegerField()
    experts = serializers.IntegerField()
    bureaux = serializers.IntegerField()
    admins = serializers.IntegerField()
    nouveaux_utilisateurs_30j = serializers.IntegerField()
    connexions_aujourdhui = serializers.IntegerField()
    connexions_semaine = serializers.IntegerField()
    messages_non_lus = serializers.IntegerField()
    messages_totaux = serializers.IntegerField()
    suggestions_envoyees = serializers.IntegerField()
    suggestions_consultees = serializers.IntegerField()


# offres/serializers.py

class SourceScrapingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceScraping
        fields = ['id', 'nom', 'url_racine', 'frequence_maj', 'est_actif', 'last_scraped', 'created_at', 'updated_at']
        read_only_fields = ['last_scraped', 'created_at', 'updated_at']
    
    # ✅ Rendre frequence_maj optionnel avec valeur par défaut
    frequence_maj = serializers.CharField(required=False, default='Toutes les 24h')
    
    # ✅ Rendre est_actif optionnel avec valeur par défaut
    est_actif = serializers.BooleanField(required=False, default=True)
    
    def validate_url_racine(self, value):
        """Valide et normalise l'URL"""
        if not value:
            raise serializers.ValidationError("L'URL est requise")
        
        # Ajouter https:// si manquant
        if not value.startswith(('http://', 'https://')):
            value = 'https://' + value
        
        return value.strip()
    
    def validate_nom(self, value):
        """Valide que le nom n'est pas vide"""
        if not value or len(str(value).strip()) == 0:
            raise serializers.ValidationError("Le nom ne peut pas être vide")
        return str(value).strip()
    



# offres/serializers.py (ajouter à la fin)

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas")
        return data
    

class SuggestionOffreExpertSerializer(serializers.ModelSerializer):
    """Serializer pour les suggestions vues par l'expert"""
    offre_titre = serializers.CharField(source='offre.titre', read_only=True)
    offre_organisme = serializers.CharField(source='offre.organisme', read_only=True)
    offre_date_cloture = serializers.DateField(source='offre.date_cloture', read_only=True)
    offre_pays = serializers.CharField(source='offre.pays', read_only=True)
    offre_description = serializers.CharField(source='offre.description', read_only=True)
    offre_url_source = serializers.URLField(source='offre.url_source', read_only=True)
    
    class Meta:
        model = SuggestionOffre
        fields = [
            'id', 
            'offre', 'offre_titre', 'offre_organisme', 
            'offre_date_cloture', 'offre_pays', 'offre_description', 'offre_url_source',
            'date_suggestion', 
            'commentaire_admin',
            'statut_reponse', 
            'date_reponse',
            'commentaire_expert',
            'est_consulte_par_expert'
        ]
        read_only_fields = ['id', 'offre', 'date_suggestion', 'commentaire_admin']


class ReponseSuggestionSerializer(serializers.Serializer):
    """Serializer pour la réponse de l'expert"""
    statut_reponse = serializers.ChoiceField(
        choices=['CONSULTEE', 'ACCEPTEE', 'REFUSEE']
    )
    commentaire_expert = serializers.CharField(
        required=False, 
        allow_blank=True,
        max_length=500
    )