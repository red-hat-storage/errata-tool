from errata_tool import ErrataConnector


class TestTextOnlyRepos(object):

    def test_get_url(self, monkeypatch, mock_get, advisory):
        monkeypatch.setattr(ErrataConnector.session, 'get', mock_get)
        advisory.textOnlyRepos()
        assert mock_get.response.url == 'https://errata.devel.redhat.com/api/v1/erratum/33840/text_only_repos'  # NOQA: E501

    def test_enable(self, monkeypatch, mock_put, advisory):
        monkeypatch.setattr(ErrataConnector.session, 'put', mock_put)
        repo = 'rhel-7-server-rhceph-3-mon-rpms__x86_64'
        advisory.textOnlyRepos(enable=[repo])
        expected = [{'enabled': True, 'repo': repo}]
        assert mock_put.kwargs['json'] == expected

    def test_disable(self, monkeypatch, mock_put, advisory):
        monkeypatch.setattr(ErrataConnector.session, 'put', mock_put)
        repo = 'rhel-7-server-rhceph-3-mon-rpms__x86_64'
        advisory.textOnlyRepos(disable=[repo])
        expected = [{'enabled': False, 'repo': repo}]
        assert mock_put.kwargs['json'] == expected
