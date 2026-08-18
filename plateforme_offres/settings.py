from datetime import timedelta
import os
from pathlib import Path
import django.db.backends.mysql.base
from celery.schedules import crontab
from dotenv import load_dotenv
import pymysql
pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-s5(dq!x37k62p)t@0fj!v)b%adn5(46-dszxai1wv4_gd9n@(v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'offres',
    'django_countries',
    'django_celery_beat',
    'django_celery_results',
    'django_filters',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'storages',  
]

# Configuration Celery + Redis
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Ouagadougou'

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


    'newsletter-hebdomadaire': {
        'task': 'offres.scraping.tasks.newsletter_hebdomadaire_task',
        'schedule': crontab(day_of_week=1, hour=8, minute=0),  # Lundi à 8h
    },


    'cloture-automatique-offres-expirees': {
        'task': 'offres.scraping.tasks.close_expired_offers_task', # Adaptez le chemin si le fichier est ailleurs
        'schedule': 86400.0,  # S'exécute toutes les 24 heures (ou utilisez crontab(hour=0, minute=0))
    },

     'daily-maintenance': {
        'task': 'offres.tasks.daily_maintenance',
        'schedule': crontab(hour=2, minute=0),  # Tous les jours à 2h
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

# =============================================================================
# BASE DE DONNÉES - ✅ CORRIGÉ
# =============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'plateforme_offres',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# ✅ Forcer Django à accepter MariaDB 10.4
#django.db.backends.mysql.base.DatabaseWrapper.check_database_version_supported = lambda self: None

AUTH_USER_MODEL = 'offres.Utilisateur'

#MEDIA_URL = '/media/'
#MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
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
# STOCKAGE CLOUD (Cloudflare R2) - Pour les PDF et fichiers uploadés
# =============================================================================
# Ces variables seront lues depuis votre fichier .env ou les variables de Render
AWS_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('R2_BUCKET_NAME', 'appels-offres-media')
AWS_S3_ENDPOINT_URL = os.getenv('R2_ENDPOINT_URL') # ex: https://votre_id_compte.r2.cloudflarestorage.com
AWS_S3_REGION_NAME = 'auto' # Cloudflare gère la région automatiquement

# Rendre les fichiers accessibles publiquement (pour le téléchargement des PDF)
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False

# Domaine public personnalisé (optionnel mais recommandé pour des URLs propres)
AWS_S3_CUSTOM_DOMAIN = os.getenv('R2_PUBLIC_DOMAIN') # ex: pub-xxxx.r2.dev

# Dire à Django d'utiliser le cloud pour TOUS les fichiers (FieldFile)
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Configuration de l'URL MEDIA
if AWS_S3_CUSTOM_DOMAIN:
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
else:
    MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/'

# On garde MEDIA_ROOT commenté car il ne sera plus utilisé en production, 
# mais il peut servir en local si les variables d'environnement sont vides.
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media') 

# =============================================================================
# CONFIGURATION EMAIL - SENDGRID
# =============================================================================
# Remplacez la ligne EMAIL_BACKEND par celle-ci :
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# ✅ VALEURS EN DUR (Fonctionne à 100%, on règlera le .env plus tard)
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = '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'

DEFAULT_FROM_EMAIL = 'Plateforme Offre <moniquek029@gmail.com>'

# =============================================================================
# CONFIGURATION EMAIL - SENDGRID
# =============================================================================
load_dotenv()

#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST = 'smtp.sendgrid.net'
#EMAIL_PORT = 587
#EMAIL_USE_TLS = True

#EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'apikey')
#EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
#DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'Plateforme Offre <moniquek029@gmail.com>')

# =============================================================================
# URLS FRONTEND/BACKEND
# =============================================================================
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

# =============================================================================
# HOSTS ET CORS
# =============================================================================
ALLOWED_HOSTS = ['*']

LANGUAGE_CODE = 'fr-FR'
TIME_ZONE = 'Africa/Ouagadougou'
USE_I18N = True
USE_TZ = True

# =============================================================================
# CORS
# =============================================================================
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

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
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

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
# =============================================================================
# LOGGING - MODE ESPION SQL (Pour trouver le coupable)
# =============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
        'offres.scraping': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

