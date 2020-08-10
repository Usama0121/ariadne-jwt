from ariadne import MutationType

from ariadne_jwt import resolve_verify, resolve_refresh
from ariadne_jwt.decorators import token_auth


@token_auth
def resolve_token_auth(obj, info, **kwargs):
    return {'user': info.context.get('request').user}


mutation = MutationType()

mutation.set_field('verifyToken', resolve_verify)
mutation.set_field('refreshToken', resolve_refresh)
mutation.set_field('tokenAuth', resolve_token_auth)
