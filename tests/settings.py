INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'ariadne_jwt.refresh_token.apps.RefreshTokenConfig'
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    },
}

SECRET_KEY = 'test'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'ariadne_jwt.backends.JSONWebTokenBackend',
]
