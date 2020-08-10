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

schema = ariadne.make_executable_schema([type_defs, jwt_schema], [mutation, GenericScalar])
~~~


``tokenAuth`` to authenticate the user and obtain the JSON Web Token.

The resolver uses User's model `USERNAME_FIELD`_, which by default is ``username``.

~~~graphql
mutation TokenAuth($username: String!, $password: String!) {
    tokenAuth(username: $username, password: $password) {
        token
    }
}
~~~


``verifyToken`` to confirm that the token is valid.

~~~graphql
mutation VerifyToken($token:String!) {
    verifyToken(token: $token) {
        payload
    }
}
~~~

``refreshToken`` to obtain a brand new token with renewed expiration time for non-expired tokens.

~~~graphql
mutation RefreshToken($token: String!) {
    refreshToken(token: $token) {
        token
        payload
    }
}
~~~