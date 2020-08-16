from django.utils.translation import ugettext as _

from . import exceptions
from .settings import jwt_settings
from .decorators import token_auth
from .utils import get_payload, get_user_by_payload
from .refresh_token.mutations import resolve_refresh_token, resolve_revoke

__all__ = ['resolve_verify', 'resolve_refresh', 'resolve_revoke', 'resolve_token_auth', 'jwt_schema']

jwt_schema = '''
    scalar GenericScalar
    
    type VerifyToken {
        payload: GenericScalar
    }
    type RefreshToken {
        token: String
        refresh_token: String
        payload: GenericScalar
    }
    type TokenAuth {
        token: String
        refresh_token: String
        payload: GenericScalar
    }
    type RevokeToken {
        revoked: Int
    }
'''


def resolve_verify(obj, info, token, **kwargs):
    return {'payload': get_payload(token, info.context)}


def resolve_keep_alive_refresh_token(obj, info, token, **kwargs):
    context = info.context
    payload = get_payload(token, context)
    user = get_user_by_payload(payload)
    orig_iat = payload.get('origIat')

    if not orig_iat:
        raise exceptions.JSONWebTokenError(_('origIat field is required'))

    if jwt_settings.JWT_REFRESH_EXPIRED_HANDLER(orig_iat, context):
        raise exceptions.JSONWebTokenError(_('Refresh has expired'))

    payload = jwt_settings.JWT_PAYLOAD_HANDLER(user, context)
    payload['origIat'] = orig_iat
    token = jwt_settings.JWT_ENCODE_HANDLER(payload, context)

    return {'token': token, 'payload': payload}


def resolve_refresh(obj, info, token, **kwargs):
    return (resolve_refresh_token(obj, info, token, **kwargs)
            if jwt_settings.JWT_LONG_RUNNING_REFRESH_TOKEN
            else resolve_keep_alive_refresh_token(obj, info, token, **kwargs))


@token_auth
def resolve_token_auth(obj, info, **kwargs):
    return {}
