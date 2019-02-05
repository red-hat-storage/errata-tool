from errata_tool import ErrataConnector


class TestExternalTests(object):

    def test_external_tests_url(self, monkeypatch, mock_get, advisory):
        monkeypatch.setattr(ErrataConnector.session, 'get', mock_get)
        advisory.externalTests(test_type='rpmdiff')
        assert mock_get.response.url == 'https://errata.devel.redhat.com/api/v1/external_tests/?filter[active]=true&filter[errata_id]=33840&filter[test_type]=rpmdiff'  # NOQA: E501

    def test_external_tests_data(self, monkeypatch, mock_get, advisory):
        monkeypatch.setattr(ErrataConnector.session, 'get', mock_get)
        rpmdiff = advisory.externalTests(test_type='rpmdiff')
        assert len(rpmdiff) == 35
