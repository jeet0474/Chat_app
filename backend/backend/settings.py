"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 5.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import os

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-c8f*sade6a#cynhu416e%i1%rz*qsq^m2qa6#qoc)org0tpgee'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# List of trusted origins for CORS
CORS_ALLOW_ALL_ORIGINS = True

# CORS settings (to handle cross-origin requests)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Add your frontend URL here
    #"https://your-production-domain.com",  # Add your production URL here
]

# Allowed hosts for the application
ALLOWED_HOSTS = []

# MongoDB settings (use environment variables for production)
# MONGO_CONNECTION_STRING = "mongodb+srv://jeet0474:Md_jeet0474@jeet.v42ik.mongodb.net/" 
# MONGO_DB_NAME = "test"


MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Your custom apps
    'users',
    # 'user_connections',

    # Third-party apps
    'corsheaders',
    
    "channels",
    
    "backend",
]

ASGI_APPLICATION = "backend.asgi.application"

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

# URL Configuration
ROOT_URLCONF = 'backend.urls'

# WSGI application
WSGI_APPLICATION = 'backend.wsgi.application'

# Database settings
# SQLite is used for development; use other databases (like PostgreSQL) for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation settings
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

# Localization settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Default primary key field type (recommended for new projects)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Template settings (for rendering HTML templates)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Add your template directories here
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

# Security settings
# CSRF settings (can be relaxed for development, but need stricter settings for production)
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",  # Allow localhost:3000 for local development
]

# Example of settings for production (you may want to adjust these for deployment)
# Example for HTTPS-only cookies in production:
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True

