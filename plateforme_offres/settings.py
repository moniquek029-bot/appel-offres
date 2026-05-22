

from datetime import timedelta
import os
from pathlib import Path

#import corsheaders

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-s5(dq!x37k62p)t@0fj!v)b%adn5(46-dszxai1wv4_gd9n@(v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
            #ajout de l'application "Offres" à la liste des applications installées
    'offres',
    'django_countries',
    'django_celery_beat',
    'django_celery_results',
    'django_filters',

    #Applications tierces pour la gestion des rôles et permissions'
    'rest_framework',
    'rest_framework_simplejwt',


    'corsheaders',



]
#  Configuration Celery CORRECTE pour développement sans Redis

# Broker : utilise la mémoire (léger, sans installation, DEV uniquement)
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # (optionnel, si vous avez Redis installé)
CELERY_RESULT_BACKEND = 'django-db'  # Stocke les résultats dans la base Django (via django-celery-results)

CELERY_BROKER_URL='redis://localhost:6379/0'  # (optionnel, si vous avez Redis installé)
CELERY_RESULT_BACKEND='redis://localhost:6379/0'  # (optionnel, pour stocker les résultats dans Redis)
# Result Backend : stocke les résultats dans la base Django (via django-celery-results)
CELERY_RESULT_BACKEND = 'django-db'
CELERY_IMPORTS=('offres.scraping.tasks',)  # Import des tâches pour que Celery les reconnaisse

# Configuration supplémentaire requise
CELERY_TIMEZONE = 'Africa/Ouagadougou'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_RESULT_EXTENDED = True  # Requis pour django-celery-results

# Planning des tâches (inchangé)
CELERY_BEAT_SCHEDULE = {
  
    
    'archive-expired-daily': {
        'task': 'offres.scraping.tasks.daily_archive_task',
        'schedule': 86400.0,
    },
    'matching-et-alertes-quotidien': {
        'task': 'offres.scraping.tasks.daily_alert_matching_task',
        'schedule': 86400.0,
        'options': {'queue': 'emails'},
    },
}
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'plateforme_offres.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'plateforme_offres.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
                    #CONNEXION A LA BASE DE DONNEES MYSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        #'NAME': BASE_DIR / 'db.sqlite3',
        'NAME': 'appel_d_offres',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

    #Pour utiliser notre modèle d'utilisateur personnalisé
AUTH_USER_MODEL = 'offres.Utilisateur'
    #Pour stocker les fichiers CV des experts
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8, # Exige un mot de passe d'au moins 8 caractères
        }
    },  
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# settings.py
# =============================================================================
# CONFIGURATION EMAIL (Mailtrap via django-anymail)
# =============================================================================
# =============================================================================
# CONFIGURATION EMAIL - Mailtrap SMTP (Test uniquement)
# =============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
EMAIL_PORT = 2525
EMAIL_HOST_USER = '3dce7fc33711b7' #identifiant pour Mailtrap (à remplacer par vos propres identifiants Mailtrap)
EMAIL_HOST_PASSWORD = '7d21e4c566a34d'  #mot de passe pour Mailtrap (à remplacer par vos propres identifiants Mailtrap)
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'hello@demomailtrap.co'
SERVER_EMAIL = DEFAULT_FROM_EMAIL
# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'fr-FR'

TIME_ZONE = 'Africa/Ouagadougou'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/


STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),   
)

#CORS configuration pour permettre les requêtes depuis le frontend (React) pendant le développement
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # Adresse du frontend React en développement
    'http://127.0.0.1:3000',  # Adresse alternative du frontend React
    'http://localhost:5173',  # Adresse du frontend React en développement (Vite)
    'http://127.0.0.1:5173',  # Adresse alternative du frontend React (Vite)
]
CORS_ALLOW_ALL_CREDENTIALS=True

# Optionnel : headers autorisés
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny', # Permet l'accès libre pendant le développement
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication', # Utilise JWT pour l'authentification
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10, # Nombre d'éléments par page pour la pagination
}

# Configuration pour les tokens JWT (si utilisé)
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60), # Durée de vie du token d'accès
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1), # Durée de vie du token de rafraîchissement
    'ROTATE_REFRESH_TOKENS': True, # Permet de faire tourner les tokens de rafraîchissement pour plus de sécurité
    'BLACKLIST_AFTER_ROTATION': True, # Noircit les tokens de rafraîchissement après leur utilisation
    'ALGORITHM': 'HS256', # Algorithme de signature du token
    'UPDATE_LAST_LOGIN': True, # Met à jour la date de dernière connexion lors de l'utilisation du token
    'SIGNING_KEY': SECRET_KEY, # Clé de signature du token (utilise la clé secrète de Django)
    'USER_ID_FIELD': 'id', # Champ utilisé pour identifier l'utilisateur dans le token
    'USER_ID_CLAIM': 'user_id', # Nom de la revendication dans le token qui contient l'ID de l'utilisateur
    'AUTH_HEADER_TYPES': ('Bearer',), # Type d'en-tête pour l'authentification
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION', # Nom de l'en-tête d'authentification
    'TOKEN_TYPE_CLAIM': 'token_type', # Nom de la revendication dans le token qui contient le type de token
}