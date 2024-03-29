from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RefreshTokenConfig(AppConfig):
    name = 'ariadne_jwt.refresh_token'
    verbose_name = _('Refresh token')
