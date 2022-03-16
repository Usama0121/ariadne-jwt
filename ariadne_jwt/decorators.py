from functools import wraps

import six
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext as _
from graphql import GraphQLResolveInfo

from promise import Promise, is_thenable

from . import exceptions
from .shortcuts import get_token
from .settings import jwt_settings
from .utils import get_authorization_header
from .refresh_token.shortcuts import create_refresh_token

__all__ = [
    'user_passes_test',
    'login_required',
    'staff_member_required',
    'permission_required',
    'token_auth',
]


def context(f):
    def decorator(func):
        def wrapper(*args, **kwargs):
            info = next(arg for arg in args
                        if isinstance(arg, GraphQLResolveInfo))
            return func(info.context, *args, **kwargs)

        return wrapper

    return decorator


def user_passes_test(test_func):
    def decorator(f):
        @wraps(f)
        @context(f)
        def wrapper(context, *args, **kwargs):
            if test_func(context.get('request').user):
                return f(*args, **kwargs)
            raise exceptions.PermissionDenied()

        return wrapper

    return decorator


login_required = user_passes_test(lambda u: u.is_authenticated)
staff_member_required = user_passes_test(lambda u: u.is_active and u.is_staff)


def permission_required(perm):
    def check_perms(user):
        if isinstance(perm, six.string_types):
            perms = (perm,)
        else:
            perms = perm

        if user.has_perms(perms):
            return True
        return False

    return user_passes_test(check_perms)


def token_auth(f):
    @wraps(f)
    def wrapper(root, info, password, **kwargs):
        def on_resolve(values):
            user, payload = values
            payload['token'] = get_token(user, info.context)
            if jwt_settings.JWT_LONG_RUNNING_REFRESH_TOKEN:
                payload['refresh_token'] = create_refresh_token(user).token
            return payload

        username = kwargs.get(get_user_model().USERNAME_FIELD)

        if get_authorization_header(info.context.get('request')) is not None:
            del info.context.get('request').META[jwt_settings.JWT_AUTH_HEADER]

        user = authenticate(info.context.get('request'),
                            username=username,
                            password=password)

        if user is None:
            raise exceptions.JSONWebTokenError(
                _('Please, enter valid credentials'))

        if hasattr(info.context.get('request'), 'user'):
            info.context.get('request').user = user

        result = f(root, info, **kwargs)
        values = (user, result)
        # Improved mutation with thenable check
        if is_thenable(result):
            return Promise.resolve(values).then(on_resolve)
        return on_resolve(values)

    return wrapper
