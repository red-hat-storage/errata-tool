import sys
import pytest
from errata_tool.cli import main


class FakeErratum(object):
    def __init__(self, **kwargs):
        pass

    def commit(self):
        pass


def test_short_help(monkeypatch):
    argv = ['errata-tool', 'advisory', '-h']
    monkeypatch.setattr(sys, 'argv', argv)
    with pytest.raises(SystemExit):
        main.main()


def test_help(monkeypatch):
    argv = ['errata-tool', 'advisory', '--help']
    monkeypatch.setattr(sys, 'argv', argv)
    with pytest.raises(SystemExit):
        main.main()


def test_get_missing_name(monkeypatch):
    argv = ['errata-tool', 'advisory', 'get']
    monkeypatch.setattr(sys, 'argv', argv)
    with pytest.raises(SystemExit):
        main.main()


def test_get(monkeypatch):
    argv = ['errata-tool', 'advisory', 'get', '12345']
    monkeypatch.setattr(sys, 'argv', argv)
    monkeypatch.setattr('errata_tool.cli.advisory.Erratum', FakeErratum)
    main.main()


def test_create_missing_args(monkeypatch):
    argv = ['errata-tool', 'advisory', 'create']
    monkeypatch.setattr(sys, 'argv', argv)
    with pytest.raises(SystemExit):
        main.main()


def test_create(monkeypatch):
    monkeypatch.setattr('errata_tool.cli.advisory.Erratum', FakeErratum)
    argv = ['errata-tool', 'advisory', 'create',
            '--product', 'RHCEPH',
            '--release', 'rhceph-2.1',
            '--synopsis', 'Red Hat Product 2.1 bug fix update',
            '--topic', 'An update for Red Hat Product 2.1 is now available.',
            '--description', 'This update contains the following fixes ...',
            '--solution', 'Before applying this update...',
            '--qe-email', 'someone@redhat.com',
            '--qe-group', 'RHC (Ceph) QE',
            '--owner-email', 'kdreyer@redhat.com',
            '--manager-email', 'ohno@redhat.com']
    monkeypatch.setattr(sys, 'argv', argv)
    main.main()
