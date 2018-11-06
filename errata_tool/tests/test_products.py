from errata_tool.products import ProductList


class TestProductList(object):

    def test_instance(self, productlist):
        assert isinstance(productlist, ProductList)

    def test_export_name(self, productlist):
        result = productlist.export()
        assert result['name'] == 'errata_tool_products'

    def test_export_prodinfo_version(self, productlist):
        result = productlist.export()
        assert result['prodinfo_version'] == 3

    def test_export_products(self, productlist):
        result = productlist.export()
        osp = result['products'][78]
        assert osp == \
            {'id': 78,
             'name': u'Red Hat Enterprise Linux OpenStack Platform',
             'releases': {},
             'short_name': 'RHOS',
             'versions': {624: u'RHEL-7-OS-11', 625: u'RHEL-7-OS-11-OPTOOLS'}}
        ceph = result['products'][104]
        assert ceph == \
            {'id': 104,
             'name': u'Red Hat Ceph Storage',
             'releases': {},
             'short_name': u'RHCEPH',
             'versions': {803: u'RHEL-7-RHCEPH-2.5'}}

    def test_export_product_ids(self, productlist):
        result = productlist.export()
        assert result['product_ids'] == {'RHCEPH': 104, 'RHOS': 78}

    def test_export_releases(self, productlist):
        result = productlist.export()
        releases = result['releases']
        assert releases[654] == \
            {'async': True,
             'brew_tags': {},
             'bz_flags': [u'ceph-2.y'],
             'description': u'Red Hat Ceph Storage 2.1 updates',
             'id': 654,
             'enabled': True,
             'name': u'ceph-2.1-updates',
             'products': {},
             'versions': {509: u'RHEL-7-CEPH-2'}}
        assert releases[655] == \
            {'async': False,
             'brew_tags': {},
             'bz_flags': [u'ceph-2.y'],
             'description': u'Red Hat Ceph Storage 2.2',
             'id': 655,
             'enabled': True,
             'name': u'ceph-2.2',
             'products': {},
             'versions': {509: u'RHEL-7-CEPH-2'}}

    def test_export_versions(self, productlist):
        result = productlist.export()
        v = result['versions']
        assert v[803] == \
            {'brew_tag': u'ceph-2-rhel-7-candidate',
             'description': u'Red Hat Ceph Storage 2.5 for Red Hat '
                            'Enterprise Linux 7',
             'id': 803,
             'enabled': True,
             'name': u'RHEL-7-RHCEPH-2.5',
             'products': {104: u'Red Hat Ceph Storage'},
             'releases': {}}
