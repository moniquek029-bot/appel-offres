from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import EmailValidator
from django_countries.fields import CountryField


# =============================================================================
# MODULE 1 : GESTION DES COMPTES ET AUTHENTIFICATION
# =============================================================================

class UtilisateurManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est requise")
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
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
    # ✅ Correction : défaut cohérent avec les choix
    role = models.CharField(max_length=20, choices=CHOIX_ROLES, default='EXPERT')
    
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    pays = CountryField(default='BF', blank=True, verbose_name="Pays de résidence")
    adresse = models.CharField(max_length=255, blank=True, verbose_name="Adresse complète")
    date_naissance = models.DateField(null=True, blank=True)
    genre = models.CharField(max_length=1, choices=[('M', 'Masculin'), ('F', 'Féminin')], blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = UtilisateurManager()

    # ✅ Correction : utilisait self.username qui est None → crash
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    class Meta:
        db_table = 'utilisateurs'
        verbose_name = "Utilisateur"


# =============================================================================
# MODULE 2 : VEILLE ET COLLECTE AUTOMATISÉE
# =============================================================================

class SourceScraping(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom du site source")
    url_racine = models.URLField(verbose_name="Lien de la page d'accueil")
    frequence_maj = models.CharField(max_length=50, help_text="Ex: Toutes les 12 heures")
    est_actif = models.BooleanField(default=True, help_text="Désactiver si le site change de structure")
    last_scraped = models.DateTimeField(null=True, blank=True, verbose_name="Dernier scraping")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        verbose_name = "Source de scraping"
        verbose_name_plural = "Sources de scraping"
    
    def __str__(self):
        return self.nom


# =============================================================================
# MODULE 3 : CONSULTATION ET RECHERCHE D'OFFRES
# =============================================================================

class AppelOffre(models.Model):
    """
    Table centrale. Gère les offres scrapées ET saisies manuellement.
    """
    STATUT_CHOICES = [
        ('Ouvert', 'Ouvert'),
        ('Clôturé', 'Clôturé'),
        ('Annulé', 'Annulé'),
        ('En cours', 'En cours'),
    ]
    
    titre = models.CharField(max_length=300)
    organisme = models.CharField(max_length=200, verbose_name="Institution émettrice")
    description = models.TextField(verbose_name="Résumé de l'offre")
    pays = CountryField(default='BF') 
    date_publication = models.DateField()
    date_cloture = models.DateField()
    
    # ✅ NOUVEAU : Séparation URL source (page de listing) et URL TDR (document)
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
    ]
    mode_acquisition = models.CharField(max_length=10, choices=MODES_SAISIE, default='AUTO')
    source_origine = models.ForeignKey('SourceScraping', on_delete=models.SET_NULL, null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="Ouvert")

    class Meta:
        db_table = "Appel_Offre"
        verbose_name = "Appels d\ Offres"
        ordering = ['-date_publication']
        indexes = [
            models.Index(fields=['statut', 'date_cloture']),
            models.Index(fields=['pays', 'statut']),
        ]

    def __str__(self):
        return f"[{self.mode_acquisition}] {self.titre[:50]}..."


# =============================================================================
# MODULE 4 : CVTHÈQUE, ALERTES & PROFILS
# =============================================================================

class ProfilExpert(models.Model):
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, limit_choices_to={'role': 'EXPERT'})
    domaine_competence = models.CharField(max_length=255, help_text="Ex: Infrastructures, IT, Finance")
    cv_fichier = models.FileField(upload_to='cv_experts/', verbose_name="CV (PDF)")
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dossier Expert : {self.utilisateur.last_name}"

    class Meta:
        db_table = "Profil_Expert"
        verbose_name = "Profil d'Expert"


class CritereRecherche(models.Model):
    """
    ✅ Correction : ForeignKey au lieu de OneToOneField pour permettre plusieurs critères par expert
    """
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='criteres', limit_choices_to={'role': 'EXPERT'})
    mots_cles = models.CharField(max_length=255, help_text="Ex: 'Forage', 'Audit informatique'")
    description_recherchee = models.TextField(blank=True, verbose_name="Description détaillée du besoin")
    alerte_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Filtres de {self.utilisateur.email}"
    
    class Meta:
        db_table = "Critere_Recherche"
        verbose_name = "Critères de Recherche"


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


class BureauEtude(models.Model):
    """
    ✅ Ajout du champ cv_fichier pour l'upload de documents structure
    """
    nom_structure = models.CharField(max_length=200)
    domaine_activite = models.CharField(max_length=200)
    email_contact = models.EmailField(validators=[EmailValidator()])
    telephone = models.CharField(max_length=20)
    cv_fichier = models.FileField(upload_to='cv_bureaux/', null=True, blank=True, verbose_name="Documents structure")
    gestionnaire = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, limit_choices_to={'role': 'BUREAU'})

    def __str__(self):
        return self.nom_structure
    
    class Meta:
        db_table = "Bureau_Etude"
        verbose_name = "Bureau d'étude / Entreprise"


class SuggestionOffre(models.Model):
    """
    ✅ Correction : fusion des deux class Meta en un seul bloc
    """
    expert = models.ForeignKey(ProfilExpert, on_delete=models.CASCADE, verbose_name="Expert sélectionné")
    offre = models.ForeignKey(AppelOffre, on_delete=models.CASCADE, verbose_name="Offre concernée")
    date_suggestion = models.DateTimeField(auto_now_add=True)
    commentaire_admin = models.TextField(blank=True, help_text="Pourquoi suggérer cet expert ?")
    est_consulte_par_expert = models.BooleanField(default=False)

    class Meta:
        db_table = "Suggestion_Offre"
        verbose_name = "Suggestion d'Expert pour une Offre"
        unique_together = ('expert', 'offre')

    def __str__(self):
        return f"Suggestion de {self.expert} pour {self.offre}"