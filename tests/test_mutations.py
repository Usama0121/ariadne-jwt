from datetime import datetime, timedelta
from unittest.mock import patch

from ariadne_jwt import settings
from ariadne_jwt.shortcuts import get_token
from ariadne_jwt.utils import get_payload

from .base import GraphQLJWTTestCase
from .decorators import override_settings


class MutationsTests(GraphQLJWTTestCase):

    def test_verify(self):
        query = '''
        mutation VerifyToken($token: String!) {
            verifyToken(token: $token) {
                payload
            }
        }
        '''
        response = self.client.execute(query, token=self.token)
        payload = response.data['verifyToken']['payload']

        self.assertEqual(self.user.username, payload['username'])

    def test_verify_invalid_token(self):
        query = '''
        mutation VerifyToken($token: String!) {
            verifyToken(token: $token) {
                payload
            }
        }
        '''

        response = self.client.execute(query, token='invalid')
        self.assertTrue(response.errors)

    def test_refresh(self):
        query = '''
        mutation RefreshToken($token: String!) {
            refreshToken(token: $token) {
                token
                payload
            }
        }
        '''

        with patch('ariadne_jwt.utils.datetime') as datetime_mock:
            datetime_mock.utcnow.return_value = datetime.utcnow() + timedelta(seconds=1)
            response = self.client.execute(query, token=self.token)

        data = response.data['refreshToken']
        token = data['token']
        payload = get_payload(token)

        self.assertNotEqual(self.token, token)
        self.assertEqual(self.user.username, data['payload']['username'])
        self.assertEqual(self.payload['orig_iat'], payload['orig_iat'])

    def test_refresh_expired(self):
        query = '''
        mutation RefreshToken($token: String!) {
            refreshToken(token: $token) {
                token
                payload
            }
        }
        '''

        with patch('ariadne_jwt.mutations.datetime') as datetime_mock:
            datetime_mock.utcnow.return_value = (datetime.utcnow() +
                                                 settings.JWT_REFRESH_EXPIRATION_DELTA +
                                                 timedelta(seconds=1))

            response = self.client.execute(query, token=self.token)

        self.assertTrue(response.errors)

    @override_settings(JWT_ALLOW_REFRESH=False)
    def test_refresh_error(self, *args):
        token = get_token(self.user)

        query = '''
        mutation RefreshToken($token: String!) {
            refreshToken(token: $token) {
                token
                payload
            }
        }
        '''

        response = self.client.execute(query, token=token)
        self.assertTrue(response.errors)
