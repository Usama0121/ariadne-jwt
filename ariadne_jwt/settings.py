from datetime import timedelta
from importlib import import_module

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.signals import setting_changed
import six

DEFAULTS = {
    'JWT_ALGORITHM': 'HS256',
    'JWT_AUDIENCE': None,
    'JWT_AUTH_HEADER': 'HTTP_AUTHORIZATION',
    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'JWT_ISSUER': None,
    'JWT_LEEWAY': 0,
    'JWT_SECRET_KEY': settings.SECRET_KEY,
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': False,
    'JWT_EXPIRATION_DELTA': timedelta(seconds=60 * 5),
    'JWT_ALLOW_REFRESH': True,
    'JWT_LONG_TIME_REFRESH': False,
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),
    'JWT_REFRESH_TOKEN_MODEL': 'refresh_token.RefreshToken',
    'JWT_REFRESH_TOKEN_LENGTH': 20,
    'JWT_ENCODE_HANDLER': 'ariadne_jwt.utils.jwt_encode',
    'JWT_DECODE_HANDLER': 'ariadne_jwt.utils.jwt_decode',
    'JWT_PAYLOAD_HANDLER': 'ariadne_jwt.utils.jwt_payload',
    'JWT_PAYLOAD_GET_USERNAME_HANDLER': (lambda payload: payload.get(get_user_model().USERNAME_FIELD)),
}

IMPORT_STRINGS = (
    'JWT_ENCODE_HANDLER',
    'JWT_DECODE_HANDLER',
    'JWT_PAYLOAD_HANDLER',
    'JWT_PAYLOAD_GET_USERNAME_HANDLER',
)


def perform_import(value, setting_name):
    if value is not None and isinstance(value, six.string_types):
        return import_from_string(value, setting_name)
    return value


def import_from_string(value, setting_name):
    try:
        module_path, class_name = value.rsplit('.', 1)
        module = import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        msg = 'Could not import `{}` for JWT setting `{}`. {}: {}.'.format(
            value, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)


class JWTSettings(object):

    def __init__(self, defaults, import_strings):
        self.defaults = defaults
        self.import_strings = import_strings
        self._cached_attrs = set()

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError('Invalid setting: `{}`'.format(attr))

        value = self.user_settings.get(attr, self.defaults[attr])

        if attr in self.import_strings:
            value = perform_import(value, attr)

        self._cached_attrs.add(attr)
        setattr(self, attr, value)
        return value

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(settings, 'GRAPHQL_JWT', {})
        return self._user_settings

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)

        self._cached_attrs.clear()

        if hasattr(self, '_user_settings'):
            delattr(self, '_user_settings')


def reload_settings(*args, **kwargs):
    setting = kwargs['setting']

    if setting == 'GRAPHQL_JWT':
        jwt_settings.reload()


setting_changed.connect(reload_settings)

jwt_settings = JWTSettings(DEFAULTS, IMPORT_STRINGS)
