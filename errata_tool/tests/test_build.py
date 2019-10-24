from errata_tool.build import Build


class TestGet(object):

    def test_instance(self, build):
        assert isinstance(build, Build)

    def test_nvr(self, build):
        assert build.nvr == 'ceph-12.2.5-42.el7cp'

    def test_url(self, build):
        assert build.url.endswith('/api/v1/build/%s' % build.nvr)

    def test_signed_rpms(self, build):
        assert build.signed_rpms is True

    def test_all_erratas(self, build):
        assert len(build.all_errata) == 1
        assert build.all_errata[0].errata_id == 33840

    def test_released_errata(self, build):
        assert build.released_errata.errata_id == 33840

    def test_files(self, build):
        example_file = '/mnt/redhat/brewroot/packages/ceph/12.2.5/42.el7cp/' \
                       'data/signed/fd431d51/x86_64/librados2-12.2.5-42.' \
                       'el7cp.x86_64.rpm'
        assert len(build.files) == 71
        assert example_file in build.files

    def test_get(self, build):
        assert build.id == 760518

    def test_all_errata_ids(self, build):
        assert len(build.all_errata_ids) == 1
        assert build.all_errata_ids == [33840]

    def test_released_errata_id(self, build):
        assert build.released_errata_id == 33840
