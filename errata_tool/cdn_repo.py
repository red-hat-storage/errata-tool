from errata_tool import ErrataConnector


class CdnRepo(ErrataConnector):
    """A CdnRepo contains a dict, for example:
    {
        'id': 12189,
        'relationships': {
            'arch': {
                'id': 28,
                'name': 'multi'
            },
            'packages': [
                {
                    'cdn_repo_package_tags': [
                        {
                            'id': 16054,
                            'tag_template': '{{version}}-{{release}}'
                        }, {
                            'id': 16055,
                            'tag_template': '{{version}}'
                        }, {
                            'id': 19195,
                            'tag_template': 'v{{version(2)}}'
                        }
                    ],
                    'id': 49826,
                    'name': 'work-container'
                }
            ],
            'variants': [
                {
                    'id': 3072,
                    'name': '8Base-RHACM-2.0'
                }, {
                    'id': 3159,
                    'name': '8Base-RHACM-2.1'
                }, {
                    'id': 3284,
                    'name': '8Base-RHACM-2.2'
                }, {
                    'id': 3421,
                    'name': '8Base-RHACM-2.3'
                }
            ]
        },
        'type': 'cdn_repos'
    }
    """

    def __init__(self, name, data=None):
        self.name = name
        self.data = data

    def refresh(self):
        url = '/api/v1/cdn_repos/%s' % self.name
        result = self._get(url)
        self.data = result['data']

    def render(self):
        output = {
            'name': str(self.name),
            'arch': str(self.relationships['arch']['name']),
            'release_type': str(self.release_type),
            'content_type':  str(self.content_type),
            'use_for_tps': self.use_for_tps,
            'variants': [
                str(variant['name'])
                for variant in self.relationships['variants']
            ],
        }
        if 'packages' in self.relationships:
            packages = {}
            for package in self.relationships['packages']:
                package_name = str(package['name'])
                packages[package_name] = sorted(
                    str(tag['tag_template'])
                    for tag in package['cdn_repo_package_tags']
                )
            output['packages'] = packages

        return output

    def __getattr__(self, name):
        if self.data is None:
            self.refresh()
        return self.data.get(name) or self.data['attributes'][name]

    def __repr__(self):
        return 'CdnRepo(%s)' % self.name

    def __str__(self):
        return self.name
