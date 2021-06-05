"""
Django settings for KitchenSite project.

Generated by 'django-admin startproject' using Django 3.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!


EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'service@tkckitchens.co.uk'
EMAIL_HOST_PASSWORD = 'rkpoibdxvvnohnrh'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

ALLOWED_HOSTS = ['tkc-kitchen.nw.r.appspot.com', '127.0.0.1', 'tkckitchens.co.uk', 'www.tkckitchens.co.uk',]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # installed/added by me
    'application.apps.ApplicationConfig',
    'adminPanel',
    'bootstrap4',
    'django_filters',
    'ckeditor',
    'openpyxl',
    'ckeditor_uploader',
    'jquery',
    'django_social_share',
    'google_analytics',
    'corsheaders',
    'webpush',
    'compressor',
    'crispy_forms',
    'tawkto',
]

TAWKTO_ID_SITE = '609415aab1d5182476b65aae'
TAWKTO_API_KEY = 'cd414feaa0eaaa11f0a234cbdadd472efbad0c9d'
SITE_ID = 1
CKEDITOR_UPLOAD_PREFIX = 'media/uploads/'
CKEDITOR_UPLOAD_PATH = "media/uploads/"
GOOGLE_ANALYTICS = {
    'google_analytics_id': 'G-WKLM57GY6R',
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
CORS_ALLOWED_ORIGINS = [
    "https://tkc-kitchen.nw.r.appspot.com",
    "https://www.tkckitchens.co.uk",
    "https://tkckitchens.co.uk",
]

ROOT_URLCONF = 'KitchenSite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'KitchenSite.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
import pymysql

pymysql.version_info = (1, 4, 6, 'final', 0)
pymysql.install_as_MySQLdb()
DEBUG = True

if DEBUG == False:
    DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'HOST': '127.0.0.1',
                'USER': 'root',
                'PASSWORD': 'tkc-kitchen',
                'NAME': 'main',
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
WEBPUSH_SETTINGS = {
   "VAPID_PUBLIC_KEY": "BP47yAVLNSvHVWDJkzMeu6FduiBLmP6ve-AUgFeUA7uCKdBEXZRVnvZ7-ikzo-PRFECedMaiQIwyqIlYj1csCq4",
   "VAPID_PRIVATE_KEY": "TAOidJ8NGiLG88NnIMfelb2UxGIVaEQfUyvRQEO2yJ4",
   "VAPID_ADMIN_EMAIL": "admin@example.com"
}
# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'staticfiles'),)
COMPRESS_ROOT = os.path.join(BASE_DIR, 'static')
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_FILTERS = {
    'css': ['compressor.filters.css_default.CssAbsoluteFilter'],
    'js': ['compressor.filters.jsmin.JSMinFilter']
}

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
# cloud_sql_proxy.exe -instances="tkc-kitchen:europe-west2:application-instance"=tcp:3307
if DEBUG:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False
else:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

DEFAULT_FILE_STORAGE = 'KitchenSite.gcloud.GoogleCloudMediaFileStorage'
GS_PROJECT_ID = 'tkc-kitchen'
GS_BUCKET_NAME = 'kitchensite'
MEDIA_ROOT = "media/"
UPLOAD_ROOT = 'media/'
MEDIA_URL = 'https://storage.googleapis.com/{}/'.format(GS_BUCKET_NAME)

from google.oauth2 import service_account

GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    os.path.join(BASE_DIR, 'credential.json')
)

LOGOUT_REDIRECT_URL = 'application:login'