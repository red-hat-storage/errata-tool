import requests


class TestAddBuilds(object):

    def test_add_builds_url(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        advisory.addBuilds(['ceph-10.2.3-17.el7cp'], release='RHEL-7-CEPH-2')
        assert mock_post.response.url == 'https://errata.devel.redhat.com/api/v1/erratum/26175/add_builds'  # NOQA: E501

    def test_builds_data(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        advisory.addBuilds(['ceph-10.2.3-17.el7cp'], release='RHEL-7-CEPH-2')
        expected = {
            "product_version": "RHEL-7-CEPH-2",
            "build": "ceph-10.2.3-17.el7cp",
        }
        assert mock_post.kwargs['json'] == [expected]

    def test_builds_pdc_data(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        # Point at a PDC-based release fixture for this test:
        advisory.release_id = 783
        advisory.addBuilds(['ceph-12.2.1-1.el7cp'], release='ceph-3.0@rhel-7')
        expected = {
            "pdc_release": "ceph-3.0@rhel-7",
            "build": "ceph-12.2.1-1.el7cp",
        }
        assert mock_post.kwargs['json'] == [expected]
