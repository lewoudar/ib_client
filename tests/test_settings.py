import pytest

# noinspection PyProtectedMember
from infoblox import _settings


@pytest.mark.parametrize(('setting_name', 'setting_type'), [
    ('DEFAULT_CONNECT_TIMEOUT', float),
    ('DEFAULT_READ_TIMEOUT', float),
    ('DEFAULT_MAX_RETRIES', int),
    ('DEFAULT_BACKOFF_FACTOR', float)
])
def test_settings_presence_and_type(setting_name, setting_type):
    assert hasattr(_settings, setting_name)
    assert isinstance(getattr(_settings, setting_name), setting_type)
