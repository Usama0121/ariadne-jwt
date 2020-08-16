from contextlib import contextmanager
from datetime import datetime, timedelta
from unittest import mock

from ariadne_jwt.settings import jwt_settings


@contextmanager
def catch_signal(signal):
    handler = mock.Mock()
    signal.connect(handler)
    yield handler
    signal.disconnect(handler)


@contextmanager
def back_to_the_future(**kwargs):
    with mock.patch('ariadne_jwt.utils.datetime') as datetime_mock:
        datetime_mock.utcnow.return_value = datetime.utcnow() + timedelta(**kwargs)
        yield datetime_mock


def refresh_expired():
    expires = jwt_settings.JWT_REFRESH_EXPIRATION_DELTA.total_seconds()
    return back_to_the_future(seconds=1 + expires)
