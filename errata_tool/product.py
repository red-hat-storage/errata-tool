from errata_tool import ErrataConnector


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
