import requests


class TestChangeDocsReviewer(object):

    def test_change_url(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        advisory.changeDocsReviewer('kdreyer@redhat.com')
        assert mock_post.response.url == 'https://errata.devel.redhat.com/api/v1/erratum/33840/change_docs_reviewer'  # NOQA: E501

    def test_change_data(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        advisory.changeDocsReviewer('kdreyer@redhat.com')
        assert mock_post.kwargs['data'] == {'login_name': 'kdreyer@redhat.com'}
