from calendar import timegm

from django.utils.translation import ugettext as _

from .. import exceptions
from ..shortcuts import get_token
from ..utils import get_payload
from .shortcuts import get_refresh_token

type_defs = '''
    type RevokeToken {
        revoked: Int
    }
    type RefreshToken {
        token: String
        refresh_token: String
        payload: GenericScalar
    }
    extend type Mutation {
    revokeToken(refresh_token:String!): RevokeToken
    refreshToken(refresh_token:String!): RefreshToken
}
'''


def long_running_refresh_token(obj, info, refresh_token, **kwargs):
    refresh_token = get_refresh_token(refresh_token)

    if refresh_token.is_expired(info.context):
        raise exceptions.JSONWebTokenError(_('Refresh token is expired'))

    token = get_token(refresh_token.user, info.context)
    payload = get_payload(token, info.context)
    refresh_token = refresh_token.rotate().token

    return {'token': token, 'payload': payload, 'refresh_token': refresh_token}


def revoke_token(obj, info, refresh_token, **kwargs):
    refresh_token = get_refresh_token(refresh_token)
    refresh_token.revoke()

    return {'revoked': timegm(refresh_token.revoked.timetuple())}
