from ariadne import MutationType
from django.contrib.auth import authenticate, login

from ariadne_jwt import resolve_verify, resolve_refresh
from ariadne_jwt.shortcuts import get_token

mutation = MutationType()

mutation.set_field('verifyToken', resolve_verify)
mutation.set_field('refreshToken', resolve_refresh)


@mutation.field('LogIn')
def resolve_login(obj, info, **kwargs):
    user = authenticate(**kwargs)

    if user is None:
        raise Exception('Please enter a correct username and password')

    if not user.is_active:
        raise Exception('It seems your account has been disabled')

    login(info.context.get('request'), user)
    return {'token': get_token(user)}
