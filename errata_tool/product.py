from errata_tool import ErrataConnector


class Product(ErrataConnector):
    def __init__(self, name):
        self.name = name
        self.data = None
        self.url = self._url + '/products/%s' % self.name

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
