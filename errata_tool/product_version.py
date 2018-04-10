from errata_tool import ErrataConnector


class ProductVersion(ErrataConnector):
    def __init__(self, id_or_name):
        """
        Find a Product Version in the ET database.

        :param id_or_name: This can be an id number (int) or product version
                           name (str), for example "RHEL-7-CEPH-3".
        """
        url = '/product_versions/%s.json' % id_or_name
        self.data = self._get(url)

    def __getattr__(self, name):
        return self.data[name]

    def __repr__(self):
        return 'ProductVersion(%s)' % self.id

    def __str__(self):
        return self.name
