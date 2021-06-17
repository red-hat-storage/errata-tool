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

    def __getattr__(self, name):
        if self.data is None:
            self.refresh()
        return self.data.get(name) or self.data['attributes'][name]

    def __repr__(self):
        return 'Product(%s)' % self.name

    def __str__(self):
        return self.name
