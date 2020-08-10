# Ariadne JWT

JSON Web Token for Ariadne Django


## Installation
~~~shell script
pip install ariadne-jwt
~~~

Include the JWT middleware in your `MIDDLEWARE` settings:

~~~python
MIDDLEWARE = [
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'ariadne_jwt.middleware.JSONWebTokenMiddleware',
]
~~~

Include the JWT backend in your `AUTHENTICATION_BACKENDS` settings:

~~~python
AUTHENTICATION_BACKENDS = [
    'ariadne_jwt.backends.JSONWebTokenBackend',
    'django.contrib.auth.backends.ModelBackend'
]
~~~

## Login
~~~python
import ariadne
from ariadne_jwt.shortcuts import get_token
from django.contrib.auth import authenticate, login
    
type_defs = '''
    scalar GenericScalar
    
    type Mutation {
        ...
        LogIn(username:String!, password:String!): GenericScalar
        ...
    }
'''

mutation = ariadne.MutationType()
@mutation.field('LogIn')
def resolve_login(obj, info, **kwargs):
    user = authenticate(**kwargs)

    if user is None:
        raise Exception('Please enter a correct username and password')

    if not user.is_active:
        raise Exception('It seems your account has been disabled')

    login(info.context, user)
    return {'token': get_token(user)}
~~~

Verify and refresh token
----------

Add mutations to your GraphQL schema

~~~python
import ariadne
from ariadne_jwt import resolve_verify, resolve_refresh, GenericScalar, jwt_schema

type_defs = '''
    type Mutation {
        ...
        verifyToken(token: String!): VerifyToken
        refreshToken(token: String!): RefreshToken
        ...
    }
    '''
    
mutation = ariadne.MutationType()
    
mutation.set_field('verifyToken', resolve_verify)
mutation.set_field('refreshToken', resolve_refresh)

schema = ariadne.make_executable_schema([type_defs, jwt_schema], [mutation, GenericScalar])
~~~

``verifyToken`` to confirm that the JWT is valid.

~~~graphql
mutation {
    verifyToken(token: "...") {
        payload
    }
}
~~~

``refreshToken`` to obtain a brand new token with renewed expiration time for non-expired tokens.

~~~graphql
mutation {
    refreshToken(token: "...") {
        token
        payload
    }
}
~~~