from ariadne import MutationType

from ariadne_jwt import resolve_verify, resolve_refresh, resolve_token_auth

mutation = MutationType()

mutation.set_field('verifyToken', resolve_verify)
mutation.set_field('refreshToken', resolve_refresh)
mutation.set_field('tokenAuth', resolve_token_auth)
