from unittest.mock import MagicMock

from promise import Promise, is_thenable

from ariadne_jwt import decorators

from .testcases import UserTestCase


class DecoratorsTests(UserTestCase):

    def test_token_auth(self, *args):
        @decorators.token_auth
        def wrapped(root, info, **kwargs):
            return Promise()

        mock = MagicMock()

        result = wrapped(mock, mock, password='dolphins', username=self.user.get_username())

        self.assertTrue(is_thenable(result))
