import sys
import pytest
from errata_tool.cli import main


class FakeErratum(object):

    errata_state = 'SHIPPED_LIVE'

    def __init__(self, **kwargs):
        pass

    def commit(self):
        pass

    def push(self, **kwargs):
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


def test_push_missing_name(monkeypatch):
    argv = ['errata-tool', 'advisory', 'push']
    monkeypatch.setattr(sys, 'argv', argv)
    with pytest.raises(SystemExit):
        main.main()


def test_push(monkeypatch):
    argv = ['errata-tool', 'advisory', 'push', '12345']
    monkeypatch.setattr(sys, 'argv', argv)
    monkeypatch.setattr('errata_tool.cli.advisory.Erratum', FakeErratum)
    main.main()


def test_push_wait_for_state(monkeypatch):
    argv = ['errata-tool', 'advisory', 'push',
            '--target', 'live',
            '--wait-for-state', 'SHIPPED_LIVE',
            '12345']
    monkeypatch.setattr(sys, 'argv', argv)
    monkeypatch.setattr('errata_tool.cli.advisory.Erratum', FakeErratum)
    main.main()


def test_push_when_ready(monkeypatch):
    argv = ['errata-tool', 'advisory', 'push',
            '--target', 'live',
            '--push-when-ready',
            '12345']
    monkeypatch.setattr(sys, 'argv', argv)
    monkeypatch.setattr('errata_tool.cli.advisory.Erratum', FakeErratum)
    main.main()


def test_wait_and_push_when_ready(monkeypatch):
    argv = ['errata-tool', 'advisory', 'push',
            '--target', 'live',
            '--target', 'live',
            '--wait-for-state', 'SHIPPED_LIVE',
            '--push-when-ready',
            '12345']
    monkeypatch.setattr(sys, 'argv', argv)
    monkeypatch.setattr('errata_tool.cli.advisory.Erratum', FakeErratum)
    main.main()


def test_push_when_ready_spurious_argument(monkeypatch):
    argv = ['errata-tool', 'advisory', 'push',
            '--target', 'live',
            '--push-when-ready', 'PUSH_READY',
            '12345']
    monkeypatch.setattr(sys, 'argv', argv)
    monkeypatch.setattr('errata_tool.cli.advisory.Erratum', FakeErratum)
    with pytest.raises(SystemExit):
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
