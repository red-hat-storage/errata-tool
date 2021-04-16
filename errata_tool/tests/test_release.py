from datetime import date
import requests
from errata_tool.release import Release


class TestGet(object):
    def test_id(self, release):
        assert release.id == 860

    def test_name(self, release):
        assert release.name == 'rhceph-3.1'

    def test_description(self, release):
        assert release.description == 'Red Hat Ceph Storage 3.1'

    def test_type(self, release):
        assert release.type == 'QuarterlyUpdate'

    def test_is_active(self, release):
        assert release.is_active is True

    def test_enabled(self, release):
        assert release.enabled is True

    def test_blocker_flags(self, release):
        expected = ['ceph-3.y', 'devel_ack', 'qa_ack', 'pm_ack']
        assert release.blocker_flags == expected

    def test_product_versions(self, release):
        expected = [{'id': 783, 'name': 'RHEL-7-RHCEPH-3.1'}]
        assert release.product_versions == expected

    def test_url(self, release):
        expected = 'https://errata.devel.redhat.com/release/show/860'
        assert release.url == expected

    def test_edit_url(self, release):
        expected = 'https://errata.devel.redhat.com/release/edit/860'
        assert release.edit_url == expected


class TestAdvisories(object):
    def test_advisories(self, release, monkeypatch, mock_get):
        monkeypatch.setattr(requests, 'get', mock_get)
        result = release.advisories()
        # Validate URL
        expected_url = 'https://errata.devel.redhat.com/release/860/advisories.json'  # NOQA: E501
        assert mock_get.response.url == expected_url
        # Validate return data
        expected = [
            {"id": 33840,
             "advisory_name": "RHBA-2018:2819",
             "product": "Red Hat Ceph Storage",
             "release": "rhceph-3.1",
             "synopsis": "Red Hat Ceph Storage 3.1 Bug Fix update",
             "release_date": None,
             "qe_owner": "hnallurv@redhat.com",
             "qe_group": "RHC (Ceph) QE",
             "status": "SHIPPED_LIVE",
             "status_time": "September 26, 2018 18:17"},
            {"id": 36762,
             "advisory_name": "RHSA-2018:2838",
             "product": "Red Hat Ceph Storage",
             "release": "rhceph-3.1",
             "synopsis": "Critical: ceph-iscsi-cli security update",
             "release_date": None,
             "qe_owner": "hnallurv@redhat.com",
             "qe_group": "RHC (Ceph) QE",
             "status": "SHIPPED_LIVE",
             "status_time": "October 01, 2018 15:13"}]
        assert result == expected


class TestCreate(object):
    # Note: we must be able to "GET" this release from a fixture file
    #       because we call GET at the end of Release.create().
    create_kwargs = dict(
        name='rhceph-3.1',
        product='RHCEPH',
        product_versions=['RHEL-7-RHCEPH-3.1'],
        type='QuarterlyUpdate',
        program_manager='anharris',
        blocker_flags='ceph-3.y',
        default_brew_tag='ceph-3.1-rhel-7-candidate',
    )

    def test_create_url(self, monkeypatch, mock_get, mock_post):
        monkeypatch.setattr(requests, 'get', mock_get)
        monkeypatch.setattr(requests, 'post', mock_post)
        Release.create(**self.create_kwargs)
        expected = 'https://errata.devel.redhat.com/release/create'
        assert mock_post.response.url == expected

    def test_create_data(self, monkeypatch, mock_get, mock_post):
        monkeypatch.setattr(requests, 'get', mock_get)
        monkeypatch.setattr(requests, 'post', mock_post)
        Release.create(**self.create_kwargs)
        today = date.today()
        ship_date = today.strftime("%Y-%b-%d")
        expected = {
            'type': 'QuarterlyUpdate',
            'release[allow_blocker]': 0,
            'release[allow_exception]': 0,
            'release[allow_pkg_dupes]': 1,
            'release[allow_shadow]': 0,
            'release[blocker_flags]': 'ceph-3.y',
            'release[description]': 'Red Hat Ceph Storage 3.1',
            'release[default_brew_tag]': 'ceph-3.1-rhel-7-candidate',
            'release[enable_batching]': 0,
            'release[enabled]': 1,
            'release[is_deferred]': 0,
            'release[name]': 'rhceph-3.1',
            'release[product_id]': 104,
            'release[program_manager_id]': 3003046,
            'release[product_version_ids][]': set([783]),
            'release[ship_date]': ship_date,
            'release[type]': 'QuarterlyUpdate',
        }
        assert mock_post.kwargs['data'] == expected


class TestSpecialCharacters(object):
    expected_url = 'https://errata.devel.redhat.com/api/v1/releases'

    def test_plus(self, monkeypatch, mock_get):
        monkeypatch.setattr(requests, 'get', mock_get)
        release = Release(name='RHEL-8.4.0.Z.MAIN+EUS')
        assert release.name == 'RHEL-8.4.0.Z.MAIN+EUS'
        assert mock_get.response.url == self.expected_url
        assert mock_get.kwargs['params']['filter[name]'] == \
            'RHEL-8.4.0.Z.MAIN+EUS'

    def test_plus_encoded(self, monkeypatch, mock_get, recwarn):
        monkeypatch.setattr(requests, 'get', mock_get)
        release = Release(name='RHEL-8.4.0.Z.MAIN%2BEUS')
        assert release.name == 'RHEL-8.4.0.Z.MAIN+EUS'
        assert mock_get.response.url == self.expected_url
        assert mock_get.kwargs['params']['filter[name]'] == \
            'RHEL-8.4.0.Z.MAIN+EUS'
        assert len(recwarn.list) == 1
        assert recwarn.pop(DeprecationWarning)
