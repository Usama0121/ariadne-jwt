# Ariadne JWT

JSON Web Token for Ariadne Django

## Installation

~~~shell
pip install ariadne-jwt
~~~

Include the `JSONWebTokenMiddleware` in your *MIDDLEWARE* settings:

~~~python
MIDDLEWARE = [
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'ariadne_jwt.middleware.JSONWebTokenMiddleware',
]
~~~

Include the `JSONWebTokenBackend` in your *AUTHENTICATION_BACKENDS* settings:

~~~python
AUTHENTICATION_BACKENDS = [
    'ariadne_jwt.backends.JSONWebTokenBackend',
    'django.contrib.auth.backends.ModelBackend'
]
~~~

## Schema

Add mutations to your GraphQL schema

~~~python
import ariadne
from ariadne_jwt import resolve_verify, resolve_refresh, resolve_token_auth, jwt_schema, GenericScalar

type_defs = '''
    type Mutation {
        ...
        verifyToken(token: String!): VerifyToken
        refreshToken(token: String!): RefreshToken
        tokenAuth(username: String!, password:String!): TokenAuth
        ...
    }
    '''

mutation = ariadne.MutationType()

mutation.set_field('verifyToken', resolve_verify)
mutation.set_field('refreshToken', resolve_refresh)
mutation.set_field('tokenAuth', resolve_token_auth)

schema = ariadne.make_executable_schema([type_defs, jwt_schema], mutation, GenericScalar)
~~~

- `tokenAuth` to authenticate the user and obtain the JSON Web Token.

The resolver uses User's model `USERNAME_FIELD`_, which by default is ``username``.

~~~graphql
mutation TokenAuth($username: String!, $password: String!) {
    tokenAuth(username: $username, password: $password) {
        token
    }
}
~~~

- `verifyToken` to confirm that the token is valid.

~~~graphql
mutation VerifyToken($token:String!) {
    verifyToken(token: $token) {
        payload
    }
}
~~~

- `refreshToken` to obtain a brand new *token* with renewed expiration time for non-expired tokens.

~~~graphql
mutation RefreshToken($token: String!) {
    refreshToken(token: $token) {
        token
        payload
    }
}
~~~

## Authentication in GraphQL queries

Now in order to access protected API you must include the ``Authorization: JWT <token>`` header. you can use
the ``login_required()`` decorator for your *resolvers*:

~~~python
from ariadne import QueryType
from ariadne_jwt.decorators import login_required

type_defs = '''
type UserNode {
    username:String
    email: String
}
type Query {
    me: UserNode
}
'''

query = QueryType()


@query.field('me')
@login_required
def resolve_viewer(self, info, **kwargs):
    return info.context.get('request').user
~~~

## Customizing

If you want to customize the ``tokenAuth`` behavior, you'll need to extend the ``TokenAuth`` type and write a resolver
with @token_auth decorator.

~~~python
from ariadne_jwt.decorators import token_auth

extended_type_defs = '''
type UserNode {
    id
    username
    email
}
extend type TokenAuth {
    user: UserNode
}
'''


@token_auth
def resolve_token_auth(obj, info, **kwargs):
    return {'user': info.context.get('request').user}
~~~

~~~graphql
mutation TokenAuth($username: String!, $password: String!) {
    tokenAuth(username: $username, password: $password) {
        token
        user {
            id
        }
    }
}
~~~

## Settings

*ariadne-jwt* reads your configuration from a single **Django setting** named ``GRAPHQL_JWT``

~~~python
GRAPHQL_JWT = {
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_EXPIRATION_DELTA': timedelta(seconds=60 * 10)
}
~~~

### Default Settings

~~~python
DEFAULTS = {
    # Algorithm for cryptographic signing
    'JWT_ALGORITHM': 'HS256',

    # Identifies the recipients that the JWT is intended for
    'JWT_AUDIENCE': None,

    # Identifies the principal that issued the JWT
    'JWT_ISSUER': None,

    # Validate an expiration time which is in the past but not very far
    'JWT_LEEWAY': 0,

    # The secret key used to sign the JWT
    'JWT_SECRET_KEY': settings.SECRET_KEY,

    # Secret key verification
    'JWT_VERIFY': True,

    # Expiration time verification
    'JWT_VERIFY_EXPIRATION': False,

    # Timedelta added to utcnow() to set the expiration time
    'JWT_EXPIRATION_DELTA': timedelta(seconds=60 * 5),

    # Enable token refresh
    'JWT_ALLOW_REFRESH': True,

    # Limit on token refresh
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),

    # Enable long time running refresh token
    'JWT_LONG_RUNNING_REFRESH_TOKEN': False,

    # The model to use to represent a refresh token
    'JWT_REFRESH_TOKEN_MODEL': 'refresh_token.RefreshToken',

    # Refresh token number of bytes
    'JWT_REFRESH_TOKEN_N_BYTES': 20,

    # Authorization header name
    'JWT_AUTH_HEADER': 'HTTP_AUTHORIZATION',

    # Authorization prefix
    'JWT_AUTH_HEADER_PREFIX': 'JWT',

    # A custom function *f(payload, context)* to encode the token
    'JWT_ENCODE_HANDLER': 'ariadne_jwt.utils.jwt_encode',

    # A custom function *f(token, context)* to decode the token
    'JWT_DECODE_HANDLER': 'ariadne_jwt.utils.jwt_decode',

    # A custom function *f(user, context)* to generate the token payload
    'JWT_PAYLOAD_HANDLER': 'ariadne_jwt.utils.jwt_payload',

    # A custom function `f(payload)` to obtain the username    
    'JWT_PAYLOAD_GET_USERNAME_HANDLER': (lambda payload: payload.get(get_user_model().USERNAME_FIELD)),

    # A custom function `f(orig_iat, context)` to determine if refresh has expired
    'JWT_REFRESH_EXPIRED_HANDLER': 'ariadne_jwt.utils.refresh_has_expired',
}
~~~

# Writing tests

~~~python
from django.contrib.auth import get_user_model
from ariadne_jwt.testcases import JSONWebTokenTestCase


class UserTests(JSONWebTokenTestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test', password='dolphins')
        self.client.authenticate(self.user)
        self.client.schema(type_defs, resolvers, directives=directives)

    def test_get_user(self):
        query = '''
            query GetUser($username: String) {
                user(username: $username) {
                    id
                }
            }
            '''
        self.client.execute(query, variables={'username': self.user.username})
~~~

# Testing the library

run the following in root directory

~~~shell script
python run_tests.py
~~~