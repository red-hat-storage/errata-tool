import requests
import pytest
from errata_tool import ErrataException


class TestAddBuilds(object):

    def test_add_builds_url(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        advisory.addBuilds(['ceph-1000-1.el7cp'], release='RHEL-7-RHCEPH-3.1')
        assert mock_post.response.url == 'https://errata.devel.redhat.com/api/v1/erratum/33840/add_builds'  # NOQA: E501

    def test_builds_data(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        advisory.addBuilds(['ceph-1000-1.el7cp'], release='RHEL-7-RHCEPH-3.1')
        expected = {
            "product_version": "RHEL-7-RHCEPH-3.1",
            "build": "ceph-1000-1.el7cp",
        }
        assert mock_post.kwargs['json'] == [expected]

    def test_builds_no_release(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        advisory.addBuilds(['ceph-1000-1.el7cp'])
        expected = {
            "product_version": "RHEL-7-RHCEPH-3.1",
            "build": "ceph-1000-1.el7cp",
        }
        assert mock_post.kwargs['json'] == [expected]

    def test_builds_empty_no_release(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        advisory.errata_builds = {}
        with pytest.raises(ErrataException,
                           message='Need to specify a release'):
            advisory.addBuilds(['ceph-1000-1.el7cp'])

    def test_builds_release_none(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        advisory.addBuilds(['ceph-1000-1.el7cp'], release=None)
        expected = {
            "product_version": "RHEL-7-RHCEPH-3.1",
            "build": "ceph-1000-1.el7cp",
        }
        assert mock_post.kwargs['json'] == [expected]

    def test_builds_new_advisory(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        advisory._new = True
        with pytest.raises(ErrataException,
                           message='Cannot add builds to unfiled erratum'):
            advisory.addBuilds(['ceph-1000-1.el7cp'])

    def test_2_builds_data(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        advisory.addBuilds(['ceph-1000-1.el7cp', 'foo-1.2.3-11.el7cp'])
        expected = [
            {
                "product_version": "RHEL-7-RHCEPH-3.1",
                "build": "ceph-1000-1.el7cp",
            },
            {
                "product_version": "RHEL-7-RHCEPH-3.1",
                "build": "foo-1.2.3-11.el7cp",
            }
        ]
        assert mock_post.kwargs['json'] == expected
