from errata_tool.bug import Bug


class TestGet(object):

    def test_instance(self, bug):
        assert isinstance(bug, Bug)

    def test_all_advisory_ids(self, bug):
        assert len(bug.all_advisory_ids) == 1
        assert bug.all_advisory_ids[0] == 44763

    def test_get(self, bug):
        assert bug.id == 1578936

    def test_url(self, bug):
        assert bug.url.endswith('/bugs/%d/advisories.json' % bug.id)
