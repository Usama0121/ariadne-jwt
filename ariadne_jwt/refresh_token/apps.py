from django.apps import AppConfig
try:
    from django.utils.translation import ugettext as _
except ImportError:
    from django.utils.translation import gettext as _


class RefreshTokenConfig(AppConfig):
    name = 'ariadne_jwt.refresh_token'
    verbose_name = _('Refresh token')
