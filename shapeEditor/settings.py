"""
Django settings for shapeEditor project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '2qtnah4)d$96m=f&9)k9j0-))c3r-ab0kiua)a6qfxb)v)s^tn'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'shapeEditor.shared',
    'shapeEditor.editor',
    'shapeEditor.shapefileIO',
    'shapeEditor.tms',
    'django.contrib.staticfiles',
    'south',
    'django.contrib.formtools',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
)

ROOT_URLCONF = 'shapeEditor.urls'

WSGI_APPLICATION = 'shapeEditor.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'shapeeditor',
	'USER': 'natallia'	
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/shapeEditor/'
STATICFILES_DIRS = (
    '/home/natallia/shapeEditor/shapeEditor/static',)


EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_PASSWORD = 'XXX' 
EMAIL_HOST_USER = "XXXXXXXXXXXXXn"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
