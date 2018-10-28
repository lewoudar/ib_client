import pytest


@pytest.fixture(scope='session')
def api_schema():
    return {
        "requested_version": "2.9",
        "supported_objects": ["ipv4address", "ipv6address", "ipv6network",
                              "ipv6networkcontainer", "ipv6range",
                              "macfilteraddress", "network"],
        "supported_versions": ["1.0", "1.1", "1.2", "1.2.1", '2.0'],
        "schema_version": "2.0",
    }
