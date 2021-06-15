import requests


class TestFilter(object):

    def test_filter_none(self, sample_connector):
        assert sample_connector.get_filter(None, None) is None

    def test_filter_sample(self, sample_connector):
        assert sample_connector.get_filter(
            '/api/v1/releases', 'filter', name='rhceph-3.1')

    def test_filter_sample_check_url(self, monkeypatch, mock_get,
                                     sample_connector):
        monkeypatch.setattr(requests, 'get', mock_get)
        assert sample_connector.get_filter(
            '/api/v1/releases', 'filter', name='rhceph-3.1')
        assert 'page' not in mock_get.response.url

    def test_filter_url_paginated_false(self, monkeypatch,
                                        mock_get, sample_connector):
        monkeypatch.setattr(requests, 'get', mock_get)
        assert sample_connector.get_filter(
            '/api/v1/releases', 'filter', name='rhceph-3.1', paginated=False)
        assert 'page' not in mock_get.response.url

    def test_filter_sample_check_url_paginated(self, monkeypatch, mock_get,
                                               sample_connector):
        monkeypatch.setattr(requests, 'get', mock_get)
        assert sample_connector.get_filter(
            '/api/v1/external_tests', 'filter', errata_id='33840',
            test_type='rpmdiff', active='true', paginated=True)
        assert 'page' in mock_get.response.url
