from unittest import mock
from django.contrib.auth import models

from ariadne_jwt import decorators, exceptions
from ariadne_jwt.settings import jwt_settings

from .testcases import TestCase


class DecoratorsTestCase(TestCase):

    def info(self, user, **kwargs):
        request = self.request_factory.post('/', **kwargs)
        request.user = user
        return mock.Mock(context={'request': request})


class UserPassesTests(DecoratorsTestCase):

    def test_user_passes_test(self):
        @decorators.user_passes_test(lambda u: u.pk == self.user.pk)
        def wrapped(info):
            """Decorated function"""

        result = wrapped(self.info(self.user))
        self.assertIsNone(result)

    def test_permission_denied(self):
        @decorators.user_passes_test(lambda u: u.pk == self.user.pk + 1)
        def wrapped(info):
            """Decorated function"""

        with self.assertRaises(exceptions.PermissionDenied):
            wrapped(self.info(self.user))


class LoginRequiredTests(DecoratorsTestCase):

    def test_login_required(self):
        @decorators.login_required
        def wrapped(info):
            """Decorated function"""

        result = wrapped(self.info(self.user))
        self.assertIsNone(result)

    def test_permission_denied(self):
        @decorators.login_required
        def wrapped(info):
            """Decorated function"""

        with self.assertRaises(exceptions.PermissionDenied):
            wrapped(self.info(models.AnonymousUser()))


class StaffMemberRequiredTests(DecoratorsTestCase):

    def test_staff_member_required(self):
        @decorators.staff_member_required
        def wrapped(info):
            """Decorated function"""

        self.user.is_staff = True
        result = wrapped(self.info(self.user))

        self.assertIsNone(result)

    def test_permission_denied(self):
        @decorators.staff_member_required
        def wrapped(info):
            """Decorated function"""

        with self.assertRaises(exceptions.PermissionDenied):
            wrapped(self.info(self.user))


class PermissionRequiredTests(DecoratorsTestCase):

    def test_permission_required(self):
        @decorators.permission_required('auth.add_user')
        def wrapped(info):
            """Decorated function"""

        perm = models.Permission.objects.get(codename='add_user')
        self.user.user_permissions.add(perm)

        result = wrapped(self.info(self.user))
        self.assertIsNone(result)

    def test_permission_denied(self):
        @decorators.permission_required(['auth.add_user', 'auth.change_user'])
        def wrapped(info):
            """Decorated function"""

        with self.assertRaises(exceptions.PermissionDenied):
            wrapped(self.info(self.user))


class TokenAuthTests(DecoratorsTestCase):

    def test_already_authenticated(self):
        @decorators.token_auth
        def wrapped(root, info, **kwargs):
            return {}

        headers = {
            jwt_settings.JWT_AUTH_HEADER: '{0} {1}'.format(
                jwt_settings.JWT_AUTH_HEADER_PREFIX,
                self.token),
        }
        info_mock = self.info(models.AnonymousUser(), **headers)
        result = wrapped(None, info_mock, password='dolphins', username=self.user.get_username())

        self.assertNotIn(jwt_settings.JWT_AUTH_HEADER, info_mock.context.get('request').META)
