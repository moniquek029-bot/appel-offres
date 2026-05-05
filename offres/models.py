from django.db import models

# Creation des  models.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
from django_countries.fields import CountryField


# MODULE 1 : GESTION DES COMPTES ET AUTHENTIFICATION

class Utilisateur(AbstractUser):
    """
    Modèle qui remplace l'utilisateur par défaut de Django.
    Permet de gérer les rôles spécifiques : Administrateur, Expert, Visiteur, Bureau.
    """
    CHOIX_ROLES = [
        ('ADMIN', 'Administrateur'),
        ('EXPERT', 'Expert'),
        ('VISITEUR', 'Visiteur'),
        ('BUREAU', 'Bureau d\'étude / Entreprise'),
    ]
    # Champ pour distinguer les types d'utilisateurs sur la plateforme
    role = models.CharField(max_length=20, choices=CHOIX_ROLES, default='VISITEUR')
    
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    pays=CountryField(default='BF', blank=True, verbose_name="Pays de résidence")
    adresse=models.CharField(max_length=255, blank=True, verbose_name="Adresse complète")
    date_naissance = models.DateField(null=True, blank=True)
    genre = models.CharField(max_length=1, choices=[('M', 'Masculin'), ('F', 'Féminin')], blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"



# MODULE 2 : VEILLE ET COLLECTE AUTOMATISÉE (WEB SCRAPING)[cite: 1]

class SourceScraping(models.Model):
    """
    Table de configuration pour le script Python (Module 2)[cite: 1].
    Elle contient les sites web que le robot doit parcourir.
    """
    nom = models.CharField(max_length=100, verbose_name="Nom du site source")
    url_racine = models.URLField(verbose_name="Lien de la page d'accueil")
    frequence_maj = models.CharField(max_length=50, help_text="Ex: Toutes les 12 heures")
    est_actif = models.BooleanField(default=True, help_text="Désactiver si le site change de structure")

    def __str__(self):
        return self.nom



# MODULE 3 : CONSULTATION ET RECHERCHE D'OFFRES
class AppelOffre(models.Model):
    """
    Table centrale stockant les offres. 
    Elle gère maintenant deux sources : le Scraping et la Saisie Manuelle par l'Admin.
    """
    # Informations de base de l'offre
    titre = models.CharField(max_length=300)
    organisme = models.CharField(max_length=200, verbose_name="Institution émettrice")
    description = models.TextField(verbose_name="Résumé de l'offre")
    pays = CountryField(default='BF') 
    date_publication = models.DateField()
    date_cloture = models.DateField()
    
    # --- MODIFICATIONS POUR LA PUBLICATION MANUELLE ---
    
    # L'URL devient optionnelle (null=True, blank=True) car une offre 
    # saisie manuellement n'a pas forcément de lien Web immédiat.
    url_tdr = models.URLField(
        unique=True, 
        null=True, 
        blank=True, 
        verbose_name="Lien source officiel (si existe)"
    )
    
    # champ pour savoir si l'offre a été publiée par l'administrateur ou collectée
    MODES_SAISIE = [
        ('AUTO', 'Collecte Automatique (Scraping)'),
        ('MANUEL', 'Saisie Manuelle (Administrateur)'),
    ]
    mode_acquisition = models.CharField(
        max_length=10, 
        choices=MODES_SAISIE, 
        default='AUTO'
    )

    # La source de scraping devient optionnelle pour les offres manuelles
    source_origine = models.ForeignKey(
        'SourceScraping', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Laisser vide si c'est une publication manuelle"
    )

    statut = models.CharField(max_length=50, default="Ouvert")

    class Meta:
        verbose_name = "Appel d'Offre"
        verbose_name_plural = "Appels d'Offres"
        ordering = ['-date_publication']

    def __str__(self):
        return f"[{self.mode_acquisition}] {self.titre}"



# MODULE 4 : GESTION DE LA CVTHÈQUE ET ALERTES CIBLÉES[cite: 1]

class ProfilExpert(models.Model):
    """
    Extension du compte Utilisateur pour les Experts uniquement[cite: 1].
    Permet de stocker le CV physique pour la suggestion d'expert par l'admin.
    """
    
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, limit_choices_to={'role': 'EXPERT'})
    domaine_competence = models.CharField(max_length=255, help_text="Ex: Infrastructures, IT, Finance")
    cv_fichier = models.FileField(upload_to='cv_experts/', verbose_name="CV (PDF)")
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dossier Expert : {self.utilisateur.last_name}"


class CritereRecherche(models.Model):
    """
    Définit ce que l'utilisateur recherche précisément.
    Sert de base pour le système de matching automatisé.
    """
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='criteres')
    mots_cles = models.CharField(max_length=255, help_text="Ex: 'Forage', 'Audit informatique'")
    description_recherchee = models.TextField(blank=True, verbose_name="Description détaillée du besoin")
    alerte_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Filtres de {self.utilisateur.username}"


class InscriptionNewsletter(models.Model):
    """
    Gestion des simples visiteurs qui laissent uniquement leur email[cite: 1].
    """
    email = models.EmailField(unique=True)
    date_inscription = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Notification(models.Model):
    """
    Table des messages envoyés aux utilisateurs connectés[cite: 1].
    Utilisée pour les alertes ciblées quand une offre correspond aux critères.
    """
    destinataire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    offre_liee = models.ForeignKey(AppelOffre, on_delete=models.CASCADE, null=True, blank=True)
    objet = models.CharField(max_length=200)
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    est_lue = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_envoi']


# ENTITÉ BUREAU D'ÉTUDE (Demandé dans le diagramme de classe)[cite: 1]

class BureauEtude(models.Model):
    """
    Représente les structures morales (entreprises) sur la plateforme[cite: 1].
    """
    nom_structure = models.CharField(max_length=200)
    domaine_activite = models.CharField(max_length=200)
    email_contact = models.EmailField(validators=[EmailValidator()])
    telephone = models.CharField(max_length=20)
    # L'utilisateur rattaché à ce bureau doit avoir le rôle 'BUREAU'
    gestionnaire = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, limit_choices_to={'role': 'BUREAU'})

    def __str__(self):
        return self.nom_structure
    
    #L'administrateur peut suggerer le CV d'un expert 
    # offres/models.py

class SuggestionOffre(models.Model):
    expert = models.ForeignKey(ProfilExpert, on_delete=models.CASCADE, verbose_name="Expert sélectionné")
    offre = models.ForeignKey(AppelOffre, on_delete=models.CASCADE, verbose_name="Offre concernée")
    date_suggestion = models.DateTimeField(auto_now_add=True)
    commentaire_admin = models.TextField(blank=True, help_text="Pourquoi suggérer cet expert ?")
    est_consulte_par_expert = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Suggestion d'expert"
        unique_together = ('expert', 'offre') # Évite de suggérer deux fois le même expert pour la même offre

    def __str__(self):
        return f"Suggestion de {self.expert} pour {self.offre}"