import requests


class TestComments(object):
    def test_comment_count(self, advisory):
        assert len(advisory.comments()) == 4

    def test_comment_keys(self, advisory):
        for comment in advisory.comments():
            assert set(comment.keys()) == {'type', 'id', 'attributes'}
            assert set(comment['attributes'].keys()) == \
                {'advisory_state', 'created_at', 'errata_id', 'text', 'who'}

    def test_comment_argument(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        advisory.addComment('test')
        expected = {'comment': 'test'}
        assert mock_post.kwargs['json'] == expected

    def test_comment_user(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        advisory.addComment('test')
        expected = {'user': {'id': 3002896, 'login_name': 'jdoe@redhat.com',
                             'realname': 'John Doe', 'preferences': {},
                             'user_organization_id': 142, 'enabled': 1,
                             'receives_mail': True, 'email_address': '',
                             'account_name': 'jdoe', 'type': 'Person'}}
        assert mock_post.response.json()['who'] == expected

    def test_comment_response(self, monkeypatch, mock_post, advisory):
        monkeypatch.setattr(requests, 'post', mock_post)
        comment = 'test'
        advisory.addComment(comment)
        expected = {'comment': comment, 'format': 'json',
                    'controller': 'api/v1/erratum', 'action': 'add_comment',
                    'id': '69356'}
        assert mock_post.response.json()['params'] == expected
