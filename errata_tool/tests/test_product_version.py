def test_id(product_version):
    assert product_version.id == 783


def test_name(product_version):
    assert product_version.name == 'RHEL-7-RHCEPH-3.1'


def test_description(product_version):
    expected = 'Red Hat Ceph Storage 3.1'
    assert product_version.description == expected
