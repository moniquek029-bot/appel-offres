# offres/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import EmailValidator
from django_countries.fields import CountryField
from django.contrib.auth.models import User
import secrets
from datetime import timedelta
from django.utils import timezone
from django.conf import settings  # ✅ AJOUTER CET IMPORT


# =============================================================================
# MODULE 1 : GESTION DES COMPTES ET AUTHENTIFICATION
# =============================================================================
# offres/models.py - Modifier UtilisateurManager

class UtilisateurManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, adresse='', 
                    date_naissance=None, genre='', **extra_fields):
        if not email:
            raise ValueError("L'adresse email est requise")
        email = self.normalize_email(email)
        user = self.model(
            email=email, 
            first_name=first_name, 
            last_name=last_name,
            adresse=adresse,
            date_naissance=date_naissance,
            genre=genre,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, first_name, last_name, password, **extra_fields)


class Utilisateur(AbstractUser):
    """
    Modèle personnalisé. L'email sert d'identifiant unique.
    """
    username = None  # Désactivation du username par défaut
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    
    CHOIX_ROLES = [
        ('ADMIN', 'Administrateur'),
        ('EXPERT', 'Expert'),
        ('BUREAU', 'Bureau d\'étude / Entreprise'),
    ]
    role = models.CharField(max_length=20, choices=CHOIX_ROLES, default='EXPERT')
    
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    pays = CountryField(default='BF', blank=True, verbose_name="Pays de résidence")
    adresse = models.CharField(max_length=255, blank=True, verbose_name="Adresse complète")
    date_naissance = models.DateField(null=True, blank=True)
    genre = models.CharField(max_length=1, choices=[('M', 'Masculin'), ('F', 'Féminin')], blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = UtilisateurManager()

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    class Meta:
        db_table = 'utilisateurs'
        verbose_name = "Utilisateur"


# =============================================================================
# MODULE 2 : VEILLE ET COLLECTE AUTOMATISÉE
# =============================================================================

# offres/models.py
class SourceScraping(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom du site source")
    url_racine = models.URLField(verbose_name="Lien de la page d'accueil")
    frequence_maj = models.CharField(max_length=50, help_text="Ex: Toutes les 12 heures")
    est_actif = models.BooleanField(default=True, help_text="Désactiver si le site change de structure")
    last_scraped = models.DateTimeField(null=True, blank=True, verbose_name="Dernier scraping")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    pays = models.CharField(max_length=10, default='BF', blank=True)
    
    # ✅ NOUVEAUX CHAMPS POUR L'ORCHESTRATEUR
    parser = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name="Type de parser",
        help_text="Laisser vide pour détection automatique. Options: undp, unfpa, agetib, sonabel, uemoa, joffres, smart"
    )
    
    use_js = models.BooleanField(
        default=False,
        verbose_name="Utiliser Selenium (JavaScript)",
        help_text="Activer si le site nécessite JavaScript pour afficher les offres"
    )
    
    delay = models.IntegerField(
        default=2,
        verbose_name="Délai entre requêtes (secondes)",
        help_text="Temps d'attente entre chaque page pour éviter le blocage"
    )
    
    class Meta:
        verbose_name = "Source de scraping"
        verbose_name_plural = "Sources de scraping"
        ordering = ['id']
    
    def __str__(self):
        return self.nom
    
    def get_url(self):
        """Retourne l'URL (compatibilité avec l'orchestrateur)"""
        return self.url_racine
    
    
# offres/models.py - Ajouter dans la classe AppelOffre

class AppelOffre(models.Model):
    """
    Table centrale. Gère les offres scrapées ET saisies manuellement."""
    STATUT_CHOICES = [
        ('Ouvert', 'Ouvert'),
        ('Clôturé', 'Clôturé'),
        ('Annulé', 'Annulé'),
        ('En cours', 'En cours'),
    ]
    
    # ✅ NOUVEAU : Types d'offres
    TYPE_OFFRE_CHOICES = [
        ('APPEL_D_OFFRES', 'Appel d\'offres (RFQ/RFP)'),
        ('APPEL_A_PROJETS', 'Appel à projets'),
        ('MANIFESTATION_INTERET', 'Manifestation d\'intérêt (EOI)'),
        ('RECRUTEMENT', 'Recrutement / Consultant'),
        ('VENTE_AUX_ENCHERES', 'Vente aux enchères'),
        ('AUTRE', 'Autre'),
    ]
    
    titre = models.CharField(max_length=300)
    organisme = models.CharField(max_length=200, verbose_name="Institution émettrice")
    
    # ✅ NOUVEAU : Type d'offre
    type_offre = models.CharField(
        max_length=50,
        choices=TYPE_OFFRE_CHOICES,
        default='APPEL_D_OFFRES',
        verbose_name="Type d'offre",
        help_text="Type d'offre (Appel d'offres, Appel à projets, etc.)",
        db_index=True  # ✅ Index pour accélérer les filtres
    )
    
    # ✅ MODIFICATION : Description maintenant optionnelle
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Résumé de l'offre",
        help_text="Description optionnelle de l'offre"
    )
    
    pays = models.CharField(
        max_length=10,
        default='BF',
        help_text="Code pays ou region (BF, SN, MULTI, REGIONAL, et.)"
    )
    
    # ✅ NOUVEAU : Domaine de l'offre (IT, Santé, Construction, etc.)
    domaine = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Domaine d'activité",
        help_text="Domaine de l'offre (IT & Digital, Santé & Médical, Ingénierie & Construction, etc.)",
        db_index=True  # ✅ Index pour accélérer les filtres
    )
    
    date_publication = models.DateField()
    date_cloture = models.DateField()
    
    url_source = models.URLField(
        max_length=500, blank=True, null=True,
        help_text="Page web où l'offre est listée"
    )
    url_tdr = models.URLField(
        max_length=500, blank=True, null=True,
        help_text="Lien direct vers le document officiel (PDF/DOC)"
    )
    
    MODES_SAISIE = [
        ('AUTO', 'Collecte Automatique (Scraping)'),
        ('MANUEL', 'Saisie Manuelle (Administrateur)'),
        ('API', 'Import via API externe'),
        ('IMPORT', 'Import fichier (CSV/Excel)'),
    ]
    
    mode_acquisition = models.CharField(
        max_length=50, 
        choices=MODES_SAISIE, 
        default='AUTO',
        help_text="Mode d'acquisition de l'offre"
    )
    source_origine = models.ForeignKey('SourceScraping', on_delete=models.SET_NULL, null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="Ouvert")

    # ✅ MODIFICATION : Upload de fichier PDF depuis PC/téléphone
    fichier_pdf = models.FileField(
        upload_to='tdr/%Y/%m/%d/',  # ✅ %Y au lieu de %y pour l'année complète
        null=True,
        blank=True,
        verbose_name="Fichier PDF (TDR)",
        help_text="Téléchargez le PDF depuis votre PC ou téléphone"
    )

    # =========================================================================
    # =========================================================================
    # 1. Résout l'erreur de blocage MariaDB (Field 'est_expire' doesn't have a default value)
    est_expire = models.BooleanField(
        default=False, 
        help_text="Indique si l'offre est marquée comme expirée"
    )
    
    # 2. Permet au frontend de calculer "Il y a 5 min", "Vient d'être scrapée", etc.
    date_scraping = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Date de collecte"
    )
    # =========================================================================

    class Meta:
        db_table = "Appel_Offre"
        verbose_name = "Appels d'Offres"
        verbose_name_plural = "Appels d'Offres"
        ordering = ['-date_publication']
        indexes = [
            models.Index(fields=['statut', 'date_cloture']),
            models.Index(fields=['pays', 'statut']),
            # ✅ NOUVEAU : Index pour optimiser les filtres par domaine
            models.Index(fields=['domaine']),
            models.Index(fields=['pays', 'domaine']),
            # ✅ NOUVEAU : Index pour le type d'offre
            models.Index(fields=['type_offre']),
        ]

    def __str__(self):
        return f"[{self.mode_acquisition}] {self.titre[:50]}..."
    
    # ✅ Méthode utilitaire pour vérifier si un PDF est disponible
    def has_pdf(self):
        """Vérifie si un PDF est disponible (fichier uploadé ou URL)"""
        return bool(self.fichier_pdf) or bool(self.url_tdr)
    
    # ✅ Méthode utilitaire pour vérifier si c'est un vrai appel d'offres
    def is_real_tender(self):
        """Vérifie si l'offre est un vrai appel d'offres"""
        return self.type_offre == 'APPEL_D_OFFRES'

# =============================================================================
# MODULE 4 : PROFILS - EXPERT (avec CV, compétences, etc.)
# =============================================================================

class ProfilExpert(models.Model):
    """
    Profil Expert - Conforme cahier des charges:
    - Nom, prénom (dans Utilisateur)
    - Date de naissance, genre (dans Utilisateur)
    - Domaine de compétence avec case à cocher
    - Charger son CV
    """
    utilisateur = models.OneToOneField(
        Utilisateur, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'EXPERT'},
        related_name='profil_expert'
    )
    
    # Domaines de compétence (case à cocher multiple)
    DOMAINES_COMPETENCE = [
        ('INFRA', 'Infrastructures et Travaux Publics'),
        ('IT', 'Informatique et Technologies'),
        ('FINANCE', 'Finance et Comptabilité'),
        ('SANTE', 'Santé et Médical'),
        ('EDUCATION', 'Éducation et Formation'),
        ('CONSULTING', 'Consulting et Management'),
        ('ENVIRONNEMENT', 'Environnement et Écologie'),
        ('AGRICULTURE', 'Agriculture et Développement Rural'),
    ]
    
    domaines_competence = models.CharField(
        max_length=500, 
        blank=True,
        help_text="Sélectionnez vos domaines de compétence"
    )
    
    # Autres compétences (texte libre)
    autres_competences = models.TextField(blank=True, help_text="Autres compétences")
    
    # CV
    cv_fichier = models.FileField(
        upload_to='cv_experts/%Y/%m/%d/', 
        verbose_name="CV (PDF)",
        blank=True,
        null=True
    )
    
    # Disponibilité
    disponible = models.BooleanField(default=True, verbose_name="Disponible pour mission")
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Expert: {self.utilisateur.first_name} {self.utilisateur.last_name}"
    
    def get_domaines_list(self):
        """Retourne la liste des domaines sélectionnés"""
        if self.domaines_competence:
            return [d.strip() for d in self.domaines_competence.split(',') if d.strip()]
        return []
    
    def profil_complet(self):
        """Vérifie si le profil expert est complet"""
        return bool(self.cv_fichier and self.domaines_competence)

    class Meta:
        db_table = "Profil_Expert"
        verbose_name = "Profil d'Expert"


# =============================================================================
# MODULE 4b : PROFILS - BUREAU D'ÉTUDE (nom, pays, adresse, domaine, email, numéro)
# =============================================================================

class BureauEtude(models.Model):
    """
    Profil Bureau d'Étude - Conforme cahier des charges:
    - Nom de la structure
    - Pays
    - Adresse
    - Domaine d'activité
    - Email de contact
    - Numéro de téléphone
    - (Pas de CV, pas de date naissance, pas de genre)
    """
    gestionnaire = models.OneToOneField(
        Utilisateur, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'BUREAU'},
        related_name='bureau_etude'
    )
    
    # Informations de la structure
    nom_structure = models.CharField(max_length=200, verbose_name="Nom de la structure")
    pays = CountryField(default='BF', verbose_name="Pays")
    adresse = models.TextField(verbose_name="Adresse complète")
    domaine_activite = models.CharField(max_length=200, verbose_name="Domaine d'activité")
    email_contact = models.EmailField(verbose_name="Email de contact", validators=[EmailValidator()])
    telephone = models.CharField(max_length=20, verbose_name="Numéro de téléphone")
    
    # Site web (optionnel)
    site_web = models.URLField(blank=True, verbose_name="Site web")
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nom_structure
    
    def profil_complet(self):
        """Vérifie si le profil bureau est complet"""
        return bool(self.nom_structure and self.email_contact and self.telephone)

    class Meta:
        db_table = "Bureau_Etude"
        verbose_name = "Bureau d'étude / Entreprise"


# =============================================================================
# MODULE 5 : CRITÈRES DE RECHERCHE ET ALERTES
# =============================================================================

class CritereRecherche(models.Model):
    """
    Critères de recherche pour les experts (alertes email)
    """
    FREQUENCE_CHOICES = [
        ('daily', 'Quotidien'),
        ('weekly', 'Hebdomadaire'),
    ]
    
    utilisateur = models.ForeignKey(
        Utilisateur, 
        on_delete=models.CASCADE, 
        related_name='criteres_recherche',
        limit_choices_to={'role': 'EXPERT'}
    )
    
    nom_critere = models.CharField(max_length=100, blank=True, help_text="Nom du critère (ex: Offres IT)")
    mots_cles = models.CharField(max_length=500, help_text="Mots-clés recherchés (séparés par des virgules)")
    pays = CountryField(default='BF', blank=True, verbose_name="Filtrer par pays")
    domaines = models.CharField(max_length=500, blank=True, help_text="Domaines recherchés")
    alerte_active = models.BooleanField(default=True, help_text="Recevoir des alertes email")
    frequence = models.CharField(max_length=20, choices=FREQUENCE_CHOICES, default='daily')
    last_notified = models.DateTimeField(null=True, blank=True)
    
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Critères de {self.utilisateur.email}"
    
    def get_mots_cles_list(self):
        return [m.strip() for m in self.mots_cles.split(',') if m.strip()]

    class Meta:
        db_table = "Critere_Recherche"
        verbose_name = "Critères de Recherche"


# =============================================================================
# MODULE 6 : NEWSLETTER ET NOTIFICATIONS
# =============================================================================

class InscriptionNewsletter(models.Model):
    email = models.EmailField(unique=True)
    date_inscription = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    
    class Meta:
        db_table = "Inscription_Newsletter"
        verbose_name = "Inscription à la Newsletter"


class Notification(models.Model):
    destinataire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    offre_liee = models.ForeignKey(AppelOffre, on_delete=models.CASCADE, null=True, blank=True)
    objet = models.CharField(max_length=200)
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    est_lue = models.BooleanField(default=False)

    class Meta:
        db_table = "Notification"
        verbose_name = "Notification"
        ordering = ['-date_envoi']


class SuggestionOffre(models.Model):
    """
    Suggestion d'expert par l'administrateur pour une offre spécifique
    ✅ MODIFIÉ : Ajout des champs pour la réponse de l'expert
    """
    STATUT_REPONSE_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('CONSULTEE', 'Consultée'),
        ('ACCEPTEE', 'Acceptée'),
        ('REFUSEE', 'Refusée'),
    ]
    
    expert = models.ForeignKey(
        ProfilExpert, 
        on_delete=models.CASCADE, 
        verbose_name="Expert sélectionned",
        related_name='suggestions_recues'
    )
    offre = models.ForeignKey(
        AppelOffre, 
        on_delete=models.CASCADE, 
        verbose_name="Offre concernée",
        related_name='suggestions'
    )
    date_suggestion = models.DateTimeField(auto_now_add=True)
    commentaire_admin = models.TextField(
        blank=True, 
        help_text="Pourquoi suggérer cet expert ?"
    )
    
    # ✅ NOUVEAU : Statut de la réponse de l'expert
    statut_reponse = models.CharField(
        max_length=20,
        choices=STATUT_REPONSE_CHOICES,
        default='EN_ATTENTE',
        verbose_name="Statut de la réponse"
    )
    
    #  NOUVEAU : Date de réponse de l'expert
    date_reponse = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Date de réponse"
    )
    
    #  NOUVEAU : Commentaire de l'expert
    commentaire_expert = models.TextField(
        blank=True,
        verbose_name="Commentaire de l'expert",
        help_text="Réponse de l'expert à la suggestion"
    )
    
    # Ancien champ (gardé pour compatibilité)
    est_consulte_par_expert = models.BooleanField(default=False)

    class Meta:
        db_table = "Suggestion_Offre"
        verbose_name = "Suggestion d'Expert pour une Offre"
        unique_together = ('expert', 'offre')
        ordering = ['-date_suggestion']

    def __str__(self):
        return f"Suggestion de {self.expert} pour {self.offre}"


# offres/models.py - Ajoutez ces champs à la classe Message

class Message(models.Model):
    """
    Modèle pour la messagerie entre utilisateurs et administrateur
    """
    
    expediteur = models.ForeignKey(
        Utilisateur, 
        on_delete=models.CASCADE, 
        related_name='messages_envoyes'
    )
    destinataire = models.ForeignKey(
        Utilisateur, 
        on_delete=models.CASCADE, 
        related_name='messages_recus'
    )
    sujet = models.CharField(max_length=200)
    contenu = models.TextField()
    est_lu = models.BooleanField(default=False)
    date_envoi = models.DateTimeField(auto_now_add=True)
    
    # ✅ NOUVEAUX CHAMPS POUR LA GESTION DES RÉPONSES
    est_reponse = models.BooleanField(default=False, help_text="True si ce message est une réponse")
    reponse_contenu = models.TextField(blank=True, null=True, help_text="Contenu de la réponse envoyée")
    message_original = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='reponses',
        help_text="Message original auquel cette réponse est liée"
    )
    
    class Meta:
        db_table = "messages"
        verbose_name = "Message"
        ordering = ['-date_envoi']
    
    def __str__(self):
        return f"{self.sujet} - {self.expediteur.email} -> {self.destinataire.email}"
    
    def marquer_comme_lu(self):
        """Marque le message comme lu"""
        self.est_lu = True
        self.save()
    
    def ajouter_reponse(self, contenu_reponse):
        """Ajoute une réponse à ce message"""
        reponse = Message.objects.create(
            expediteur=self.destinataire,
            destinataire=self.expediteur,
            sujet=f"RE: {self.sujet}",
            contenu=contenu_reponse,
            est_reponse=True,
            reponse_contenu=contenu_reponse,
            message_original=self
        )
        self.est_lu = True
        self.save()
        return reponse
#Historique des connexions des utilisateurs (pour sécurité et audit)

class HistoriqueConnexion(models.Model):
    """
    Historique des connexions des utilisateurs
    """
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='connexions')
    date_connexion = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        db_table = "historique_connexions"
        verbose_name = "Historique de connexion"
        ordering = ['-date_connexion']
    
    def __str__(self):
        return f"{self.utilisateur.email} - {self.date_connexion}"
    

class PasswordResetToken(models.Model):
    """Token pour la réinitialisation de mot de passe"""
    # ✅ REMPLACER User par settings.AUTH_USER_MODEL
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ← MODIFICATION ICI
        on_delete=models.CASCADE, 
        related_name='reset_tokens'
    )
    token = models.CharField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Token de réinitialisation"
        verbose_name_plural = "Tokens de réinitialisation"
    
    def __str__(self):
        return f"Token pour {self.user.email} - {self.created_at}"
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(48)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)  # Expire en 24h
        super().save(*args, **kwargs)
    
    @property
    def is_valid(self):
        """Vérifie si le token est encore valide"""
        return not self.used and self.expires_at > timezone.now()