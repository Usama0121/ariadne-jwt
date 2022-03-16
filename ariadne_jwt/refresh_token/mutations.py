from calendar import timegm

from django.utils.translation import gettext as _

from .. import exceptions
from ..settings import jwt_settings
from .shortcuts import get_refresh_token


def resolve_refresh_token(obj, info, refresh_token, **kwargs):
    context = info.context
    refresh_token = get_refresh_token(refresh_token)

    if refresh_token.is_expired(context):
        raise exceptions.JSONWebTokenError(_('Refresh token is expired'))

    payload = jwt_settings.JWT_PAYLOAD_HANDLER(refresh_token.user, context)
    token = jwt_settings.JWT_ENCODE_HANDLER(payload, context)
    refreshed_token = refresh_token.rotate().token

    return {'token': token, 'payload': payload, 'refresh_token': refreshed_token}


def resolve_revoke(obj, info, refresh_token, **kwargs):
    refresh_token = get_refresh_token(refresh_token)
    refresh_token.revoke()

    return {'revoked': timegm(refresh_token.revoked.timetuple())}
