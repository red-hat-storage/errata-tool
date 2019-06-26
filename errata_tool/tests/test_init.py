import errata_tool
from errata_tool import ErrataConnector, security


class TestInit(object):
    def test_init(self):
        assert errata_tool


class TestSecurity(object):
    def test_ssl_default(self):
        """Ensure that we verify SSL by default. """
        assert security.security_settings.ssl_verify()


class TestErratum(object):
    def test_ssl_default(self):
        """Ensure that we verify SSL by default. """
        e = ErrataConnector()
        assert e.ssl_verify
