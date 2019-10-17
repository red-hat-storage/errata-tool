import pytest
import requests


class TestRemoveBuilds(object):

    def test_builds_url(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        advisory.removeBuilds(['ceph-12.2.5-42.el7cp'])
        assert mock_post.response.url == 'https://errata.devel.redhat.com/api/v1/erratum/33840/remove_build'  # NOQA: E501

    def test_builds_flag_set(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        advisory.removeBuilds(['ceph-12.2.5-42.el7cp'])
        assert advisory._buildschanged is True

    def test_builds_data(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        advisory.removeBuilds(['ceph-12.2.5-42.el7cp'])
        expected = {
            "nvr": "ceph-12.2.5-42.el7cp",
        }
        assert mock_post.kwargs['data'] == expected

    def test_builds_name(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        advisory.removeBuilds('ceph-12.2.5-42.el7cp')
        expected = {
            "nvr": "ceph-12.2.5-42.el7cp",
        }
        assert mock_post.kwargs['data'] == expected

    def test_builds_tuple(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        advisory.removeBuilds(('ceph-12.2.5-42.el7cp'))
        expected = {
            "nvr": "ceph-12.2.5-42.el7cp",
        }
        assert mock_post.kwargs['data'] == expected

    def test_builds_none(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        with pytest.raises(IndexError):
            advisory.removeBuilds(None)
        assert advisory._buildschanged is False

    def test_builds_empty_string(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        with pytest.raises(IndexError):
            advisory.removeBuilds('')
        assert advisory._buildschanged is False

    def test_builds_whitespace_string(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        with pytest.raises(IndexError):
            advisory.removeBuilds(' ')
        assert advisory._buildschanged is False

    def test_builds_empty_set(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        with pytest.raises(IndexError):
            advisory.removeBuilds(set())
        assert advisory._buildschanged is False

    def test_builds_empty_list(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        with pytest.raises(IndexError):
            advisory.removeBuilds([])
        assert advisory._buildschanged is False

    def test_builds_empty_tuple(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        with pytest.raises(IndexError):
            advisory.removeBuilds(())
        assert advisory._buildschanged is False

    def test_builds_dict(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        with pytest.raises(IndexError):
            advisory.removeBuilds({'foo': 'bar'})
        assert advisory._buildschanged is False
