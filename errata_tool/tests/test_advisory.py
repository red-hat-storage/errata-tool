from errata_tool import Erratum


class TestAdvisory(object):

    def test_instance(self, advisory):
        assert isinstance(advisory, Erratum)

    def test_errata_state(self, advisory):
        assert advisory.errata_state == 'SHIPPED_LIVE'

    def test_url(self, advisory):
        expected = 'https://errata.devel.redhat.com/advisory/26175'
        assert advisory.url() == expected

    def test_synopsis(self, advisory):
        expected = 'Red Hat Ceph Storage 2.2 bug fix and enhancement update'
        assert advisory.synopsis == expected

    def test_topic(self, advisory):
        expected = 'Red Hat Ceph Storage 2.2 is now available.'
        assert advisory.topic == expected

    def test_description(self, advisory):
        expected = 'Red Hat Ceph Storage is a scalable'
        assert advisory.description.startswith(expected)

    def test_solution(self, advisory):
        expected = 'Before applying'
        assert advisory.solution.startswith(expected)

    def test_qe_email(self, advisory):
        assert advisory.qe_email == 'hnallurv@redhat.com'

    def test_qe_group(self, advisory):
        assert advisory.qe_group == 'Default'

    def test_errata_type(self, advisory):
        assert advisory.errata_type == 'RHBA'

    def test_owner_email(self, advisory):
        assert advisory.package_owner_email == 'kdreyer@redhat.com'

    def test_manager_email_is_none(self, advisory):
        # NOTE: the ET does not give this information when querying a
        # pre-existing advisory. We can only update it with POST/PUT, but we
        # cannot GET it.
        #  assert advisory.manager_email == 'gmeno@redhat.com'
        assert advisory.manager_email is None

    def test_text_only(self, advisory):
        assert advisory.text_only is False

    def test_publish_date_override(self, advisory):
        assert advisory.publish_date_override is None

    def test_creation_date(self, advisory):
        assert advisory.creation_date == '2017-Jan-10'

    def test_ship_date(self, advisory):
        assert advisory.ship_date == '2017-Mar-14'

    def test_age(self, advisory):
        assert advisory.age == 63

    def test_errata_bugs(self, advisory):
        # Only sanity-check one for brevity.
        assert 1425771 in advisory.errata_bugs
        assert len(advisory.errata_bugs) == 61

    def test_errata_builds(self, advisory):
        expected = {'RHEL-7-CEPH-2': ['ceph-10.2.5-37.el7cp']}
        assert advisory.errata_builds == expected

    def test_current_flags(self, advisory):
        assert advisory.current_flags == []
