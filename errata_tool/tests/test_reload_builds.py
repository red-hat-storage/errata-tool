import requests


class TestReloadBuilds(object):

    def test_reload_builds_url(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        advisory.reloadBuilds()
        assert mock_post.response.url == 'https://errata.devel.redhat.com/api/v1/erratum/33840/reload_builds'  # NOQA: E501

    def test_reload_builds_data(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        advisory.reloadBuilds()
        expected = {'no_rpm_listing_only': 0, 'no_current_files_only': 0}
        assert mock_post.kwargs['data'] == expected
