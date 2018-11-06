import six
from errata_tool import ErrataConnector
from errata_tool.product_version import ProductVersion


class Product(ErrataConnector):
    def __init__(self, name):
        self.name = name
        self.data = None
        self.url = self._url + '/products/%s' % self.name

    def refresh(self):
        url = self.url + '.json'
        result = self._get(url)
        self.data = result['product']

    def __getattr__(self, name):
        if self.data is None:
            self.refresh()
        return self.data[name]

    def __repr__(self):
        return 'Product(%s)' % self.name

    def __str__(self):
        return self.name

    def productVersions(self, **kwargs):
        """
        Return a list of Product Versions for this product.

        You may optionally filter this list by passing additional keyword args.

        :param **kwargs: Optionally filter the list of product versions. For
                         example, pass the "enabled=1" keyword argument to
                         select product versions that are enabled and skip over
                         the ones that are disabled.
        :returns: list of ProductVersion objects
        """
        url = self._url + '/products/%s/product_versions.json' % self.name
        result = self._get(url)
        pvs = []
        for r in result:
            data = r['product_version']
            keep = True
            for key, value in six.iteritems(kwargs):
                if key in data and data[key] != value:
                    keep = False
                    break
            if keep:
                pvs.append(ProductVersion(data['id']))
        return pvs
