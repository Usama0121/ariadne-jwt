from ariadne_jwt.utils import get_payload
from ariadne_jwt.shortcuts import create_refresh_token, get_refresh_token

from ..testcases import SchemaTestCase
from ..decorators import override_jwt_settings
from ..test_mutations import back_to_the_future, refresh_expired


class TokenAuthTests(SchemaTestCase):
    @override_jwt_settings(JWT_LONG_RUNNING_REFRESH_TOKEN=True)
    def setUp(self):
        self.query = '''
        mutation TokenAuth($username: String!, $password: String!) {
            tokenAuth(username: $username, password: $password) {
                token
                refresh_token
            }
        }
        '''
        super().setUp()

    @override_jwt_settings(JWT_LONG_RUNNING_REFRESH_TOKEN=True)
    def test_token_auth(self):
        response = self.client.execute(self.query, {
            self.user.USERNAME_FIELD: self.user.get_username(),
            'password': 'dolphins',
        })
        data = response.data['tokenAuth']
        payload = get_payload(data['token'])
        refresh_token = get_refresh_token(data['refresh_token'])
        self.assertEqual(self.user.get_username(), payload[self.user.USERNAME_FIELD])
        self.assertEqual(refresh_token.user, self.user)


class RefreshTests(SchemaTestCase):
    @override_jwt_settings(JWT_LONG_RUNNING_REFRESH_TOKEN=True)
    def setUp(self):
        self.query = '''
        mutation RefreshToken($refreshToken: String!) {
            refreshToken(token: $refreshToken) {
                token
                refresh_token
                payload
            }
        }
        '''
        super().setUp()
        self.refresh_token = create_refresh_token(self.user)

    @override_jwt_settings(JWT_LONG_RUNNING_REFRESH_TOKEN=True)
    def test_refresh_token(self):
        with back_to_the_future(seconds=1):
            response = self.client.execute(self.query, {'refreshToken': self.refresh_token.token})

        data = response.data['refreshToken']
        token = data['token']
        refresh_token = get_refresh_token(data['refresh_token'])
        payload = get_payload(token)

        self.assertNotEqual(token, self.token)
        self.assertGreater(payload['exp'], self.payload['exp'])

        self.assertNotEqual(refresh_token.token, self.refresh_token.token)
        self.assertEqual(refresh_token.user, self.user)
        self.assertGreater(refresh_token.created, self.refresh_token.created)

    def test_refresh_token_expired(self):
        with refresh_expired():
            response = self.client.execute(self.query, {'refreshToken': self.refresh_token.token})

        self.assertIsNotNone(response.errors)


class RevokeTests(SchemaTestCase):
    @override_jwt_settings(JWT_LONG_RUNNING_REFRESH_TOKEN=True)
    def setUp(self):
        self.query = '''
        mutation RevokeToken($refreshToken: String!) {
            revokeToken(refresh_token: $refreshToken) {
                revoked
            }
        }
        '''
        super().setUp()
        self.refresh_token = create_refresh_token(self.user)

    @override_jwt_settings(JWT_LONG_RUNNING_REFRESH_TOKEN=True)
    def test_revoke(self):
        response = self.client.execute(self.query, {
            'refreshToken': self.refresh_token.token,
        })

        self.refresh_token.refresh_from_db()
        self.assertIsNotNone(self.refresh_token.revoked)
        self.assertIsNotNone(response.data['revokeToken']['revoked'])
