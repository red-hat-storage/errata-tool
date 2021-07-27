import errata_tool
from errata_tool import ErrataConnector
from errata_tool.product_version import ProductVersion


class Product(ErrataConnector):
    def __init__(self, name):
        self.name = name
        self.data = None
        self.url = self._url + '/products/%s' % self.name

    def product_versions(self):
        """Get the list of product version for this Product.

        :returns: a (possibly-empty) list of ProductVersion objects.
        """
        url = '/api/v1/products/%s/product_versions' % self.name
        result = self._get(url)['data']
        product_versions = []
        for product_version in result:
            product_version_id = product_version['id']
            product_versions.append(
                ProductVersion(
                    id_or_name=product_version_id,
                    data=product_version
                )
            )
        return product_versions

    def refresh(self):
        url = '/api/v1/products/' + self.name
        result = self._get(url)
        self.data = result['data']

    def render(self):
        default_docs_reviewer = self.relationships['default_docs_reviewer']
        if default_docs_reviewer:
            reviewer = str(default_docs_reviewer['login_name'])
        else:
            reviewer = None
        rule_set = str(self.relationships['state_machine_rule_set']['name'])
        return {
            'name': str(self.data['attributes']['name']),
            'short_name': str(self.short_name),
            'bugzilla_product_name': str(self.bugzilla_product_name),
            'description': str(self.description),
            'valid_bug_states': [
                str(state)
                for state in self.valid_bug_states
            ],
            'default_docs_reviewer': reviewer,
            'ftp_subdir': str(self.ftp_subdir),
            'move_bugs_on_qe': self.move_bugs_on_qe,
            'push_targets': [
                str(target['name'])
                for target in self.relationships['push_targets']
            ],
            'state_machine_rule_set': rule_set,
            'product_versions': [
                product_version.render()
                for product_version in self.product_versions()
            ],
        }

    def releases(self):
        """Get the list of product releases for this Product

        :returns: a (possibly-empty) list of Release objects.
        """
        url = '/api/v1/releases?filter[product_id]=%s' % self.id
        result = self._get(url)['data']
        releases = []

        for release in result:
            release_name = release['attributes']['name']
            releases.append(errata_tool.Release(
                name=release_name, data=release))
        return releases

    def __getattr__(self, name):
        if self.data is None:
            self.refresh()
        return self.data.get(name) or self.data['attributes'][name]

    def __repr__(self):
        return 'Product(%s)' % self.name

    def __str__(self):
        return self.name
