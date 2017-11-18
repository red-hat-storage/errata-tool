import json
import os
from errata_tool import ErrataConnector, Erratum
from errata_tool.products import ProductList
from errata_tool.product import Product
from errata_tool.release import Release
import requests
import pytest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(TESTS_DIR, 'fixtures')


class MockResponse(object):
    status_code = 200
    encoding = 'utf-8'
    headers = {'content-type': 'application/json; charset=utf-8'}

    def raise_for_status(self):
        pass

    @property
    def _fixture(self):
        """ Return path to our static fixture file. """
        return self.url.replace('https://errata.devel.redhat.com/',
                                os.path.join(FIXTURES_DIR,
                                             'errata.devel.redhat.com/'))

    def json(self):
        try:
            with open(self._fixture) as fp:
                return json.load(fp)
        except IOError:
            print('Try ./new-fixture.sh %s' % self.url)
            raise

    @property
    def text(self):
        """ Return contents of our static fixture file. """
        try:
            with open(self._fixture) as fp:
                return fp.read()
        except IOError:
            print('Try ./new-fixture.sh %s' % self.url)
            raise


class RequestRecorder(object):
    """ Record args to requests.get() or requests.post() """
    def __call__(self, url, **kwargs):
        """ mocking requests.get() or requests.post() """
        self.response = MockResponse()
        self.response.url = url
        self.kwargs = kwargs
        return self.response


@pytest.fixture
def mock_get():
    return RequestRecorder()


@pytest.fixture
def mock_post():
    return RequestRecorder()


@pytest.fixture
def mock_put():
    return RequestRecorder()


@pytest.fixture
def advisory(monkeypatch, mock_get):
    monkeypatch.delattr('requests.sessions.Session.request')
    monkeypatch.setattr(ErrataConnector, '_auth', None)
    monkeypatch.setattr(requests, 'get', mock_get)
    return Erratum(errata_id=26175)


@pytest.fixture
def rhsa(monkeypatch, mock_get):
    """ Like the advisory() fixture above, but an RHSA. """
    monkeypatch.delattr('requests.sessions.Session.request')
    monkeypatch.setattr(ErrataConnector, '_auth', None)
    monkeypatch.setattr(requests, 'get', mock_get)
    return Erratum(errata_id=25856)


@pytest.fixture
def productlist(monkeypatch, mock_get):
    monkeypatch.delattr('requests.sessions.Session.request')
    monkeypatch.setattr(ErrataConnector, '_auth', None)
    monkeypatch.setattr(requests, 'get', mock_get)
    return ProductList()


@pytest.fixture
def product(monkeypatch, mock_get):
    monkeypatch.delattr('requests.sessions.Session.request')
    monkeypatch.setattr(ErrataConnector, '_auth', None)
    monkeypatch.setattr(requests, 'get', mock_get)
    return Product('RHCEPH')


@pytest.fixture
def release(monkeypatch, mock_get):
    monkeypatch.delattr('requests.sessions.Session.request')
    monkeypatch.setattr(ErrataConnector, '_auth', None)
    monkeypatch.setattr(requests, 'get', mock_get)
    return Release(name='rhceph-3.0')
