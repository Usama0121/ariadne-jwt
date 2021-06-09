from django.contrib.auth import get_user_model

from ariadne_jwt import jwt_schema, GenericScalar
from ariadne_jwt.testcases import JSONWebTokenTestCase
from project_1.schema import root_type_defs, user_type_defs
from user.mutations import mutation
from user.queries import query


class UserTests(JSONWebTokenTestCase):
    def setUp(self):
        self.username = 'test'
        self.password = 'dolphins'
        self.user = get_user_model().objects.create_user(
            username=self.username,
            password=self.password)
        self.client.schema([root_type_defs, user_type_defs, jwt_schema],
                           [query, mutation, GenericScalar])

    def test_user_is_authenticated(self):
        self.client.authenticate(self.user)
        query = '''
            query {
                me {
                    username
                }
            }
            '''
        res = self.client.execute(query)
        self.assertIsNone(res.errors)
        self.assertEqual(res.data.get('me', {}).get('username'),
                         self.user.username)

    def test_token_auth_mutation(self):
        query = '''
            mutation($username: String!, $password: String!) {
                tokenAuth(username: $username, password: $password) {
                    token
                    user {
                        username
                    }
                }
            }
        '''
        res = self.client.execute(query, variables={'username': self.username,
                                                    'password': self.password})
        self.assertIsNone(res.errors)
        token_auth = res.data.get('tokenAuth')
        self.assertIsNotNone(token_auth)
        token = token_auth.get('token')
        self.assertIsNotNone(token)
        username = token_auth.get('user', {}).get('username')
        self.assertEqual(self.username, username)
