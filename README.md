# Ariadne JWT

JSON Web Token for Ariadne Django


## Installation
~~~shell script
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

schema = ariadne.make_executable_schema([type_defs, jwt_schema], [mutation, GenericScalar])
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

Now in order to access protected API you must include the ``Authorization: JWT <token>`` header.
you can use the ``login_required()`` decorator for your *resolvers*:

~~~python
from ariadne import QueryType
from ariadne_jwt.decorators import login_required
type_defs='''
type UserNode {
    username:String
    email: String
}
type Query {
    me: UserNode
}
'''
query=QueryType()
@query.field('me')
@login_required
def resolve_viewer(self, info, **kwargs):
    return info.context.get('request').user
~~~

## Customizing

If you want to customize the ``tokenAuth`` behavior, you'll need to extend the ``TokenAuth`` type and write a resolver with @token_auth decorator.

~~~python
from ariadne_jwt.decorators import token_auth
extended_type_defs='''
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
    return { 'user':info.context.get('request').user }
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