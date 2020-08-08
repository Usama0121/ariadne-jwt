INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test',
    },
}

SECRET_KEY = 'test'

AUTHENTICATION_BACKENDS = [
    'ariadne_jwt.backends.JWTBackend',
]

ROOT_URLCONF = 'tests.urls'
