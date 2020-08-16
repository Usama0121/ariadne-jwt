from datetime import datetime, timedelta
from unittest.mock import patch

from ariadne_jwt.settings import jwt_settings
from ariadne_jwt.shortcuts import get_token
from ariadne_jwt.utils import get_payload

from .testcases import SchemaTestCase
from .decorators import override_jwt_settings


class TokenAuthTests(SchemaTestCase):
    def setUp(self):
        self.query = '''
        mutation TokenAuth($username: String!, $password: String!) {
            tokenAuth(username: $username, password: $password) {
                token
            }
        }
        '''
        super().setUp()

    def test_token_auth(self):
        response = self.client.execute(self.query, {
            'username': self.user.get_username(),
            'password': 'dolphins',
        })

        payload = get_payload(response.data['tokenAuth']['token'])
        self.assertEqual(self.user.get_username(), payload['username'])

    def test_token_auth_invalid_credentials(self):
        response = self.client.execute(self.query, {
            'username': self.user.get_username(),
            'password': 'wrong',
        })

        self.assertTrue(response.errors)


class VerifyTokenTests(SchemaTestCase):

    def setUp(self):
        self.query = '''
        mutation VerifyToken($token: String!) {
            verifyToken(token: $token) {
                payload
            }
        }
        '''
        super().setUp()

    def test_verify(self):
        response = self.client.execute(self.query, token=self.token)
        payload = response.data['verifyToken']['payload']
        self.assertEqual(self.user.get_username(), payload['username'])

    def test_verify_invalid_token(self):
        response = self.client.execute(self.query, token='invalid')
        self.assertTrue(response.errors)


class RefreshTokenTests(SchemaTestCase):
    def setUp(self):
        self.query = '''
        mutation RefreshToken($token: String!) {
            refreshToken(token: $token) {
                token
                payload
            }
        }
        '''
        super().setUp()

    def test_refresh(self):
        with patch('ariadne_jwt.utils.datetime') as datetime_mock:
            datetime_mock.utcnow.return_value = datetime.utcnow() + timedelta(seconds=1)
            response = self.client.execute(self.query, token=self.token)

        data = response.data['refreshToken']
        token = data['token']
        payload = get_payload(token)

        self.assertNotEqual(self.token, token)
        self.assertEqual(self.user.get_username(), data['payload']['username'])
        self.assertEqual(self.payload['orig_iat'], payload['orig_iat'])

    def test_refresh_expired(self):
        with patch('ariadne_jwt.mutations.datetime') as datetime_mock:
            datetime_mock.utcnow.return_value = (datetime.utcnow() +
                                                 jwt_settings.JWT_REFRESH_EXPIRATION_DELTA +
                                                 timedelta(seconds=1))

            response = self.client.execute(self.query, token=self.token)

        self.assertTrue(response.errors)

    @override_jwt_settings(JWT_ALLOW_REFRESH=False)
    def test_refresh_error(self, *args):
        token = get_token(self.user)
        response = self.client.execute(self.query, token=token)
        self.assertTrue(response.errors)
