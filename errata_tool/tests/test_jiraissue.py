from errata_tool.jira_issue import JiraIssue


class TestGet(object):

    def test_instance(self, jiraissue):
        assert isinstance(jiraissue, JiraIssue)

    def test_all_advisory_ids(self, jiraissue):
        assert len(jiraissue.all_advisory_ids) == 1
        assert jiraissue.all_advisory_ids[0] == 102176

    def test_get(self, jiraissue):
        assert jiraissue.id == "OCPBUGS-1590"

    def test_url(self, jiraissue):
        assert jiraissue.url.endswith(
            '/jira_issues/%s/advisories.json' % jiraissue.id)
