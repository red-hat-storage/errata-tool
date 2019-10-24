from errata_tool import ErrataConnector


class User(ErrataConnector):
    def __init__(self, id_or_login_name):
        """Find a user in the ET database.

        :param id_or_login_name: This can be an id number (int) or login name
                                 (str). The user's login name should be passed
                                 without "@redhat.com", eg. "anharris".
        """
        url = self._url + '/api/v1/user/%s' % id_or_login_name
        self.data = self._get(url)

    def __getattr__(self, name):
        return self.data[name]

    def __repr__(self):
        return 'User(%s)' % self.id

    def __str__(self):
        return self.login_name
