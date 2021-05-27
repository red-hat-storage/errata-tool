from errata_tool import ErrataConnector
from errata_tool.variant import Variant

class ProductVersion(ErrataConnector):
    def __init__(self, id_or_name):
        """Find a Product Version in the ET database.

        :param id_or_name: This can be an id number (int) or product version
                           name (str), for example "RHEL-7-CEPH-3".
        """
        url = '/product_versions/%s.json' % id_or_name
        self.data = self._get(url)

    def releasedBuilds(self):
        """Get the list of released builds for this Product Version.

        :returns: a (possibly-empty) list of dicts. Each dict represents a
                  build, for example::

                    {'build': u'ceph-12.2.5-42.el7cp',
                     'created_at': '2018-09-26T18:17:33Z',
                     'errata_id': 33840,
                     'updated_at': '2018-09-26T18:17:33Z'},
        """
        url = '/api/v1/product_versions/%d/released_builds' % self.id
        result = self._get(url)
        return result

    def variants(self):
        """Get the list of variants for this Product Version.

        :returns: a (possibly-empty) list of Variant objects.
        """
        url = '/api/v1/variants?filter[product_version_id]=%s' % self.id
        result = self._get(url)['data']
        variants = []
        for variant in result:
            variant_name = variant['attributes']['name']
            variants.append(Variant(name=variant_name, data=variant))
        return variants

    def __getattr__(self, name):
        return self.data[name]

    def __repr__(self):
        return 'ProductVersion(%s)' % self.id

    def __str__(self):
        return self.name
