from errata_tool import ErrataConnector


class Variant(ErrataConnector):
    """A Variant contains a "data" dict, for example::
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

    def __init__(self, name, data=None):
        self.name = name
        self.data = data
        self.url = self._url + '/variants/%s' % self.name

    def refresh(self):
        url = '/api/v1/variants/%s' % self.name
        result = self._get(url)
        self.data = result['data']

    def __getattr__(self, name):
        if self.data is None:
            self.refresh()
        return self.data.get(name) or self.data['attributes'][name]

    def __repr__(self):
        return 'Variant(%s)' % self.name

    def __str__(self):
        return self.name
