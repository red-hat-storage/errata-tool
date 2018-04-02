import sys
import pytest
from errata_tool.cli import main
import errata_tool.cli.release
from errata_tool.connector import ErrataConnector


class CallRecorder(object):
    def __call__(self, *args):
        self.args = args


def test_short_help(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['errata-tool', '-h'])
    with pytest.raises(SystemExit):
        main.main()


def test_help(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['errata-tool', '--help'])
    with pytest.raises(SystemExit):
        main.main()


def test_prod_connector(monkeypatch):
    argv = ['errata-tool', 'release', 'get', 'rhceph-2.4']
    monkeypatch.setattr(sys, 'argv', argv)
    monkeypatch.setattr(errata_tool.cli.release, 'get', lambda x: None)
    main.main()
    expected = 'https://errata.devel.redhat.com'
    assert ErrataConnector._url == expected


def test_staging_connector(monkeypatch):
    argv = ['errata-tool', '--stage', 'release', 'get', 'rhceph-2.4']
    monkeypatch.setattr(sys, 'argv', argv)
    monkeypatch.setattr(errata_tool.cli.release, 'get', lambda x: None)
    main.main()
    expected = 'https://errata.stage.engineering.redhat.com'
    assert ErrataConnector._url == expected


def test_dispatch(monkeypatch):
    argv = ['errata-tool', 'release', 'get', 'rhceph-2.4']
    monkeypatch.setattr(sys, 'argv', argv)
    recorder = CallRecorder()
    monkeypatch.setattr(errata_tool.cli.release, 'get', recorder)
    main.main()
    assert recorder.args
