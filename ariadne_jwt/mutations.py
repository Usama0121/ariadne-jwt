from django.utils.translation import ugettext as _

from . import exceptions
from .settings import jwt_settings
from .decorators import token_auth
from .shortcuts import get_token
from .utils import get_payload, get_user_by_payload
from .refresh_token.mutations import resolve_long_running_refresh_token, resolve_revoke

__all__ = ['resolve_verify', 'resolve_refresh', 'resolve_revoke', 'resolve_token_auth', 'jwt_schema']

jwt_schema = '''
    scalar GenericScalar
    
    type VerifyToken {
        payload: GenericScalar
    }
    type RefreshToken {
        token: String
        payload: GenericScalar
    }
    type TokenAuth {
        token: String
        payload: GenericScalar
    }
'''
if jwt_settings.JWT_LONG_TIME_REFRESH:
    jwt_schema += '''
    extend type RefreshToken {
        refresh_token: String
    }
    extend type TokenAuth {
        refresh_token: String
    }
    '''


def resolve_verify(obj, info, token, **kwargs):
    return {'payload': get_payload(token, info.context)}


def resolve_keep_alive_refresh_token(obj, info, token, **kwargs):
    payload = get_payload(token, info.context)
    user = get_user_by_payload(payload)
    orig_iat = payload.get('origIat')

    if not orig_iat:
        raise exceptions.JSONWebTokenError(_('origIat field is required'))

    if jwt_settings.JWT_REFRESH_EXPIRED_HANDLER(orig_iat, info.context):
        raise exceptions.JSONWebTokenError(_('Refresh has expired'))

    token = get_token(user, info.context, origIat=orig_iat)

    return {'token': token, 'payload': payload}


def resolve_refresh(obj, info, token, **kwargs):
    return (resolve_long_running_refresh_token(obj, info, token, **kwargs)
            if jwt_settings.JWT_LONG_TIME_REFRESH
            else resolve_keep_alive_refresh_token(obj, info, token, **kwargs))


@token_auth
def resolve_token_auth(obj, info, **kwargs):
    return {}
