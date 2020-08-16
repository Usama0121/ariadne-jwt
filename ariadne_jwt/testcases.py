from django.contrib.auth import authenticate
from django.core.handlers.wsgi import WSGIRequest
from django.test import Client, RequestFactory, testcases

import ariadne
from graphql import ExecutionResult

from .settings import jwt_settings
from .shortcuts import get_token


class SchemaRequestFactory(RequestFactory):

    def execute(self, context, query, variables):
        response = ariadne.graphql_sync(self._schema, {'query': query, 'variables': variables}, context_value=context)
        response = ExecutionResult(response[1].get('data'), response[1].get('errors'))
        return response


class JSONWebTokenClient(SchemaRequestFactory, Client):

    def __init__(self, **defaults):
        super(JSONWebTokenClient, self).__init__(**defaults)
        self._credentials = {}
        self._schema = None

    def request(self, **request):
        request = WSGIRequest(self._base_environ(**request))
        request.user = authenticate(request)
        return request

    def schema(self, type_defs, *resolvers, directives=None):
        self._schema = ariadne.make_executable_schema(type_defs, *resolvers, directives=directives)

    def credentials(self, **kwargs):
        self._credentials = kwargs

    def execute(self, query, variables=None, **extra):
        if variables is None:
            variables = {}
        extra.update(self._credentials)
        variables.update(extra)
        context = {'request': self.post('/', **extra)}
        return super(JSONWebTokenClient, self).execute(context, query, variables)

    def authenticate(self, user):
        self._credentials = {
            jwt_settings.JWT_AUTH_HEADER: '{0} {1}'.format(
                jwt_settings.JWT_AUTH_HEADER_PREFIX,
                get_token(user)),
        }

    def logout(self):
        self._credentials.pop(jwt_settings.JWT_AUTH_HEADER, None)


class JSONWebTokenTestCase(testcases.TestCase):
    client_class = JSONWebTokenClient
