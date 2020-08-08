from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase

from ariadne_jwt.utils import jwt_payload, jwt_encode

from .schema import schema
from graphql import graphql_sync


class GraphQLRequestFactory(RequestFactory):

    def execute(self, query, **kwargs):
        return graphql_sync(self.schema, query, variable_values=kwargs)


class GraphQLClient(GraphQLRequestFactory, Client):

    def __init__(self, **defaults):
        super().__init__(**defaults)
        self.schema = schema


class GraphQLJWTTestCase(TestCase):
    client_class = GraphQLClient

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test')
        self.payload = jwt_payload(self.user)
        self.token = jwt_encode(self.payload)
        self.factory = RequestFactory()
