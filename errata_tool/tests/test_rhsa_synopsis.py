from errata_tool import ErrataConnector


class TestRhsaSynopsis(object):

    def test_synopsis(self, monkeypatch, mock_post, mock_put, rhsa):
        """
        Verify that we do not include the "Moderate: " prefix in our PUT data.
        """
        monkeypatch.setattr(ErrataConnector.session, 'post', mock_post)
        monkeypatch.setattr(ErrataConnector.session, 'put', mock_put)
        # Any typical advisory update would toggle this internal "_update"
        # attribute. Simulate that here:
        rhsa._update = True
        # Now save our "changes":
        rhsa.commit()
        expected = 'ceph-iscsi-cli security update'
        assert mock_put.kwargs['data']['advisory[synopsis]'] == expected
