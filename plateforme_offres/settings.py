

from datetime import timedelta
import os
from pathlib import Path
from dotenv import load_dotenv

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
#CELERY_BROKER_URL = 'memory://'  # (optionnel, si vous avez Redis installé)
#CELERY_RESULT_BACKEND = 'django-db'  # Stocke les résultats dans la base Django (via django-celery-results)


#CELERY_RESULT_BACKEND = 'django-db'
#CELERY_IMPORTS=('offres.scraping.tasks',)  # Import des tâches pour que Celery les reconnaisse

# Configuration supplémentaire requise
#CELERY_TIMEZONE = 'Africa/Ouagadougou'
#CELERY_TASK_TRACK_STARTED = True
#CELERY_TASK_TIME_LIMIT = 30 * 60
#CELERY_RESULT_EXTENDED = True #  # Requis pour django-celery-results


# Configuration Celery + Redis
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Ouagadougou'

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

# Taille max des uploads (10 MB)
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

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
# =============================================================================
# CONFIGURATION EMAIL - SENDGRID
# =============================================================================
load_dotenv()

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'apikey')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'Plateforme Offre <moniquek029@gmail.com>')  # ✅ Sans espace

# =============================================================================
# URLS FRONTEND/BACKEND
# =============================================================================
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

# =============================================================================
# HOSTS ET CORS - ✅ IMPORTANT POUR NGROK !
# =============================================================================
ALLOWED_HOSTS = ['*']  # ✅ En développement seulement

LANGUAGE_CODE = 'fr-FR'
TIME_ZONE = 'Africa/Ouagadougou'
USE_I18N = True
USE_TZ = True

# =============================================================================
# CORS - Autoriser localhost ET ngrok
# =============================================================================
CORS_ALLOW_ALL_ORIGINS = True  # ✅ En développement seulement (plus simple)
CORS_ALLOW_CREDENTIALS = True

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

# =============================================================================
# STATIC FILES
# =============================================================================
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),   
)

# =============================================================================
# REST FRAMEWORK
# =============================================================================
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# =============================================================================
# JWT CONFIGURATION
# =============================================================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'UPDATE_LAST_LOGIN': True,
    'SIGNING_KEY': SECRET_KEY,
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'TOKEN_TYPE_CLAIM': 'token_type',
}