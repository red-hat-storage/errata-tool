from errata_tool import ErrataConnector


class JiraIssue(ErrataConnector):
    def __init__(self, id):
        """Find jira issue information and advisories where the jira issue
        is attached.
        :param id: jira issue id
        """
        self.id = id
        self._all_advisory_ids = []
        self._fetch()

    def _fetch(self):
        """Fetch jira issue data from Errata Tool API and store them to
        properties"""

        self.url = self._url + '/jira_issues/%s/advisories.json' % self.id
        self._data = self._get(self.url)

        for advisory in self._data:
            self._all_advisory_ids.append(advisory['id'])

    @property
    def all_advisory_ids(self):
        """List of all Advisories id where the jira issue is attached
        :return: list of int objects (Advisory ids)
        """
        return self._all_advisory_ids

    def __getattr__(self):
        return self._data

    def __repr__(self):
        return 'Jira Issue (%s)' % self.id
