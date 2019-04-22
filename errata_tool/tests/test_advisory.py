from errata_tool import Erratum


class TestAdvisory(object):

    def test_instance(self, advisory):
        assert isinstance(advisory, Erratum)

    def test_errata_state(self, advisory):
        assert advisory.errata_state == 'SHIPPED_LIVE'

    def test_url(self, advisory):
        expected = 'https://errata.devel.redhat.com/advisory/33840'
        assert advisory.url() == expected

    def test_synopsis(self, advisory):
        expected = 'Red Hat Ceph Storage 3.1 Bug Fix update'
        assert advisory.synopsis == expected

    def test_topic(self, advisory):
        expected = 'Red Hat Ceph Storage 3.1 is now available.'
        assert advisory.topic == expected

    def test_cve_names(self, advisory):
        expected = None
        assert advisory.cve_names == expected

    def test_description(self, advisory):
        expected = 'Red Hat Ceph Storage is a scalable'
        assert advisory.description.startswith(expected)

    def test_solution(self, advisory):
        expected = 'Before applying'
        assert advisory.solution.startswith(expected)

    def test_qe_email(self, advisory):
        assert advisory.qe_email == 'hnallurv@redhat.com'

    def test_qe_group(self, advisory):
        assert advisory.qe_group == 'RHC (Ceph) QE'

    def test_errata_type(self, advisory):
        assert advisory.errata_type == 'RHBA'

    def test_owner_email(self, advisory):
        assert advisory.package_owner_email == 'kdreyer@redhat.com'

    def test_reporter(self, advisory):
        assert advisory.reporter == 'kdreyer@redhat.com'

    def test_manager_email_is_none(self, advisory):
        # NOTE: the ET does not give this information when querying a
        # pre-existing advisory. We can only update it with POST/PUT, but we
        # cannot GET it. https://bugzilla.redhat.com/show_bug.cgi?id=1664884
        #  assert advisory.manager_email == 'gmeno@redhat.com'
        assert advisory.manager_email is None

    def test_manager_id(self, advisory):
        assert advisory.manager_id == 3001931

    def test_text_only(self, advisory):
        assert advisory.text_only is False

    def test_text_only_cpe(self, advisory):
        assert advisory.text_only_cpe is None

    def test_publish_date_override(self, advisory):
        assert advisory.publish_date_override == '2018-Sep-26'

    def test_publish_date(self, advisory):
        assert advisory.publish_date == '2018-Sep-26'

    def test_creation_date(self, advisory):
        assert advisory.creation_date == '2018-May-03'

    def test_ship_date(self, advisory):
        assert advisory.ship_date == '2018-Sep-26'

    def test_age(self, advisory):
        assert advisory.age == 146

    def test_errata_bugs(self, advisory):
        # Only sanity-check one for brevity.
        assert 1253486 in advisory.errata_bugs
        assert len(advisory.errata_bugs) == 138

    def test_errata_builds(self, advisory):
        expected = {'RHEL-7-RHCEPH-3.1': ['ceph-12.2.5-42.el7cp']}
        assert advisory.errata_builds == expected

    def test_missing_prod_listings(self, advisory):
        # (note, all builds have product listings for this advisory)
        assert advisory.missing_prod_listings == []

    def test_current_flags(self, advisory):
        assert advisory.current_flags == []

    def test_content_types(self, advisory):
        assert advisory.content_types == ['rpm']

    def test_batch_id(self, advisory):
        assert advisory.batch_id is None

    def test_get_erratum_data(self, advisory):
        result = advisory.get_erratum_data()
        assert isinstance(result, dict)
        # spot-check one element
        assert result['synopsis'] == 'Red Hat Ceph Storage 3.1 Bug Fix update'
