from errata_tool import ErrataConnector
from errata_tool.variant import Variant

class ProductVersion(ErrataConnector):
    def __init__(self, id_or_name, data=None):
        """Find a Product Version in the ET database.

        :param id_or_name: This can be an id number (int) or product version
                           name (str), for example "RHEL-7-CEPH-3".
        """

        self.id_or_name = id_or_name
        self.data = data
        self.url = self._url + '/product_versions/%s' % self.id_or_name

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

    def render(self):
        sig_key = str(self.relationships['sig_key']['name'])
        rhel_release = str(self.relationships['rhel_release']['name'])
        brew_tags = [str(tag) for tag in (self.data.get('brew_tags') or [])]
        return {
            'name': str(self.name),
            'description': str(self.description),
            'enabled': self.enabled,
            'default_brew_tag': str(self.default_brew_tag),
            'sig_key_name': sig_key,
            'rhel_release_name': rhel_release,
            'brew_tags': brew_tags,
            'is_server_only': self.is_server_only,
            'push_targets': [
                str(target['name'])
                for target in self.relationships['push_targets']
            ],
            'variants': [
                variant.render()
                for variant in self.variants()
            ],
        }

    def refresh(self):
        # The v1 API doesn't support retrieving a product version directly,
        # so an additional request is made to retrieve the product that it
        # falls under.
        legacy_url = '/product_versions/%s.json' % self.id_or_name
        result = self._get(legacy_url)
        product_id = result['product']['id']
        product_version_id = result['id']
        new_url = '/api/v1/products/%s/product_versions/%s' \
            % (product_id, product_version_id)
        self.data = self._get(new_url)['data']

    def __getattr__(self, name):
        if self.data is None:
            self.refresh()
        return self.data.get(name) or self.data['attributes'][name]

    def __repr__(self):
        return 'ProductVersion(%s)' % self.id

    def __str__(self):
        return self.name
