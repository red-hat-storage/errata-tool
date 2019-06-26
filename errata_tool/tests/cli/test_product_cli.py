import pytest
import sys

from errata_tool.cli import main


class FakeProduct(object):
    def __init__(self, name):
        self.name = name
        self.description = 'Foo description'
        self.url = 'https://errata.devel.redhat.com/myrelease'


def test_short_help(monkeypatch):
    argv = ['errata-tool', 'product', '-h']
    monkeypatch.setattr(sys, 'argv', argv)
    with pytest.raises(SystemExit):
        main.main()


def test_help(monkeypatch):
    argv = ['errata-tool', 'product', '--help']
    monkeypatch.setattr(sys, 'argv', argv)
    with pytest.raises(SystemExit):
        main.main()


def test_get_missing_name(monkeypatch):
    argv = ['errata-tool', 'product', 'get']
    monkeypatch.setattr(sys, 'argv', argv)
    with pytest.raises(SystemExit):
        main.main()


def test_get(monkeypatch):
    argv = ['errata-tool', 'product', 'get', 'RHCEPH']
    monkeypatch.setattr(sys, 'argv', argv)
    monkeypatch.setattr('errata_tool.cli.product.Product', FakeProduct)
    main.main()
