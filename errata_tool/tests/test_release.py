from datetime import date
import requests
from errata_tool.release import Release


class TestGet(object):
    def test_id(self, release):
        assert release.id == 783

    def test_name(self, release):
        assert release.name == 'rhceph-3.0'

    def test_description(self, release):
        assert release.description == 'Red Hat Ceph Storage 3.0'

    def test_type(self, release):
        assert release.type == 'QuarterlyUpdate'

    def test_is_active(self, release):
        assert release.is_active is True

    def test_enabled(self, release):
        assert release.enabled is True

    def blocker_flags(self, release):
        expected = ['ceph-3.0', 'pm_ack', 'devel_ack', 'qa_ack']
        assert release.blocker_flags == expected

    def test_is_pdc(self, release):
        assert release.is_pdc is True

    def test_url(self, release):
        expected = 'https://errata.devel.redhat.com/release/show/783'
        assert release.url == expected

    def test_edit_url(self, release):
        expected = 'https://errata.devel.redhat.com/release/edit/783'
        assert release.edit_url == expected


class TestCreate(object):
    # Note: we must be able to "GET" this release from a fixture file
    #       because we call GET at the end of Release.create().
    create_kwargs = dict(
        name='rhceph-3.0',
        product='RHCEPH',
        type='QuarterlyUpdate',
        program_manager='anharris',
        blocker_flags='ceph-3.0',
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
            'release[blocker_flags]': 'ceph-3.0',
            'release[description]': 'Red Hat Ceph Storage 3.0',
            'release[enable_batching]': 0,
            'release[enabled]': 1,
            'release[is_deferred]': 0,
            'release[is_pdc]': 1,
            'release[name]': 'rhceph-3.0',
            'release[product_id]': 104,
            'release[program_manager_id]': 3003046,
            'release[ship_date]': ship_date,
            'release[type]': 'QuarterlyUpdate',
        }
        assert mock_post.kwargs['data'] == expected
