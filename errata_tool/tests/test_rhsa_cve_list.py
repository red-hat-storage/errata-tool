class TestRhsaCveNames(object):

    def test_cve_names(self, monkeypatch, mock_post, mock_put, rhsa):
        """
        Verify that we have CVE names in our advisory (not None)
        """
        expected = 'CVE-2016-9579'
        assert rhsa.cve_names == expected
