import json
from unittest import mock

from django.http import JsonResponse

from ariadne_jwt.middleware import JSONWebTokenMiddleware
from ariadne_jwt.settings import jwt_settings

from .testcases import TestCase


class MiddlewareTests(TestCase):

    def setUp(self):
        super().setUp()

        self.get_response_mock = mock.Mock(return_value=JsonResponse({}))
        self.middleware = JSONWebTokenMiddleware(self.get_response_mock)

    def test_authenticate(self):
        headers = {
            jwt_settings.JWT_AUTH_HEADER: '{0} {1}'.format(
                jwt_settings.JWT_AUTH_HEADER_PREFIX,
                self.token),
        }

        request = self.request_factory.get('/', **headers)
        self.middleware(request)

        self.get_response_mock.assert_called_once_with(request)

    @mock.patch('ariadne_jwt.middleware.authenticate', return_value=None)
    def test_user_not_authenticate(self, *args):
        headers = {
            jwt_settings.JWT_AUTH_HEADER: '{0} {1}'.format(
                jwt_settings.JWT_AUTH_HEADER_PREFIX,
                self.token),
        }

        request = self.request_factory.get('/', **headers)
        self.middleware(request)

        self.get_response_mock.assert_called_once_with(request)

    def test_graphql_error(self):
        headers = {
            jwt_settings.JWT_AUTH_HEADER: '{} invalid'.format(
                jwt_settings.JWT_AUTH_HEADER_PREFIX),
        }

        request = self.request_factory.get('/', **headers)
        response = self.middleware(request)
        content = json.loads(response.content.decode('utf-8'))

        self.assertTrue(content['errors'])
        self.get_response_mock.assert_not_called()

    def test_header_not_found(self):
        request = self.request_factory.get('/')
        self.middleware(request)

        self.get_response_mock.assert_called_once_with(request)

    def test_user_is_authenticated(self):
        headers = {
            jwt_settings.JWT_AUTH_HEADER: '{0} {1}'.format(
                jwt_settings.JWT_AUTH_HEADER_PREFIX,
                self.token),
        }

        request = self.request_factory.get('/', **headers)
        request.user = self.user
        self.middleware(request)

        self.get_response_mock.assert_called_once_with(request)
