import warnings
import urllib3  # NOQA
import urllib3.exceptions as exceptions  # NOQA


class SecurityParameters():
    _warnings_disabled = False
    _verify_ssl = True

    def __init__(self):
        if self._warnings_disabled is False and self._verify_ssl is False:
            self._warnings_disabled = True
            warnings.simplefilter('default')
            # urllib3.disable_warnings()
            # urllib3.disable_warnings(category=exceptions.SecurityWarning)
            # urllib3.disable_warnings(category=exceptions.InsecureRequestWarning)
            warnings.filterwarnings('ignore')

    def __str__(self):
        return "SSL Warnings: " + str(not self._warnings_disabled) + \
               "  Verify SSL: " + str(self._verify_ssl)

    def ssl_verify(self):
        return self._verify_ssl

security_settings = SecurityParameters()
