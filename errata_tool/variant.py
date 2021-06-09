from errata_tool import ErrataConnector


class Variant(ErrataConnector):
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
