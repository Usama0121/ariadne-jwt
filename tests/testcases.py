from unittest import mock

from django.contrib.auth import get_user_model
from django.core.handlers.wsgi import WSGIRequest
from django.test import Client, RequestFactory, TestCase

from ariadne import make_executable_schema, MutationType
from graphql import graphql_sync

from ariadne_jwt import (GenericScalar, jwt_schema, resolve_verify, resolve_refresh, resolve_token_auth)
from ariadne_jwt.settings import env
from ariadne_jwt.utils import jwt_payload, jwt_encode


class GraphQLRequestFactory(RequestFactory):

    def execute(self, query, **kwargs):
        return graphql_sync(self._schema, query, variable_values=kwargs, context_value=mock.MagicMock())


class GraphQLClient(GraphQLRequestFactory, Client):

    def __init__(self, **defaults):
        super().__init__(**defaults)
        self._schema = None

    def schema(self, **kwargs):
        self._schema = make_executable_schema(kwargs.get('type_defs'), kwargs.get('resolvers'))


class UserTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test', password='dolphins')


class GraphQLJWTTestCase(UserTestCase):

    def setUp(self):
        super().setUp()
        self.payload = jwt_payload(self.user)
        self.token = jwt_encode(self.payload)
        self.factory = RequestFactory()


class GraphQLSchemaTestCase(GraphQLJWTTestCase):
    client_class = GraphQLClient

    type_defs = '''
                 type Query {
                    test_query: GenericScalar
                 }
                 type Mutation {
                    verifyToken(token: String!): VerifyToken
                    refreshToken(token: String!): RefreshToken
                    tokenAuth(username: String!, password:String!): TokenAuth
                 }
                 ''' + jwt_schema

    def setUp(self):
        super().setUp()
        mutation = MutationType()
        mutation.set_field('refreshToken', resolve_refresh)
        mutation.set_field('verifyToken', resolve_verify)
        mutation.set_field('tokenAuth', resolve_token_auth)
        self.client.schema(type_defs=self.type_defs, resolvers=[mutation, GenericScalar])
