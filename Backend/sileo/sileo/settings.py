"""
Django settings for sileo project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

SECRET_KEY = 'xoshs+fvjv1gib^4sf8_01y5njom433enjv+j8gvhufy4w80*1'

ROOT_URLCONF = 'sileo.urls'

STATIC_URL = '/static/'

STORAGE_PATH = './dev_storage'

SILEO_API_FALLBACK_VERSION = 'v1'
SILEO_ALLOWED_VERSIONS = ('v1', 'v2')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

INSTALLED_APPS = (
    'sileo',
    'django.contrib.auth',
    'django.contrib.contenttypes',)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',)

ROOT_URLCONF = 'sileo.urls'
