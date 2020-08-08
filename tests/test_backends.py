from .base import GraphQLJWTTestCase
from ariadne_jwt.backends import JWTBackend
from ariadne_jwt.exceptions import GraphQLJWTError
from ariadne_jwt import settings as ariadne_jwt_settings


class BackendsTests(GraphQLJWTTestCase):

    def test_authenticate(self):
        headers = {
            'HTTP_AUTHORIZATION': '{0} {1}'.format(
                ariadne_jwt_settings.JWT_AUTH_HEADER_PREFIX,
                self.token),
        }

        request = self.factory.get('/', **headers)
        user = JWTBackend().authenticate(request=request)

        self.assertEqual(user, self.user)

    def test_authenticate_fail(self):
        headers = {
            'HTTP_AUTHORIZATION': '{} invalid'.format(
                ariadne_jwt_settings.JWT_AUTH_HEADER_PREFIX),
        }

        request = self.factory.get('/', **headers)

        with self.assertRaises(GraphQLJWTError):
            JWTBackend().authenticate(request=request)

    def test_authenticate_null_request(self):
        user = JWTBackend().authenticate(request=None)
        self.assertIsNone(user)

    def test_authenticate_missing_token(self):
        request = self.factory.get('/')
        user = JWTBackend().authenticate(request=request)

        self.assertIsNone(user)

    def test_get_user(self):
        user = JWTBackend().get_user(self.user.username)
        self.assertEqual(user, self.user)
