from calendar import timegm

from django.utils.translation import ugettext as _

from .. import exceptions
from ..shortcuts import get_token
from ..utils import get_payload
from .shortcuts import get_refresh_token


def resolve_refresh_token(obj, info, refresh_token, **kwargs):
    refresh_token = get_refresh_token(refresh_token)

    if refresh_token.is_expired(info.context):
        raise exceptions.JSONWebTokenError(_('Refresh token is expired'))

    token = get_token(refresh_token.user, info.context)
    payload = get_payload(token, info.context)
    refreshed_token = refresh_token.rotate().token

    return {'token': token, 'payload': payload, 'refresh_token': refreshed_token}


def resolve_revoke(obj, info, refresh_token, **kwargs):
    refresh_token = get_refresh_token(refresh_token)
    refresh_token.revoke()

    return {'revoked': timegm(refresh_token.revoked.timetuple())}
