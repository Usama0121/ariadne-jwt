from ariadne_jwt.settings import jwt_settings
from ariadne_jwt.exceptions import JSONWebTokenError
from ariadne_jwt.backends import JSONWebTokenBackend

from .testcases import TestCase


class BackendsTests(TestCase):

    def setUp(self):
        super(BackendsTests, self).setUp()
        self.backend = JSONWebTokenBackend()

    def test_authenticate(self):
        headers = {
            jwt_settings.JWT_AUTH_HEADER: '{0} {1}'.format(
                jwt_settings.JWT_AUTH_HEADER_PREFIX,
                self.token),
        }

        request = self.factory.get('/', **headers)
        user = self.backend.authenticate(request=request)

        self.assertEqual(user, self.user)

    def test_authenticate_fail(self):
        headers = {
            jwt_settings.JWT_AUTH_HEADER: '{} invalid'.format(
                jwt_settings.JWT_AUTH_HEADER_PREFIX),
        }

        request = self.factory.get('/', **headers)

        with self.assertRaises(JSONWebTokenError):
            self.backend.authenticate(request=request)

    def test_authenticate_null_request(self):
        user = self.backend.authenticate(request=None)
        self.assertIsNone(user)

    def test_authenticate_missing_token(self):
        request = self.factory.get('/')
        user = self.backend.authenticate(request=request)

        self.assertIsNone(user)

    def test_get_user(self):
        user = self.backend.get_user(self.user.get_username())
        self.assertEqual(user, self.user)
