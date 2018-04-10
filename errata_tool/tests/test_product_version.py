def test_id(product_version):
    assert product_version.id == 665


def test_name(product_version):
    assert product_version.name == 'RHEL-7-CEPH-3'


def test_description(product_version):
    expected = 'Red Hat Ceph Storage 3 for Red Hat Enterprise Linux 7'
    assert product_version.description == expected
