from unittest import mock
from django.contrib.auth import get_user_model
from django.test import RequestFactory, testcases

from ariadne import MutationType

from ariadne_jwt.testcases import JSONWebTokenTestCase
from ariadne_jwt.utils import jwt_payload, jwt_encode
from ariadne_jwt import (GenericScalar, jwt_schema, resolve_verify, resolve_refresh, resolve_revoke, resolve_token_auth)


class UserTestCase(testcases.TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test', password='dolphins')


class TestCase(UserTestCase):

    def setUp(self):
        super().setUp()
        self.payload = jwt_payload(self.user)
        self.token = jwt_encode(self.payload)
        self.request_factory = RequestFactory()

    def info(self, user, **kwargs):
        request = self.request_factory.post('/', **kwargs)
        request.user = user
        return mock.Mock(context={'request': request})


class SchemaTestCase(TestCase, JSONWebTokenTestCase):
    type_defs = '''
                 type Query {
                    test_query: GenericScalar
                 }
                 type Mutation {
                    verifyToken(token: String!): VerifyToken
                    refreshToken(token: String!): RefreshToken
                    tokenAuth(username: String!, password:String!): TokenAuth
                    revokeToken(refresh_token: String!): RevokeToken
                 }
                 ''' + jwt_schema

    def setUp(self):
        super().setUp()
        mutation = MutationType()
        mutation.set_field('refreshToken', resolve_refresh)
        mutation.set_field('verifyToken', resolve_verify)
        mutation.set_field('tokenAuth', resolve_token_auth)
        mutation.set_field('revokeToken', resolve_revoke)
        self.client.schema(self.type_defs, mutation, GenericScalar)
