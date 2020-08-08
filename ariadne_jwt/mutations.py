import ariadne
from calendar import timegm
from datetime import datetime

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from . import settings
from .shortcuts import get_token
from .utils import get_payload, get_user_by_payload

jwt_schema = '''
    scalar GenericScalar
    
    type Verify {
        payload: GenericScalar
    }
    type Refresh {
        token: String
        payload: GenericScalar
    }
'''


def verify(obj, info, token, **kwargs):
    payload = get_payload(token)
    return {'payload': payload}


def refresh(obj, info, token, **kwargs):
    payload = get_payload(token)
    user = get_user_by_payload(payload)
    orig_iat = payload.get('orig_iat')

    if orig_iat:
        utcnow = timegm(datetime.utcnow().utctimetuple())
        expiration = orig_iat + settings.JWT_REFRESH_EXPIRATION_DELTA.total_seconds()

        if utcnow > expiration:
            raise ValidationError(_('Refresh has expired'))
    else:
        raise ValidationError(_('orig_iat field is required'))

    token = get_token(user, orig_iat=orig_iat)

    return {'token': token, 'payload': payload}
