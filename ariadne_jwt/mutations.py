from calendar import timegm
from datetime import datetime

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from promise import Promise

from . import settings
from .decorators import token_auth
from .shortcuts import get_token
from .utils import get_payload, get_user_by_payload

__all__ = ['resolve_verify', 'resolve_refresh', 'resolve_token_auth', 'jwt_schema']

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
    }
'''


def resolve_verify(obj, info, token, **kwargs):
    return {'payload': get_payload(token)}


def resolve_refresh(obj, info, token, **kwargs):
    payload = get_payload(token)
    user = get_user_by_payload(payload)
    orig_iat = payload.get('orig_iat')

    if orig_iat:
        utcnow = timegm(datetime.utcnow().utctimetuple())
        expiration = orig_iat + settings.JWT_REFRESH_EXPIRATION_DELTA.total_seconds()

        if utcnow > expiration:
            raise ValidationError(_('RefreshToken has expired'))
    else:
        raise ValidationError(_('orig_iat field is required'))

    token = get_token(user, orig_iat=orig_iat)

    return {'token': token, 'payload': payload}


@token_auth
def resolve_token_auth(obj, info, **kwargs):
    return {}
