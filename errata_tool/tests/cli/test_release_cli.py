import sys
import pytest
from errata_tool.cli import main
from errata_tool.release import NoReleaseFoundError


class FakeRelease(object):
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.description = 'Foo description'
        self.url = 'https://errata.devel.redhat.com/myrelease'
        self.edit_url = 'https://errata.devel.redhat.com/myrelease/edit'


class FakeMissingRelease(object):
    def __init__(self, **kwargs):
        raise NoReleaseFoundError

    @classmethod
    def create(cls, **kwargs):
        name = kwargs['name']
        return FakeRelease(name=name)


def test_short_help(monkeypatch):
    argv = ['errata-tool', 'release', '-h']
    monkeypatch.setattr(sys, 'argv', argv)
    with pytest.raises(SystemExit):
        main.main()


def test_help(monkeypatch):
    argv = ['errata-tool', 'release', '--help']
    monkeypatch.setattr(sys, 'argv', argv)
    with pytest.raises(SystemExit):
        main.main()


def test_get_missing_name(monkeypatch):
    argv = ['errata-tool', 'release', 'get']
    monkeypatch.setattr(sys, 'argv', argv)
    with pytest.raises(SystemExit):
        main.main()


def test_get(monkeypatch):
    monkeypatch.setattr('errata_tool.cli.release.Release', FakeRelease)
    argv = ['errata-tool', 'release', 'get', 'foo-3.0']
    monkeypatch.setattr(sys, 'argv', argv)
    main.main()


def test_get_missing(monkeypatch):
    monkeypatch.setattr('errata_tool.cli.release.Release', FakeMissingRelease)
    argv = ['errata-tool', 'release', 'get', 'missing-3.0']
    monkeypatch.setattr(sys, 'argv', argv)
    with pytest.raises(SystemExit):
        main.main()


def test_create_missing_args(monkeypatch):
    argv = ['errata-tool', 'release', 'create']
    monkeypatch.setattr(sys, 'argv', argv)
    with pytest.raises(SystemExit):
        main.main()


def test_create(monkeypatch):
    monkeypatch.setattr('errata_tool.cli.release.Release', FakeMissingRelease)
    argv = ['errata-tool', 'release', 'create',
            '--name', 'rhceph-2.4',
            '--product', 'RHCEPH',
            '--product_version', 'RHEL-7-CEPH-2',
            '--type', 'QuarterlyUpdate',
            '--program_manager', 'anharris',
            '--blocker_flags', 'ceph-2.y',
            '--default_brew_tag', 'ceph-3.0-rhel-7-candidate']
    monkeypatch.setattr(sys, 'argv', argv)
    main.main()
