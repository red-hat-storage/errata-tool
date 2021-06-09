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

        :returns: a (possibly-empty) list of Variant objects. Each Variant
                  contains a dict, for example::

                    {
                        'attributes': {
                            'buildroot': False,
                            'cpe': 'cpe:/a:redhat:ceph_storage:1.2::el7',
                            'description': 'Red Hat Ceph Storage Calamari 1.2',
                            'enabled': True,
                            'name': '7Server-RH7-CEPH-CALAMARI-1.2',
                            'override_ftp_base_folder': None,
                            'relationships': {
                                'product': {
                                    'id': 104,
                                    'name': 'Red Hat Ceph Storage',
                                    'short_name': 'RHCEPH'
                                },
                                'product_version': {
                                    'id': 392,
                                    'name': 'RHEL-7-CEPH-1.2'
                                },
                                'push_targets': [
                                    {
                                        'id': 7,
                                        'name': 'cdn_stage'
                                    }, {
                                        'id': 10,
                                        'name': 'cdn_docker_stage'
                                    }, {
                                        'id': 9,
                                        'name': 'cdn_docker'
                                    }, {
                                        'id': 4,
                                        'name': 'cdn'
                                    }
                                ],
                                'rhel_release': {
                                    'id': 87,
                                    'name': 'RHEL-8'
                                },
                                'rhel_variant': {
                                    'id': 2235,
                                    'name': '8Base'
                                }
                            },
                            'tps_stream': 'RHEL-7-Main-Server'
                        },
                        'id': 3085,
                        'type': 'variants'
                    }

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
