import requests


class TestAddCC(object):

    def test_add_cc_url(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        advisory.addCC('kdreyer@redhat.com')
        assert mock_post.response.url == 'https://errata.devel.redhat.com/carbon_copies/add_to_cc_list'  # NOQA: E501

    def test_add_cc_data(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        advisory.addCC('kdreyer@redhat.com')
        expected = {'id': 33840, 'email': 'kdreyer@redhat.com'}
        assert mock_post.kwargs['data'] == expected
